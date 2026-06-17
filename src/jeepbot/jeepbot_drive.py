"""
JeepBot drive loop — dual VESC (motor+encoder steering, duty-cycle drive)
Integrates OAK-D Pro camera + Flask web server as in-process threads.

Drive modes (set via web UI or web_server.get_mode()):
  manual        — F710 joystick controls everything
  record        — joystick controls + tub data is recorded to disk
  auto_steering — AI steers, joystick controls throttle
  full_drive    — AI steers AND drives (full autonomous)
"""
from __future__ import annotations

import argparse
import math
import queue
import time
import threading
import serial
import sys

from serial.tools import list_ports

from pyvesc.protocol.interface import encode
from pyvesc.VESC.messages.setters import (
    Alive,
    SetCurrentBrake,
    SetDutyCycle,
    SetPosition,
)
from pygame_f710 import F710DirectInput
from pygame_radiomaster import RadioMasterInput
from web_server import JeepBotWebServer, JeepBotRearWebServer
from camera import start_camera_thread, start_rear_camera_thread, resolve_devices
# -----------------------------------------------------------------------
# Math helpers
# -----------------------------------------------------------------------

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def apply_deadzone(value: float, deadzone: float) -> float:
    if abs(value) <= deadzone:
        return 0.0
    sign = 1.0 if value > 0.0 else -1.0
    return sign * ((abs(value) - deadzone) / (1.0 - deadzone))


def shape_axis(value: float, expo: float) -> float:
    expo = clamp(expo, 0.0, 1.0)
    return ((1.0 - expo) * value) + (expo * math.copysign(value * value, value))


def wrap_degrees(value: float, wrap_deg: float) -> float:
    if wrap_deg <= 0:
        return value
    return value % wrap_deg


def shortest_wrapped_delta(start_deg: float, end_deg: float, wrap_deg: float) -> float:
    if wrap_deg <= 0:
        return end_deg - start_deg
    return ((end_deg - start_deg + (wrap_deg / 2.0)) % wrap_deg) - (wrap_deg / 2.0)


def endpoint_target_deg(
    stick: float,
    center_deg: float,
    left_deg: float,
    right_deg: float,
    wrap_deg: float,
) -> float:
    if stick < 0.0:
        delta = shortest_wrapped_delta(center_deg, left_deg, wrap_deg)
        target = center_deg + (-stick * delta)
    else:
        delta = shortest_wrapped_delta(center_deg, right_deg, wrap_deg)
        target = center_deg + (stick * delta)
    return wrap_degrees(target, wrap_deg)


def move_toward(current: float, target: float, max_step: float) -> float:
    error = target - current
    if abs(error) <= max_step:
        return target
    return current + (max_step if error > 0.0 else -max_step)


def move_angle_toward(
    current: float,
    target: float,
    max_step: float,
    wrap_deg: float,
    min_step: float,
) -> float:
    error = shortest_wrapped_delta(current, target, wrap_deg)
    if abs(error) <= max_step:
        return target
    step = max_step
    if min_step > 0.0:
        step = max(step, min(min_step, abs(error)))
    current += step if error > 0.0 else -step
    return wrap_degrees(current, wrap_deg)


# -----------------------------------------------------------------------
# Steering normalisation helpers (used for AI pilot output)
# -----------------------------------------------------------------------

def norm_to_deg(norm: float, config) -> float:
    """Convert [-1, +1] pilot output → steering degrees for VESC."""
    center = config.DEFAULT_STEERING_CENTER_DEG
    left   = config.DEFAULT_STEERING_LEFT_DEG
    right  = config.DEFAULT_STEERING_RIGHT_DEG
    norm   = clamp(norm, -1.0, 1.0)
    if norm <= 0.0:
        return center + (norm * (center - left))   # norm=-1 → left
    else:
        return center + (norm * (right - center))  # norm=+1 → right


# -----------------------------------------------------------------------
# Serial helpers
# -----------------------------------------------------------------------

def list_serial_ports() -> None:
    ports = list(list_ports.comports())
    if not ports:
        print("No serial ports found.")
        return
    for port in ports:
        print(f"{port.device}: {port.description}")


def open_serial(port: str, baudrate: int, label: str) -> serial.Serial:
    try:
        serial_port = serial.Serial(port, baudrate, timeout=0)
    except serial.SerialException as exc:
        raise SystemExit(
            f"Could not open {label} port {port}: {exc}\n"
            "Close VESC Tool or any other program using that serial port."
        ) from exc
    print(f"Opened {label} VESC serial port {port} at {baudrate} baud.")
    return serial_port


# -----------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------

def parse_args(config) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Control JeepBot with Logitech F710 and dual VESCs."
    )

    parser.add_argument("--list-ports",  action="store_true")
    parser.add_argument("--dry-run",     action="store_true")
    parser.add_argument("--baudrate",    type=int,   default=config.DEFAULT_BAUDRATE)
    parser.add_argument("--joystick-id", type=int,   default=-1)
    parser.add_argument("--rate-hz",     type=float, default=config.DEFAULT_RATE_HZ)
    parser.add_argument("--deadman-button", type=int, default=config.DEFAULT_DEADMAN_BUTTON)
    parser.add_argument("--no-deadman",  action="store_true")
    parser.add_argument("--deadzone",    type=float, default=config.DEFAULT_DEADZONE)
    parser.add_argument("--expo",        type=float, default=config.DEFAULT_EXPO)

    # Model path for autonomous modes
    parser.add_argument(
        "--model",
        default=config.DEFAULT_MODEL_PATH,
        help="Keras model for auto_steering / full_drive modes",
    )

    # Tub path for record mode
    parser.add_argument(
        "--tub",
        default=config.DEFAULT_TUB_PATH,
        help="Directory to save tub recordings",
    )

    # Steering
    parser.add_argument("--steering-port",         default=config.DEFAULT_STEERING_PORT)
    parser.add_argument("--steering-axis",         type=int,   default=config.DEFAULT_STEERING_AXIS)
    parser.add_argument("--steering-center-deg",   type=float, default=config.DEFAULT_STEERING_CENTER_DEG)
    parser.add_argument("--steering-left-deg",     type=float, default=config.DEFAULT_STEERING_LEFT_DEG)
    parser.add_argument("--steering-right-deg",    type=float, default=config.DEFAULT_STEERING_RIGHT_DEG)
    parser.add_argument("--steering-wrap-deg",     type=float, default=config.DEFAULT_STEERING_WRAP_DEG)
    parser.add_argument("--steering-ramp-deg-per-s", type=float, default=config.DEFAULT_STEERING_RAMP_DEG_PER_S)
    parser.add_argument("--steering-min-step-deg", type=float, default=config.DEFAULT_STEERING_MIN_STEP_DEG)
    parser.add_argument("--steering-smoothing",    type=float, default=config.DEFAULT_STEERING_SMOOTHING)
    parser.add_argument("--invert-steering",       action="store_true", default=config.DEFAULT_INVERT_STEERING)
    parser.add_argument("--disable-steering",      action="store_true")

    # Drive
    parser.add_argument("--drive-port",            default=config.DEFAULT_DRIVE_PORT)
    parser.add_argument("--drive-axis",            type=int,   default=config.DEFAULT_DRIVE_AXIS)
    parser.add_argument("--max-duty",              type=float, default=config.DEFAULT_MAX_DUTY)
    parser.add_argument("--drive-ramp-duty-per-s", type=float, default=config.DEFAULT_DRIVE_RAMP_DUTY_PER_S)
    parser.add_argument("--drive-smoothing",       type=float, default=config.DEFAULT_DRIVE_SMOOTHING)
    parser.add_argument("--drive-brake-current-a", type=float, default=config.DEFAULT_DRIVE_BRAKE_CURRENT_A)
    parser.add_argument("--invert-drive",          action="store_true", default=config.DEFAULT_INVERT_DRIVE)
    parser.add_argument("--disable-drive",         action="store_true")

    return parser.parse_args()


# -----------------------------------------------------------------------
# Latest-frame helper — non-blocking peek at the camera queue
# -----------------------------------------------------------------------

# Shared: camera thread puts BGR frames here (separate from the JPEG queue)
_bgr_frame_lock  = threading.Lock()
_latest_bgr      = None   # most recent raw BGR frame for AI inference
_depth_frame_lock = threading.Lock()
_latest_depth     = None  # most recent aligned depth frame in millimeters


def _bgr_frame_sidecar(jpeg_queue: queue.Queue) -> None:
    """
    Background thread that decodes JPEG bytes from the camera queue into
    BGR numpy arrays for the AI pilot.  Runs as a daemon.
    """
    import cv2, numpy as np

    global _latest_bgr
    while True:
        try:
            jpg_bytes = jpeg_queue.get(timeout=2.0)
        except queue.Empty:
            continue
        arr = np.frombuffer(jpg_bytes, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is not None:
            with _bgr_frame_lock:
                _latest_bgr = bgr


def get_latest_bgr():
    with _bgr_frame_lock:
        return _latest_bgr


def _depth_frame_sidecar(depth_queue: queue.Queue) -> None:
    global _latest_depth
    while True:
        try:
            depth = depth_queue.get(timeout=2.0)
        except queue.Empty:
            continue
        if depth is not None:
            with _depth_frame_lock:
                _latest_depth = depth


def get_latest_depth():
    with _depth_frame_lock:
        return _latest_depth


def _start_camera_web_stack(config):
    frame_queue = queue.Queue(maxsize=1)
    ai_queue    = queue.Queue(maxsize=1)
    rear_queue  = queue.Queue(maxsize=1)
    depth_queue = queue.Queue(maxsize=1)

    # Assign front/rear OAK-D (honors SWAP_CAMERAS and FRONT/REAR_CAMERA_MXID).
    front_info, rear_info = resolve_devices(config)

    depth_enabled = bool(getattr(config, "ENABLE_DEPTH_DISTANCE", False))
    front_enabled = bool(getattr(config, "ENABLE_FRONT_CAMERA", True))
    rear_enabled  = bool(getattr(config, "ENABLE_REAR_CAMERA", True))
    front_res = getattr(config, "FRONT_CAMERA_RESOLUTION", (1280, 720))
    rear_res  = getattr(config, "REAR_CAMERA_RESOLUTION", (1280, 720))

    # Rear is only "active" when enabled AND a second OAK-D is present.
    rear_active = rear_enabled and rear_info is not None

    if front_enabled:
        start_camera_thread(
            frame_queue,
            ai_queue,
            device_info=front_info,
            depth_queue=depth_queue,
            enable_depth=depth_enabled,
            resolution=front_res,
        )
    else:
        print("[camera] Front camera disabled (ENABLE_FRONT_CAMERA=False).")

    if rear_active:
        start_rear_camera_thread(rear_queue, device_info=rear_info, resolution=rear_res)
    elif not rear_enabled:
        print("[camera] Rear camera disabled (ENABLE_REAR_CAMERA=False).")
    else:
        print("[camera] No rear OAK-D found — rear server not started.")

    # BGR sidecar — decodes JPEG → numpy for AI pilot and YOLO.
    t = threading.Thread(
        target=_bgr_frame_sidecar,
        args=(ai_queue,),
        daemon=True,
        name="bgr-sidecar",
    )
    t.start()

    d = threading.Thread(
        target=_depth_frame_sidecar,
        args=(depth_queue,),
        daemon=True,
        name="depth-sidecar",
    )
    d.start()

    detector = None
    if getattr(config, "ENABLE_YOLO_DETECTION", False):
        try:
            from yolo_detector import YoloDetector

            detector = YoloDetector(
                get_frame=get_latest_bgr,
                get_depth=get_latest_depth if depth_enabled else None,
                model_path=getattr(config, "YOLO_MODEL_PATH", ""),
                imgsz=getattr(config, "YOLO_IMGSZ", 320),
                conf=getattr(config, "YOLO_CONFIDENCE", 0.25),
                interval_s=getattr(config, "YOLO_INTERVAL_S", 0.20),
                depth_min_mm=getattr(config, "DEPTH_MIN_MM", 150),
                depth_max_mm=getattr(config, "DEPTH_MAX_MM", 10000),
                depth_roi_scale=getattr(config, "DEPTH_ROI_SCALE", 0.35),
            )
            detector.start()
            print(f"[YOLO] Detection overlay enabled: {detector.model_path}")
        except Exception as exc:
            print(f"[YOLO] WARNING: Could not start detector: {exc}")

    web_server = JeepBotWebServer(
        config,
        frame_queue,
        rear_queue if rear_active else None,
        detector=detector,
    )
    web_server.start()

    if rear_active:
        JeepBotRearWebServer(config, rear_queue).start()

    return web_server, frame_queue, ai_queue, rear_queue


def _run_web_only(config, reason: str) -> int:
    if not config.ENABLE_WEB_SERVER:
        raise RuntimeError(reason)

    print(f"[web-only] {reason}")
    print("[web-only] Starting camera, web server, and YOLO only.")
    _start_camera_web_stack(config)
    print("[web-only] No joystick/VESC control is active. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopped.")

    return 0


# -----------------------------------------------------------------------
# Main drive loop
# -----------------------------------------------------------------------

def drive(config) -> int:
    args = parse_args(config)

    if args.list_ports:
        list_serial_ports()
        return 0

    # ------------------------------------------------------------------
    # Joystick FIRST — pygame must be fully initialised before any
    # other threads start. SDL is not thread-safe at init time and
    # OAK-D USB traffic can race with SDL startup causing event.pump()
    # to block forever when camera is running.
    # ------------------------------------------------------------------
    try:
        explicit_id = None if args.joystick_id < 0 else args.joystick_id
        controller_type = getattr(config, "CONTROLLER", "f710").lower()
        if controller_type == "radiomaster":
            joystick = RadioMasterInput(
                explicit_id,
                name_match=getattr(config, "CONTROLLER_DEVICE_NAME", "Arduino"),
            )
        else:
            joystick = F710DirectInput(explicit_id)
    except RuntimeError as exc:
        return _run_web_only(config, str(exc))

    print(f"Using joystick {joystick.joystick_id}: {joystick.name}")

    # ------------------------------------------------------------------
    # Camera + web server (in-process threads — NOT subprocess)
    # Started AFTER joystick/pygame is fully ready.
    # ------------------------------------------------------------------
    web_server   = None
    frame_queue  = None      # JPEG bytes → web stream
    ai_queue     = None      # JPEG bytes → AI frame decoder

    if config.ENABLE_WEB_SERVER:
        web_server, frame_queue, ai_queue, rear_queue = _start_camera_web_stack(config)
    # ------------------------------------------------------------------
    # Lazy-load AI pilot (only if model file exists)
    # ------------------------------------------------------------------
    pilot = None
    if args.model:
        from pathlib import Path
        if Path(args.model).exists():
            try:
                from jeep_model import load_pilot
                pilot = load_pilot(args.model)
                print(f"[AI] Pilot loaded from {args.model}")
            except Exception as exc:
                print(f"[AI] WARNING: Could not load pilot: {exc}")
        else:
            print(f"[AI] No model at '{args.model}' — auto modes will fall back to manual")

    # ------------------------------------------------------------------
    # Tub recorder (created fresh each run; only records when mode=record)
    # ------------------------------------------------------------------
    recorder = None
    if args.tub:
        try:
            from tub_recorder import TubRecorder
            recorder = TubRecorder(config, ai_queue or queue.Queue(), tub_root=args.tub)
        except Exception as exc:
            print(f"[TUB] WARNING: Could not create recorder: {exc}")

    # ------------------------------------------------------------------
    # Serial ports
    # ------------------------------------------------------------------
    steering_serial = None
    drive_serial    = None

    if not args.dry_run and not args.disable_steering:
        steering_serial = open_serial(args.steering_port, args.baudrate, "steering")

    if not args.dry_run and not args.disable_drive:
        drive_serial = open_serial(args.drive_port, args.baudrate, "drive")

    period         = 1.0 / max(args.rate_hz, 1.0)
    last_loop_time = time.time()
    last_print     = 0.0

    steering_cmd_deg = args.steering_center_deg
    drive_cmd_duty   = 0.0
    filtered_steering = 0.0
    filtered_drive    = 0.0

    print(f"Hold button {args.deadman_button} to enable commands.")
    print(f"Steering center={args.steering_center_deg}")
    print(f"Drive max duty={abs(args.max_duty):.3f}")
    print("Modes: manual | record | auto_steering | full_drive")

    try:
        while True:
            now = time.time()
            dt  = max(0.001, now - last_loop_time)
            last_loop_time = now

            state    = joystick.read()
            web_mode = web_server.get_mode() if web_server else "manual"

            max_axis = max(args.steering_axis, args.drive_axis)
            if max_axis >= len(state.axes):
                raise RuntimeError(f"Axis {max_axis} is not available.")

            # ---- Deadman safety ----
            deadman = args.no_deadman or state.pressed(args.deadman_button)

            # ====================================================
            # JOYSTICK INPUT  (always computed; used in manual/record
            #                  and as throttle override in auto_steering)
            # ====================================================

            raw_steering   = state.axes[args.steering_axis]
            steering_stick = shape_axis(
                apply_deadzone(raw_steering, args.deadzone), args.expo
            )
            if args.invert_steering:
                steering_stick *= -1.0

            s_smooth = clamp(args.steering_smoothing, 0.0, 0.95)
            filtered_steering = (
                s_smooth * filtered_steering + (1.0 - s_smooth) * steering_stick
            )

            joystick_steering_deg = endpoint_target_deg(
                stick=filtered_steering,
                center_deg=args.steering_center_deg,
                left_deg=args.steering_left_deg,
                right_deg=args.steering_right_deg,
                wrap_deg=args.steering_wrap_deg,
            )

            raw_drive   = state.axes[args.drive_axis]
            drive_stick = shape_axis(
                apply_deadzone(raw_drive, args.deadzone), args.expo
            )
            if args.invert_drive:
                drive_stick *= -1.0

            d_smooth = clamp(args.drive_smoothing, 0.0, 0.95)
            filtered_drive = (
                d_smooth * filtered_drive + (1.0 - d_smooth) * drive_stick
            )

            joystick_duty = clamp(
                filtered_drive * abs(args.max_duty),
                -abs(args.max_duty),
                abs(args.max_duty),
            )

            # ====================================================
            # MODE DISPATCH
            # ====================================================

            if web_mode in ("manual", "record") or pilot is None:
                # ---- Manual / Record ----
                steering_target_deg = joystick_steering_deg
                drive_target_duty   = joystick_duty

            elif web_mode == "auto_steering":
                # ---- AI steers, joystick throttles ----
                bgr = get_latest_bgr()
                if bgr is not None and pilot is not None:
                    s_norm, _ = pilot.predict(bgr)
                    steering_target_deg = norm_to_deg(s_norm, args)
                else:
                    steering_target_deg = args.steering_center_deg
                drive_target_duty = joystick_duty

            elif web_mode == "full_drive":
                # ---- Full autonomous ----
                bgr = get_latest_bgr()
                if bgr is not None and pilot is not None:
                    s_norm, d_norm = pilot.predict(bgr)
                    steering_target_deg = norm_to_deg(s_norm, args)
                    drive_target_duty   = clamp(
                        d_norm * abs(args.max_duty),
                        -abs(args.max_duty),
                        abs(args.max_duty),
                    )
                else:
                    steering_target_deg = args.steering_center_deg
                    drive_target_duty   = 0.0

            else:
                # Unknown mode — safe default
                steering_target_deg = args.steering_center_deg
                drive_target_duty   = 0.0

            # ====================================================
            # RAMP toward targets (same logic regardless of mode)
            # ====================================================

            if deadman:
                steering_cmd_deg = move_angle_toward(
                    current=steering_cmd_deg,
                    target=steering_target_deg,
                    max_step=abs(args.steering_ramp_deg_per_s) * dt,
                    wrap_deg=args.steering_wrap_deg,
                    min_step=max(args.steering_min_step_deg, 0.0),
                )
                drive_cmd_duty = move_toward(
                    current=drive_cmd_duty,
                    target=drive_target_duty,
                    max_step=abs(args.drive_ramp_duty_per_s) * dt,
                )
            else:
                # Deadman released — centre steering, brake to stop
                steering_cmd_deg = args.steering_center_deg
                drive_cmd_duty   = move_toward(
                    drive_cmd_duty, 0.0,
                    abs(args.drive_ramp_duty_per_s) * dt,
                )

            # ====================================================
            # SEND TO VESCs
            # ====================================================

            if steering_serial is not None and not args.disable_steering:
                steering_serial.write(encode(Alive()))
                steering_serial.write(encode(SetPosition(steering_cmd_deg)))

            if drive_serial is not None and not args.disable_drive:
                drive_serial.write(encode(Alive()))
                if abs(drive_cmd_duty) > 0.0001:
                    drive_serial.write(encode(SetDutyCycle(drive_cmd_duty)))
                elif args.drive_brake_current_a > 0.0:
                    drive_serial.write(encode(SetCurrentBrake(args.drive_brake_current_a)))
                else:
                    drive_serial.write(encode(SetDutyCycle(0.0)))

            # ====================================================
            # TUB RECORDING  (only in record mode + deadman held)
            # ====================================================

            if web_mode == "record" and deadman and recorder is not None:
                # Grab the latest JPEG from the ai_queue (non-blocking peek)
                latest_jpg = None
                if ai_queue is not None:
                    try:
                        latest_jpg = ai_queue.get_nowait()
                        # Put it back so the bgr-sidecar can still use it
                        try:
                            ai_queue.put_nowait(latest_jpg)
                        except queue.Full:
                            pass
                    except queue.Empty:
                        pass
                recorder.update(steering_cmd_deg, drive_cmd_duty, latest_jpg)

            # ====================================================
            # DEBUG PRINT
            # ====================================================

            if now - last_print > 0.2:
                deadman_label = "SEND" if deadman else "safe"
                rec_label = (
                    f" REC:{recorder.frame_count()}" if (
                        recorder and web_mode == "record" and deadman
                    ) else ""
                )
                print(
                    f"\r{deadman_label} [{web_mode}]{rec_label} "
                    f"steer={steering_cmd_deg:+.2f}° "
                    f"drive={drive_cmd_duty:+.3f}  ",
                    end="",
                    flush=True,
                )
                last_print = now

            time.sleep(period)

    except KeyboardInterrupt:
        print("\nStopped.")

    finally:
        # Close tub recorder (flushes background writer)
        if recorder is not None:
            recorder.close()

        # Return steering to centre
        if steering_serial is not None:
            steering_serial.write(encode(SetPosition(args.steering_center_deg)))
            steering_serial.close()

        # Stop drive motor
        if drive_serial is not None:
            drive_serial.write(encode(SetDutyCycle(0.0)))
            drive_serial.close()

        # Daemon threads (camera, flask, bgr-sidecar) die automatically.

    return 0

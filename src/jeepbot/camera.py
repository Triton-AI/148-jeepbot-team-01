"""
JeepBot Camera module — Dual OAK-D Pro edition

Camera capture threads, split out of web_server.py so the cameras and the
Flask web servers live in separate files. The web servers only consume the
JPEG queues these threads fill.

Enable/disable and resolution for each camera are controlled by global values
in myconfig.py:
    ENABLE_FRONT_CAMERA / ENABLE_REAR_CAMERA       (bool)
    FRONT_CAMERA_RESOLUTION / REAR_CAMERA_RESOLUTION   ((width, height))

The drive code reads those globals and passes the resolution to the start_*
functions below. These functions stay config-agnostic so they remain easy to
reuse and test.

frame_queue  → front camera JPEG bytes (also fed to AI sidecar)
ai_queue     → front camera JPEG bytes for AI inference
rear_queue   → rear camera JPEG bytes
"""

import threading
import queue
import time
import cv2
import depthai as dai


# Default capture resolution if a caller does not specify one.
DEFAULT_RESOLUTION = (1280, 720)
# Default JPEG encode quality (0-100) for the MJPEG stream.
DEFAULT_JPEG_QUALITY = 60

# Rear camera queue auto-created by the 2-device discovery path in
# start_camera_thread(). web_server.JeepBotWebServer falls back to this when no
# rear_queue is passed explicitly.
_default_rear_queue: "queue.Queue | None" = None


def get_default_rear_queue() -> "queue.Queue | None":
    """Return the rear queue auto-created during 2-device discovery (or None)."""
    return _default_rear_queue


def _mxid(dev) -> "str | None":
    """Best-effort read of an OAK-D device serial across depthai versions."""
    for attr in ("getMxId", "getDeviceId"):
        fn = getattr(dev, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    for attr in ("mxid", "deviceId"):
        val = getattr(dev, attr, None)
        if val:
            return val
    return None


def resolve_devices(config):
    """
    Discover connected OAK-D devices and decide which is 'front' and which is
    'rear'. Returns (front_info, rear_info); either may be None.

    Assignment order of preference:
      1. FRONT_CAMERA_MXID / REAR_CAMERA_MXID — pin each role to a specific
         device serial (most reliable; survives reboots and USB re-ordering).
      2. Discovery order (devs[0]=front, devs[1]=rear), optionally swapped by
         the SWAP_CAMERAS flag when the physical mounting is reversed.
    """
    try:
        devs = dai.Device.getAllAvailableDevices()
    except Exception as exc:
        print(f"[camera] WARNING: Could not list OAK devices: {exc}")
        devs = []

    print(f"[camera] Found {len(devs)} OAK device(s): {[_mxid(d) for d in devs]}")

    front_mxid = (getattr(config, "FRONT_CAMERA_MXID", "") or "").strip()
    rear_mxid  = (getattr(config, "REAR_CAMERA_MXID", "") or "").strip()

    # 1) Pin by serial when provided.
    if front_mxid or rear_mxid:
        by_id = {_mxid(d): d for d in devs}
        front_info = by_id.get(front_mxid) if front_mxid else None
        rear_info  = by_id.get(rear_mxid) if rear_mxid else None
        if front_mxid and front_info is None:
            print(f"[camera] WARNING: FRONT_CAMERA_MXID '{front_mxid}' not connected.")
        if rear_mxid and rear_info is None:
            print(f"[camera] WARNING: REAR_CAMERA_MXID '{rear_mxid}' not connected.")
        return front_info, rear_info

    # 2) Discovery order, with optional swap.
    front_info = devs[0] if len(devs) >= 1 else None
    rear_info  = devs[1] if len(devs) >= 2 else None
    if getattr(config, "SWAP_CAMERAS", False):
        front_info, rear_info = rear_info, front_info
        print("[camera] SWAP_CAMERAS=True → front/rear devices swapped.")
    return front_info, rear_info


# ------------------------------------------------------------------
# Shared helper
# ------------------------------------------------------------------
def _put(q: "queue.Queue | None", data: bytes) -> None:
    """Drop-oldest enqueue — never blocks."""
    if q is None:
        return
    if q.full():
        try:
            q.get_nowait()
        except queue.Empty:
            pass
    try:
        q.put_nowait(data)
    except queue.Full:
        pass


# ------------------------------------------------------------------
# Front camera thread  (first discovered OAK-D device)
# ------------------------------------------------------------------
def start_camera_thread(
    frame_queue: queue.Queue,
    ai_queue:    "queue.Queue | None" = None,
    device_info: "dai.DeviceInfo | None" = None,
    depth_queue: "queue.Queue | None" = None,
    enable_depth: bool = False,
    resolution: "tuple[int, int]" = DEFAULT_RESOLUTION,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
) -> threading.Thread:
    """
    Opens the front OAK-D Pro and, when a second OAK is present, starts
    the rear camera for the main web UI.
    Fills frame_queue (web stream), ai_queue (AI sidecar), and optionally
    depth_queue with aligned stereo depth frames in millimeters.
    Pass device_info to pin to a specific device; otherwise uses first found.
    resolution     : (width, height) of the RGB / depth output.
    jpeg_quality   : JPEG encode quality (0-100) for the MJPEG stream.
    """
    global _default_rear_queue

    width, height = resolution

    if device_info is None:
        try:
            devs = dai.Device.getAllAvailableDevices()
        except Exception as exc:
            print(f"[camera] WARNING: Could not list OAK devices: {exc}")
            devs = []

        print(f"[camera] Found {len(devs)} OAK device(s).")
        front_info = devs[0] if len(devs) >= 1 else None
        rear_info = devs[1] if len(devs) >= 2 else None
    else:
        front_info = device_info
        rear_info = None

    def _run_worker(use_depth: bool):
        device_args = [front_info] if front_info is not None else []
        with dai.Pipeline(dai.Device(*device_args)) as pipeline:
            cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
            out = cam.requestOutput(size=(width, height), type=dai.ImgFrame.Type.BGR888p)
            rgb_q = out.createOutputQueue()

            depth_q = None
            if use_depth:
                left = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_B)
                right = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_C)
                stereo = pipeline.create(dai.node.StereoDepth)
                stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.ROBOTICS)
                stereo.setLeftRightCheck(True)
                stereo.setSubpixel(True)
                stereo.setDepthAlign(dai.CameraBoardSocket.CAM_A)
                stereo.setOutputSize(width, height)
                left.requestFullResolutionOutput().link(stereo.left)
                right.requestFullResolutionOutput().link(stereo.right)
                depth_q = stereo.depth.createOutputQueue()

            pipeline.start()
            print(f"[camera] Front OAK-D Pro started @ {width}x{height}.")
            if depth_q is not None:
                print("[camera] Front OAK-D depth stream started.")

            while True:
                msg   = rgb_q.get()
                frame = msg.getCvFrame()

                if depth_q is not None:
                    try:
                        depth_msg = depth_q.tryGet()
                        if depth_msg is not None:
                            _put(depth_queue, depth_msg.getFrame())
                    except Exception as exc:
                        print(f"[camera] WARNING: Depth stream stopped: {exc}")
                        depth_q = None

                ret, buf = cv2.imencode(
                    ".jpg", frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
                )
                if not ret:
                    continue
                jpg = buf.tobytes()
                _put(frame_queue, jpg)
                _put(ai_queue,    jpg)
                time.sleep(0.05)

    def _worker():
        use_depth = bool(enable_depth and depth_queue is not None)
        try:
            _run_worker(use_depth)
        except Exception as exc:
            if not use_depth:
                print(f"[camera] ERROR: Front OAK-D thread stopped: {exc}")
                return
            print(f"[camera] WARNING: Depth startup failed, retrying RGB only: {exc}")
            time.sleep(1.0)
            try:
                _run_worker(False)
            except Exception as fallback_exc:
                print(f"[camera] ERROR: Front OAK-D RGB fallback stopped: {fallback_exc}")

    t = threading.Thread(target=_worker, daemon=True, name="camera-front")
    t.start()

    if rear_info is not None:
        _default_rear_queue = queue.Queue(maxsize=1)
        start_rear_camera_thread(_default_rear_queue, device_info=rear_info)
    elif device_info is None:
        _default_rear_queue = None
        print("[camera] Rear OAK-D Pro not found; rear video disabled.")

    return t


# ------------------------------------------------------------------
# Rear camera thread  (second discovered OAK-D device)
# ------------------------------------------------------------------
def start_rear_camera_thread(
    rear_queue:  queue.Queue,
    device_info: "dai.DeviceInfo | None" = None,
    resolution: "tuple[int, int]" = DEFAULT_RESOLUTION,
    jpeg_quality: int = DEFAULT_JPEG_QUALITY,
) -> threading.Thread:
    """
    Opens the rear OAK-D Pro independently.
    Fills rear_queue only — no AI inference on rear feed.
    Pass device_info to pin to a specific device.
    resolution   : (width, height) of the RGB output.
    jpeg_quality : JPEG encode quality (0-100) for the MJPEG stream.
    """
    width, height = resolution

    def _worker():
        device_args = [device_info] if device_info is not None else []
        with dai.Pipeline(dai.Device(*device_args)) as pipeline:
            cam = pipeline.create(dai.node.Camera).build(dai.CameraBoardSocket.CAM_A)
            out = cam.requestOutput(size=(width, height), type=dai.ImgFrame.Type.BGR888p)
            rgb_q = out.createOutputQueue()
            pipeline.start()
            print(f"[camera] Rear OAK-D Pro started @ {width}x{height}.")

            while True:
                msg   = rgb_q.get()
                frame = msg.getCvFrame()
                ret, buf = cv2.imencode(
                    ".jpg", frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), jpeg_quality],
                )
                if not ret:
                    continue
                _put(rear_queue, buf.tobytes())
                time.sleep(0.05)

    t = threading.Thread(target=_worker, daemon=True, name="camera-rear")
    t.start()
    return t

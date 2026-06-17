"""
JeepBot Web Server — Dual OAK-D Pro edition
Runs as daemon threads inside jeepbot_drive.py (NOT subprocesses).

Main page    → http://pi-ip:8887  (mode switching + front/rear video)
Rear-only    → http://pi-ip:8888  (legacy view-only page, when used)

This file holds only the Flask servers. The OAK-D capture threads live in
camera.py; the servers just consume the JPEG queues those threads fill.

frame_queue  → front camera JPEG bytes (also fed to AI sidecar)
ai_queue     → front camera JPEG bytes for AI inference
rear_queue   → rear camera JPEG bytes
"""

from flask import Flask, render_template, Response, request, jsonify
import threading
import queue

import camera
from camera import start_camera_thread, start_rear_camera_thread


# ------------------------------------------------------------------
# Front camera web server  (port WEB_PORT, has mode switching)
# ------------------------------------------------------------------
class JeepBotWebServer:
    def __init__(
        self,
        config,
        frame_queue: queue.Queue,
        rear_queue: "queue.Queue | None" = None,
        detector=None,
    ):
        """
        Args:
            config      : myconfig module
            frame_queue : Queue of JPEG bytes for the /video stream
            rear_queue  : Optional queue of rear-camera JPEG bytes
            detector    : Optional YOLO detector with a snapshot() method
        """
        self.config      = config
        self.frame_queue = frame_queue
        self.rear_queue  = rear_queue if rear_queue is not None else camera.get_default_rear_queue()
        self.detector    = detector
        self.app         = Flask(__name__, static_folder="static", template_folder="templates")
        self._lock       = threading.Lock()
        self.mode        = config.DEFAULT_DRIVE_MODE

        self.setup_routes()

    def setup_routes(self):
        @self.app.route("/")
        def index():
            return render_template(
                "index.html",
                mode=self.get_mode(),
                rear_enabled=self.rear_queue is not None,
                yolo_enabled=self.detector is not None,
            )

        @self.app.route("/set_mode", methods=["POST"])
        def set_mode():
            data     = request.get_json()
            new_mode = data.get("mode", "manual")
            with self._lock:
                self.mode = new_mode
            print("WEB MODE CHANGED TO:", new_mode)
            return jsonify({"mode": new_mode})

        @self.app.route("/get_mode")
        def get_mode_route():
            return jsonify({"mode": self.get_mode()})

        @self.app.route("/detections")
        def detections():
            if self.detector is None:
                return jsonify({
                    "enabled": False,
                    "status": "disabled",
                    "detections": [],
                })
            return jsonify(self.detector.snapshot())

        @self.app.route("/video")
        @self.app.route("/video/front")
        def video():
            return Response(
                self._generate_frames(self.frame_queue),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

        @self.app.route("/video/rear")
        def rear_video():
            if self.rear_queue is None:
                return ("Rear camera is not available", 503)
            return Response(
                self._generate_frames(self.rear_queue),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

    def _generate_frames(self, q: "queue.Queue"):
        while True:
            try:
                jpg_bytes = q.get(timeout=2.0)
            except queue.Empty:
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: "
                + str(len(jpg_bytes)).encode()
                + b"\r\n\r\n"
                + jpg_bytes
                + b"\r\n"
            )

    def get_mode(self) -> str:
        with self._lock:
            return self.mode

    def start(self):
        t = threading.Thread(
            target=self.app.run,
            kwargs={
                "host":         self.config.WEB_HOST,
                "port":         self.config.WEB_PORT,
                "debug":        False,
                "use_reloader": False,
                "threaded":     True,
            },
            daemon=True,
            name="flask-front",
        )
        t.start()
        print(f"[web] Front camera server → http://<pi-ip>:{self.config.WEB_PORT}")


# ------------------------------------------------------------------
# Rear camera web server  (port WEB_PORT_REAR, view-only)
# ------------------------------------------------------------------
class JeepBotRearWebServer:
    # Minimal inline HTML page — no template file needed
    _PAGE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>JeepBot — Rear Camera</title>
  <style>
    body {{ margin: 0; background: #111; display: flex;
            flex-direction: column; align-items: center; justify-content: center;
            height: 100vh; color: #eee; font-family: sans-serif; }}
    h2   {{ margin-bottom: 10px; letter-spacing: 2px; color: #0cf; }}
    img  {{ max-width: 100%; border: 2px solid #0cf; border-radius: 4px; }}
  </style>
</head>
<body>
  <h2>REAR CAMERA</h2>
  <img src="/video" />
</body>
</html>"""

    def __init__(self, config, rear_queue: queue.Queue):
        """
        Args:
            config     : myconfig module
            rear_queue : Queue of JPEG bytes for the rear /video stream
        """
        self.config     = config
        self.rear_queue = rear_queue
        self.app        = Flask(__name__ + "_rear")

        self._setup_routes()

    def _setup_routes(self):
        page = self._PAGE  # capture for closure

        @self.app.route("/")
        def index():
            return page

        @self.app.route("/video")
        def video():
            return Response(
                self._generate_frames(),
                mimetype="multipart/x-mixed-replace; boundary=frame",
            )

    def _generate_frames(self):
        while True:
            try:
                jpg_bytes = self.rear_queue.get(timeout=2.0)
            except queue.Empty:
                continue
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Content-Length: "
                + str(len(jpg_bytes)).encode()
                + b"\r\n\r\n"
                + jpg_bytes
                + b"\r\n"
            )

    def start(self):
        t = threading.Thread(
            target=self.app.run,
            kwargs={
                "host":         self.config.WEB_HOST,
                "port":         self.config.WEB_PORT_REAR,
                "debug":        False,
                "use_reloader": False,
                "threaded":     True,
            },
            daemon=True,
            name="flask-rear",
        )
        t.start()
        print(f"[web] Rear  camera server → http://<pi-ip>:{self.config.WEB_PORT_REAR}")



# ------------------------------------------------------------------
# Convenience launcher — starts both cameras + both servers
# ------------------------------------------------------------------
def start_all(config, frame_queue: queue.Queue, rear_queue: queue.Queue,
              ai_queue: "queue.Queue | None" = None):
    """
    Discovers all connected OAK-D devices and starts:
      • front camera thread  (device index 0)
      • rear  camera thread  (device index 1)
      • front Flask server   (WEB_PORT)
      • rear  Flask server   (WEB_PORT_REAR)

    If only one device is found, only the front camera/server starts.
    ENABLE_FRONT_CAMERA / ENABLE_REAR_CAMERA in myconfig.py can disable
    either camera regardless of how many devices are connected.
    """
    front_info, rear_info = camera.resolve_devices(config)

    front_enabled = bool(getattr(config, "ENABLE_FRONT_CAMERA", True))
    rear_enabled  = bool(getattr(config, "ENABLE_REAR_CAMERA", True))
    front_res = getattr(config, "FRONT_CAMERA_RESOLUTION", camera.DEFAULT_RESOLUTION)
    rear_res  = getattr(config, "REAR_CAMERA_RESOLUTION", camera.DEFAULT_RESOLUTION)

    rear_active = rear_enabled and rear_info is not None

    # Front camera + server
    if front_enabled:
        start_camera_thread(frame_queue, ai_queue, device_info=front_info,
                            resolution=front_res)
    else:
        print("[camera] Front camera disabled (ENABLE_FRONT_CAMERA=False).")
    JeepBotWebServer(config, frame_queue, rear_queue if rear_active else None).start()

    # Rear camera + server (only if enabled and a second device is found)
    if rear_active:
        start_rear_camera_thread(rear_queue, device_info=rear_info,
                                 resolution=rear_res)
        JeepBotRearWebServer(config, rear_queue).start()
    elif not rear_enabled:
        print("[camera] Rear camera disabled (ENABLE_REAR_CAMERA=False).")
    else:
        print("[camera] Only 1 OAK device found — rear server not started.")

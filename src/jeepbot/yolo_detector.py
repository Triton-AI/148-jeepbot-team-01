"""
YOLO detection sidecar for JeepBot.

The detector reads the latest front-camera BGR frame through a callback and
publishes a small JSON-friendly snapshot for the web UI.
"""
from __future__ import annotations

from pathlib import Path
import threading
import time


class YoloDetector:
    def __init__(
        self,
        get_frame,
        model_path: str,
        imgsz: int = 320,
        conf: float = 0.25,
        interval_s: float = 0.20,
        get_depth=None,
        depth_min_mm: int = 150,
        depth_max_mm: int = 10000,
        depth_roi_scale: float = 0.35,
    ):
        self.get_frame = get_frame
        self.get_depth = get_depth
        self.model_path = model_path
        self.imgsz = int(imgsz)
        self.conf = float(conf)
        self.interval_s = max(0.05, float(interval_s))
        self.depth_min_mm = int(depth_min_mm)
        self.depth_max_mm = int(depth_max_mm)
        self.depth_roi_scale = max(0.05, min(1.0, float(depth_roi_scale)))

        self._lock = threading.Lock()
        self._thread: "threading.Thread | None" = None
        self._state = {
            "enabled": bool(model_path),
            "status": "starting" if model_path else "disabled",
            "model_path": model_path,
            "detections": [],
            "frame_width": None,
            "frame_height": None,
            "inference_ms": None,
            "timestamp": None,
            "age_ms": None,
            "depth_enabled": get_depth is not None,
            "depth_status": "waiting" if get_depth is not None else "disabled",
            "depth_frame_width": None,
            "depth_frame_height": None,
            "error": None,
        }

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(
            target=self._run,
            daemon=True,
            name="yolo-detector",
        )
        self._thread.start()

    def snapshot(self) -> dict:
        with self._lock:
            state = dict(self._state)
            state["detections"] = [dict(item) for item in self._state["detections"]]
        if state["timestamp"] is not None:
            state["age_ms"] = int((time.time() - state["timestamp"]) * 1000)
        return state

    def _set_state(self, **updates) -> None:
        with self._lock:
            self._state.update(updates)

    def _run(self) -> None:
        if not self.model_path:
            self._set_state(status="disabled", enabled=False)
            return

        path = Path(self.model_path)
        if not path.exists():
            self._set_state(
                status="error",
                error=f"YOLO model not found: {self.model_path}",
            )
            return

        try:
            from ultralytics import YOLO
        except Exception as exc:
            self._set_state(
                status="error",
                error=f"Could not import ultralytics: {exc}",
            )
            return

        try:
            model = YOLO(str(path))
        except Exception as exc:
            self._set_state(
                status="error",
                error=f"Could not load YOLO model: {exc}",
            )
            return

        names = getattr(model, "names", {})
        self._set_state(status="waiting_for_frame", error=None)

        while True:
            frame = self.get_frame()
            if frame is None:
                self._set_state(
                    status="waiting_for_frame",
                    detections=[],
                    timestamp=time.time(),
                )
                time.sleep(self.interval_s)
                continue

            try:
                frame_h, frame_w = frame.shape[:2]
                depth = self.get_depth() if self.get_depth is not None else None
                started = time.time()
                result = model(
                    frame,
                    imgsz=self.imgsz,
                    conf=self.conf,
                    verbose=False,
                )[0]
                inference_ms = (time.time() - started) * 1000.0
                detections = self._extract_detections(
                    result,
                    names,
                    depth=depth,
                    frame_w=frame_w,
                    frame_h=frame_h,
                )
                depth_h, depth_w = depth.shape[:2] if depth is not None else (None, None)
                self._set_state(
                    status="running",
                    detections=detections,
                    frame_width=int(frame_w),
                    frame_height=int(frame_h),
                    inference_ms=round(inference_ms, 1),
                    timestamp=time.time(),
                    depth_status="running" if depth is not None else self._depth_wait_status(),
                    depth_frame_width=int(depth_w) if depth_w is not None else None,
                    depth_frame_height=int(depth_h) if depth_h is not None else None,
                    error=None,
                )
            except Exception as exc:
                self._set_state(
                    status="error",
                    detections=[],
                    timestamp=time.time(),
                    error=str(exc),
                )
                time.sleep(1.0)
                continue

            time.sleep(self.interval_s)

    def _depth_wait_status(self) -> str:
        return "waiting" if self.get_depth is not None else "disabled"

    def _extract_detections(self, result, names, depth, frame_w: int, frame_h: int) -> list[dict]:
        detections = []
        boxes = getattr(result, "boxes", None)
        if boxes is None:
            return detections

        for box in boxes:
            xyxy = box.xyxy[0].tolist()
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            label = names.get(class_id, str(class_id)) if isinstance(names, dict) else str(class_id)
            distance = self._estimate_distance(depth, xyxy, frame_w, frame_h)
            detections.append(
                {
                    "class_id": class_id,
                    "label": label,
                    "confidence": round(confidence, 4),
                    "distance_m": distance["distance_m"],
                    "distance_mm": distance["distance_mm"],
                    "depth_samples": distance["samples"],
                    "box": {
                        "x1": round(float(xyxy[0]), 1),
                        "y1": round(float(xyxy[1]), 1),
                        "x2": round(float(xyxy[2]), 1),
                        "y2": round(float(xyxy[3]), 1),
                    },
                }
            )
        return detections

    def _estimate_distance(self, depth, xyxy, frame_w: int, frame_h: int) -> dict:
        empty = {"distance_m": None, "distance_mm": None, "samples": 0}
        if depth is None:
            return empty

        try:
            import numpy as np

            depth_arr = np.asarray(depth)
            if depth_arr.ndim < 2:
                return empty

            depth_h, depth_w = depth_arr.shape[:2]
            x1, y1, x2, y2 = [float(v) for v in xyxy]
            box_w = max(1.0, x2 - x1)
            box_h = max(1.0, y2 - y1)
            cx = (x1 + x2) / 2.0
            cy = (y1 + y2) / 2.0
            roi_w = max(3.0, box_w * self.depth_roi_scale)
            roi_h = max(3.0, box_h * self.depth_roi_scale)

            scale_x = depth_w / max(1.0, float(frame_w))
            scale_y = depth_h / max(1.0, float(frame_h))
            dx1 = int(max(0, min(depth_w - 1, (cx - roi_w / 2.0) * scale_x)))
            dx2 = int(max(0, min(depth_w, (cx + roi_w / 2.0) * scale_x)))
            dy1 = int(max(0, min(depth_h - 1, (cy - roi_h / 2.0) * scale_y)))
            dy2 = int(max(0, min(depth_h, (cy + roi_h / 2.0) * scale_y)))
            if dx2 <= dx1 or dy2 <= dy1:
                return empty

            roi = depth_arr[dy1:dy2, dx1:dx2]
            valid = roi[(roi >= self.depth_min_mm) & (roi <= self.depth_max_mm)]
            if valid.size == 0:
                return empty

            distance_mm = int(round(float(np.median(valid))))
            return {
                "distance_m": round(distance_mm / 1000.0, 2),
                "distance_mm": distance_mm,
                "samples": int(valid.size),
            }
        except Exception:
            return empty

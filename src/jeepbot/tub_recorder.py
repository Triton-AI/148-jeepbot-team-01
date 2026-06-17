"""
tub_recorder.py — JeepBot data recorder for autonomous training

Records (camera frame, steering_norm, duty) tuples to disk while
drive mode is "record".  Layout mirrors Donkey Car tubs so you can
use donkey train directly on the data.

Tub layout
----------
tub/<session>/
    images/
        frame_000001.jpg
        frame_000002.jpg
        ...
    records.jsonl          ← one JSON line per frame

Each JSONL record
-----------------
{
  "frame_idx": 1,
  "image_file": "images/frame_000001.jpg",
  "steering_norm": -0.23,   # -1.0 (full left) … +1.0 (full right)
  "steering_deg":  -27.3,   # raw degrees sent to VESC
  "duty":           0.15,   # raw duty sent to VESC  (-1…+1)
  "timestamp_ms":  1716300000123
}

steering_norm is what the model trains on.
steering_deg / duty are kept for debugging / re-normalisation.
"""

from __future__ import annotations

import json
import os
import queue
import threading
import time
from datetime import datetime
from pathlib import Path


class TubRecorder:
    """
    Drop-in recorder.  Call update() every drive loop tick.
    It writes to disk in a background thread so the 100 Hz loop
    is never blocked by file I/O.
    """

    def __init__(
        self,
        config,
        frame_queue: queue.Queue,
        tub_root: str = "tub",
    ):
        """
        Args:
            config       : myconfig module  (needs STEERING_* constants)
            frame_queue  : same Queue the camera thread fills with JPEG bytes
                           (TubRecorder peeks at the latest frame)
            tub_root     : directory that holds all tub sessions
        """
        self.config = config
        self.frame_queue = frame_queue

        # Create a timestamped session folder
        session_name = datetime.now().strftime("session_%Y%m%d_%H%M%S")
        self.session_dir = Path(tub_root) / session_name
        self.img_dir = self.session_dir / "images"
        self.img_dir.mkdir(parents=True, exist_ok=True)

        self.record_path = self.session_dir / "records.jsonl"
        self._record_file = self.record_path.open("w")

        self._frame_idx = 0
        self._lock = threading.Lock()
        self._write_queue: queue.Queue = queue.Queue(maxsize=200)
        self._active = True

        # Background writer thread — keeps I/O off the drive loop
        self._writer = threading.Thread(
            target=self._writer_loop,
            daemon=True,
            name="tub-writer",
        )
        self._writer.start()

        print(f"[TubRecorder] Recording to {self.session_dir}")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def update(
        self,
        steering_deg: float,
        duty: float,
        latest_jpeg: bytes | None,
    ) -> None:
        """
        Call once per drive loop tick while mode == 'record'.

        Args:
            steering_deg : actual degrees commanded to steering VESC
            duty         : actual duty commanded to drive VESC
            latest_jpeg  : JPEG bytes from the camera queue (or None)
        """
        if latest_jpeg is None:
            return  # no frame yet — skip rather than record a blank

        with self._lock:
            idx = self._frame_idx
            self._frame_idx += 1

        steering_norm = self._deg_to_norm(steering_deg)

        record = {
            "frame_idx": idx,
            "image_file": f"images/frame_{idx:07d}.jpg",
            "steering_norm": round(steering_norm, 6),
            "steering_deg": round(steering_deg, 4),
            "duty": round(duty, 6),
            "timestamp_ms": int(time.time() * 1000),
        }

        # Hand off to background writer (non-blocking)
        try:
            self._write_queue.put_nowait((record, latest_jpeg))
        except queue.Full:
            pass  # drop frame rather than stall the drive loop

    def close(self) -> None:
        """Flush and close the tub.  Called on exit."""
        self._active = False
        self._write_queue.join()
        self._record_file.close()
        print(
            f"[TubRecorder] Saved {self._frame_idx} frames "
            f"→ {self.session_dir}"
        )

    def frame_count(self) -> int:
        with self._lock:
            return self._frame_idx

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _writer_loop(self) -> None:
        while self._active or not self._write_queue.empty():
            try:
                record, jpeg_bytes = self._write_queue.get(timeout=0.5)
            except queue.Empty:
                continue

            # Write image
            img_path = self.session_dir / record["image_file"]
            img_path.write_bytes(jpeg_bytes)

            # Write JSON line
            self._record_file.write(json.dumps(record) + "\n")
            self._record_file.flush()

            self._write_queue.task_done()

    def _deg_to_norm(self, deg: float) -> float:
        """
        Convert VESC steering degrees → normalised [-1, +1].

        LEFT  = -1.0  (full left)
        CENTER =  0.0
        RIGHT = +1.0  (full right)
        """
        cfg = self.config
        center = cfg.DEFAULT_STEERING_CENTER_DEG
        left   = cfg.DEFAULT_STEERING_LEFT_DEG
        right  = cfg.DEFAULT_STEERING_RIGHT_DEG

        if deg <= center:
            # centre → left
            span = center - left
            if span == 0:
                return 0.0
            return -((center - deg) / span)
        else:
            # centre → right
            span = right - center
            if span == 0:
                return 0.0
            return (deg - center) / span

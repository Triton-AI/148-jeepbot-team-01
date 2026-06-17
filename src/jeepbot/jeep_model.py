"""
jeep_model.py — CNN model for JeepBot autonomous driving

Architecture
------------
Mirrors Donkey Car's default linear model (dave2-style CNN → Dense heads).
Input : (120, 160, 3) RGB image  — matches OAK-D Pro output resized in web_server
Output: two scalars
    steering_norm  in [-1, +1]   (denormalise → degrees for VESC SetPosition)
    duty           in [-1, +1]   (scale by MAX_DUTY for VESC SetDutyCycle)

Training
--------
Run from the project root after collecting tub data:

    python3 jeep_train.py --tub tub --model models/jeep_pilot.keras

Inference
---------
    from jeep_model import load_pilot
    pilot = load_pilot("models/jeep_pilot.keras")
    steering_norm, duty = pilot.predict(bgr_frame)
"""

from __future__ import annotations

import numpy as np

# TensorFlow / Keras — lazy import so the file is importable without TF
# on machines that only need to inspect the architecture.
try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers
    _TF_AVAILABLE = True
except ImportError:
    _TF_AVAILABLE = False


# -----------------------------------------------------------------------
# Image pre-processing (shared by training and inference)
# -----------------------------------------------------------------------

IMG_H = 120
IMG_W = 160
IMG_C = 3

# Crop the bottom N rows (Jeep hood) and top N rows (sky) before training.
# Tune these to match what your camera actually sees on the track.
CROP_TOP    = 20   # rows to remove from the top   (sky / irrelevant background)
CROP_BOTTOM = 10   # rows to remove from the bottom (hood / bonnet)


def preprocess(bgr_frame: np.ndarray) -> np.ndarray:
    """
    Prepare a raw BGR OpenCV frame for the model.

    Steps:
      1. Resize to (IMG_H, IMG_W) — should already be this size from OAK-D
      2. Crop top / bottom
      3. Normalise pixel values to [0, 1]
      4. Add batch dimension → (1, H, W, 3)

    Returns a float32 array ready for model.predict().
    """
    import cv2

    # 1. Resize if needed (camera outputs 320×200; crop brings it to model size)
    if bgr_frame.shape[:2] != (IMG_H, IMG_W):
        bgr_frame = cv2.resize(bgr_frame, (IMG_W, IMG_H))

    # 2. Crop
    h = bgr_frame.shape[0]
    top    = min(CROP_TOP, h - 1)
    bottom = max(h - CROP_BOTTOM, top + 1)
    cropped = bgr_frame[top:bottom, :, :]

    # 3. Resize back to fixed model input after crop
    resized = cv2.resize(cropped, (IMG_W, IMG_H))

    # 4. RGB conversion + normalise
    rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    # 5. Batch dim
    return np.expand_dims(rgb, axis=0)


# -----------------------------------------------------------------------
# Model definition
# -----------------------------------------------------------------------

def build_model(input_shape: tuple = (IMG_H, IMG_W, IMG_C)) -> "keras.Model":
    """
    Build and return the untrained Keras model.

    Architecture (dave2 / Donkey Car style):
        5 Conv layers  →  Flatten  →  3 Dense layers
        Two output heads: steering_norm, duty
    """
    if not _TF_AVAILABLE:
        raise ImportError("TensorFlow is required to build the model.")

    inp = keras.Input(shape=input_shape, name="image")

    x = layers.Conv2D(24, (5, 5), strides=(2, 2), activation="relu")(inp)
    x = layers.Conv2D(32, (5, 5), strides=(2, 2), activation="relu")(x)
    x = layers.Conv2D(64, (5, 5), strides=(2, 2), activation="relu")(x)
    x = layers.Conv2D(64, (3, 3), strides=(1, 1), activation="relu")(x)
    x = layers.Conv2D(64, (3, 3), strides=(1, 1), activation="relu")(x)

    x = layers.Flatten()(x)
    x = layers.Dense(100, activation="relu")(x)
    x = layers.Dropout(0.1)(x)
    x = layers.Dense(50, activation="relu")(x)
    x = layers.Dropout(0.1)(x)

    # Two heads — tanh keeps outputs in [-1, +1]
    steering_out = layers.Dense(1, activation="tanh", name="steering")(x)
    duty_out     = layers.Dense(1, activation="tanh", name="duty")(x)

    model = keras.Model(inputs=inp, outputs=[steering_out, duty_out])

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=1e-4),
        loss={
            "steering": "mse",
            "duty":     "mse",
        },
        metrics={
            "steering": "mae",
            "duty":     "mae",
        },
    )

    return model


# -----------------------------------------------------------------------
# Inference helper
# -----------------------------------------------------------------------

class JeepPilot:
    """
    Wraps a trained Keras model for real-time inference in the drive loop.

    Usage
    -----
        pilot = JeepPilot("models/jeep_pilot.keras")
        steering_norm, duty = pilot.predict(bgr_frame)
    """

    def __init__(self, model_path: str):
        if not _TF_AVAILABLE:
            raise ImportError("TensorFlow is required for inference.")
        self.model = keras.models.load_model(model_path)
        print(f"[JeepPilot] Loaded model from {model_path}")

    def predict(self, bgr_frame: np.ndarray) -> tuple[float, float]:
        """
        Args:
            bgr_frame : raw OpenCV BGR frame (any size — will be resized)

        Returns:
            (steering_norm, duty)  both in [-1, +1]
        """
        x = preprocess(bgr_frame)
        steering_raw, duty_raw = self.model.predict(x, verbose=0)
        steering_norm = float(np.clip(steering_raw[0, 0], -1.0, 1.0))
        duty          = float(np.clip(duty_raw[0, 0],     -1.0, 1.0))
        return steering_norm, duty


def load_pilot(model_path: str) -> JeepPilot:
    """Convenience function — returns a ready JeepPilot."""
    return JeepPilot(model_path)

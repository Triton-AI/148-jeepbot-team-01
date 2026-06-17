"""
jeep_train.py — train the JeepBot pilot CNN from tub data

Usage
-----
    # Train on all sessions inside ./tub/
    python3 jeep_train.py --tub tub --model models/jeep_pilot.keras

    # Train on a specific session only
    python3 jeep_train.py --tub tub/session_20260521_143000 --model models/jeep_pilot.keras

    # Resume / fine-tune from an existing model
    python3 jeep_train.py --tub tub --model models/jeep_pilot.keras --base models/jeep_pilot.keras

Options
-------
    --tub       path to tub root or single session dir  (default: tub)
    --model     where to save the trained model         (default: models/jeep_pilot.keras)
    --base      existing model to fine-tune             (optional)
    --epochs    training epochs                         (default: 100)
    --batch     batch size                              (default: 64)
    --val-split fraction of data kept for validation   (default: 0.15)
    --no-aug    disable data augmentation
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

try:
    import tensorflow as tf
    from tensorflow import keras
except ImportError:
    sys.exit("TensorFlow not found.  Install with:  pip install tensorflow")

from jeep_model import build_model, preprocess, IMG_H, IMG_W


# -----------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------

def find_sessions(tub_root: str) -> list[Path]:
    """
    Return a list of session directories found under tub_root.
    A session dir contains a records.jsonl file.
    """
    root = Path(tub_root)

    # If the path itself is a session, use it directly
    if (root / "records.jsonl").exists():
        return [root]

    # Otherwise scan one level deep for session_* folders
    sessions = sorted(
        p for p in root.iterdir()
        if p.is_dir() and (p / "records.jsonl").exists()
    )
    return sessions


def load_dataset(sessions: list[Path]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load all records from a list of session dirs.

    Returns
    -------
    images         : float32 (N, IMG_H, IMG_W, 3)  normalised 0-1
    steering_norms : float32 (N,)
    duties         : float32 (N,)
    """
    images_list: list[np.ndarray] = []
    steerings: list[float] = []
    duties: list[float] = []

    for session in sessions:
        record_path = session / "records.jsonl"
        print(f"  Loading {session.name} …", end=" ", flush=True)
        count = 0

        with record_path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)

                img_path = session / rec["image_file"]
                if not img_path.exists():
                    continue

                bgr = cv2.imread(str(img_path))
                if bgr is None:
                    continue

                # preprocess returns (1, H, W, 3) — squeeze the batch dim
                x = preprocess(bgr)[0]
                images_list.append(x)
                steerings.append(float(rec["steering_norm"]))
                duties.append(float(rec["duty"]))
                count += 1

        print(f"{count} frames")

    if not images_list:
        sys.exit("No valid frames found in tub.  Check tub path and image files.")

    images = np.stack(images_list, axis=0).astype(np.float32)
    s_arr  = np.array(steerings, dtype=np.float32)
    d_arr  = np.array(duties,    dtype=np.float32)

    print(f"  Total: {len(images)} frames")
    return images, s_arr, d_arr


# -----------------------------------------------------------------------
# Augmentation
# -----------------------------------------------------------------------

def augment_batch(
    images: np.ndarray,
    steerings: np.ndarray,
    duties: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Light augmentation applied per-batch:
      - random brightness  ±20 %
      - horizontal flip (mirrors steering sign)
      - small random crop shift (±10 px) to simulate lateral position variation
    """
    rng = np.random.default_rng()

    # Brightness jitter
    factor = rng.uniform(0.80, 1.20, size=(len(images), 1, 1, 1)).astype(np.float32)
    images = np.clip(images * factor, 0.0, 1.0)

    # Horizontal flip with 50 % probability
    flip_mask = rng.random(len(images)) < 0.5
    images[flip_mask]    = images[flip_mask, :, ::-1, :]
    steerings[flip_mask] = -steerings[flip_mask]

    return images, steerings, duties


# -----------------------------------------------------------------------
# Training
# -----------------------------------------------------------------------

def train(args: argparse.Namespace) -> None:
    # ---- Find tub sessions ----
    sessions = find_sessions(args.tub)
    if not sessions:
        sys.exit(f"No tub sessions found under '{args.tub}'")
    print(f"Found {len(sessions)} session(s):")

    # ---- Load data ----
    images, steerings, duties = load_dataset(sessions)
    N = len(images)

    # ---- Shuffle ----
    idx = np.random.permutation(N)
    images    = images[idx]
    steerings = steerings[idx]
    duties    = duties[idx]

    # ---- Train / val split ----
    val_n   = max(1, int(N * args.val_split))
    train_n = N - val_n

    X_train, X_val = images[:train_n],    images[train_n:]
    S_train, S_val = steerings[:train_n], steerings[train_n:]
    D_train, D_val = duties[:train_n],    duties[train_n:]

    print(f"Train: {train_n}  |  Val: {val_n}")

    # ---- Build or load model ----
    if args.base and Path(args.base).exists():
        print(f"Fine-tuning from {args.base}")
        model = keras.models.load_model(args.base)
    else:
        model = build_model()

    model.summary()

    # ---- Callbacks ----
    Path(args.model).parent.mkdir(parents=True, exist_ok=True)

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=args.model,
            monitor="val_loss",
            save_best_only=True,
            verbose=1,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=10,
            restore_best_weights=True,
            verbose=1,
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=5,
            min_lr=1e-6,
            verbose=1,
        ),
    ]

    # ---- Augmentation wrapper ----
    def make_dataset(X, S, D, shuffle: bool, augment: bool) -> tf.data.Dataset:
        def gen():
            indices = np.arange(len(X))
            if shuffle:
                np.random.shuffle(indices)
            for i in indices:
                img = X[i]
                s   = S[i]
                d   = D[i]
                if augment and not args.no_aug:
                    img_b, s_b, d_b = augment_batch(
                        img[np.newaxis], np.array([s]), np.array([d])
                    )
                    img = img_b[0]
                    s   = s_b[0]
                    d   = d_b[0]
                yield img, {"steering": s, "duty": d}

        return (
            tf.data.Dataset.from_generator(
                gen,
                output_signature=(
                    tf.TensorSpec(shape=(IMG_H, IMG_W, 3), dtype=tf.float32),
                    {
                        "steering": tf.TensorSpec(shape=(), dtype=tf.float32),
                        "duty":     tf.TensorSpec(shape=(), dtype=tf.float32),
                    },
                ),
            )
            .batch(args.batch)
            .prefetch(tf.data.AUTOTUNE)
        )

    train_ds = make_dataset(X_train, S_train, D_train, shuffle=True,  augment=True)
    val_ds   = make_dataset(X_val,   S_val,   D_val,   shuffle=False, augment=False)

    # ---- Train ----
    print(f"\nTraining for up to {args.epochs} epochs …\n")
    model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=args.epochs,
        callbacks=callbacks,
    )

    print(f"\nBest model saved to: {args.model}")


# -----------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Train JeepBot pilot CNN")
    parser.add_argument("--tub",       default="tub",                   help="Tub root or session dir")
    parser.add_argument("--model",     default="models/jeep_pilot.keras", help="Output model path")
    parser.add_argument("--base",      default=None,                    help="Existing model to fine-tune")
    parser.add_argument("--epochs",    type=int,   default=100,         help="Max epochs")
    parser.add_argument("--batch",     type=int,   default=64,          help="Batch size")
    parser.add_argument("--val-split", type=float, default=0.15,        help="Validation fraction")
    parser.add_argument("--no-aug",    action="store_true",             help="Disable augmentation")
    args = parser.parse_args()

    train(args)


if __name__ == "__main__":
    main()

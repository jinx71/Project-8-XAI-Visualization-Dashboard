"""Loads the CNN classifier and runs inference.

Supports two modes:
  * Thesis mode  -> loads a saved Keras model from MODEL_PATH.
  * Demo mode    -> uses a pretrained EfficientNetV2B0 (ImageNet) so the full
                    pipeline works without proprietary thesis weights.
"""
import io

import numpy as np
import tensorflow as tf
from PIL import Image

from .config import settings


class ModelService:
    def __init__(self) -> None:
        self.input_size = settings.INPUT_SIZE
        self._load()

    def _load(self) -> None:
        if settings.demo_mode:
            # EfficientNetV2B0 mirrors the EfficientNetV2 family used in the
            # thesis ensemble, so GradCAM behaves representatively in demos.
            self.model = tf.keras.applications.EfficientNetV2B0(weights="imagenet")
            self.preprocess = tf.keras.applications.efficientnet_v2.preprocess_input
            self.class_names = self._imagenet_top_labels()
            self._imagenet = True
        else:
            self.model = tf.keras.models.load_model(settings.MODEL_PATH, compile=False)
            # Thesis pipeline preprocessing: EfficientNetV2 expects raw 0-255.
            self.preprocess = tf.keras.applications.efficientnet_v2.preprocess_input
            n_out = int(self.model.output_shape[-1])
            self.class_names = settings.CLASS_NAMES or [
                f"class_{i}" for i in range(n_out)
            ]
            self._imagenet = False

        self.last_conv_layer = self._resolve_last_conv_layer()

    def _resolve_last_conv_layer(self) -> str:
        if settings.LAST_CONV_LAYER:
            return settings.LAST_CONV_LAYER
        # Walk layers in reverse, return the last one emitting a 4D tensor.
        for layer in reversed(self.model.layers):
            try:
                shape = layer.output.shape
            except AttributeError:
                continue
            if len(shape) == 4:
                return layer.name
        raise RuntimeError("No 4D conv layer found for GradCAM.")

    @staticmethod
    def _imagenet_top_labels() -> list[str]:
        # Lazy: full 1000-class decode happens at predict time. Placeholder here.
        return []

    def preprocess_image(self, raw: bytes) -> tuple[np.ndarray, Image.Image]:
        """Return (model_input_batch, display_image)."""
        img = Image.open(io.BytesIO(raw)).convert("RGB")
        resized = img.resize((self.input_size, self.input_size))
        arr = np.asarray(resized).astype("float32")
        batch = self.preprocess(np.expand_dims(arr.copy(), axis=0))
        return batch, resized

    def predict(self, batch: np.ndarray) -> np.ndarray:
        """Return a 1D probability vector."""
        preds = self.model.predict(batch, verbose=0)[0]
        # If the model emits logits (no softmax head), normalise.
        if not np.isclose(preds.sum(), 1.0, atol=1e-2):
            preds = tf.nn.softmax(preds).numpy()
        return preds

    def label_probabilities(self, preds: np.ndarray) -> list[dict]:
        if self._imagenet:
            decoded = tf.keras.applications.efficientnet_v2.decode_predictions(
                np.expand_dims(preds, 0), top=5
            )[0]
            return [
                {"label": name.replace("_", " "), "probability": float(score)}
                for (_, name, score) in decoded
            ]
        pairs = sorted(
            zip(self.class_names, preds), key=lambda p: p[1], reverse=True
        )
        return [
            {"label": label, "probability": float(prob)} for label, prob in pairs
        ]


# Instantiated once at import; model weights load a single time per process.
model_service = ModelService()

"""GradCAM: class-discriminative localisation heatmaps.

Implements the standard Grad-CAM (Selvaraju et al., 2017): gradient of the
target class score w.r.t. the last conv feature maps, global-average-pooled
into channel weights, applied to the feature maps and ReLU'd.
"""
import base64
import io

import numpy as np
import tensorflow as tf
from PIL import Image


def _build_grad_model(model: tf.keras.Model, last_conv_layer: str) -> tf.keras.Model:
    """Model that returns (conv feature maps, predictions) in one pass."""
    return tf.keras.models.Model(
        model.inputs,
        [model.get_layer(last_conv_layer).output, model.output],
    )


def compute_heatmap(
    model: tf.keras.Model,
    batch: np.ndarray,
    last_conv_layer: str,
    class_index: int,
) -> np.ndarray:
    """Return a 2D heatmap normalised to [0, 1]."""
    grad_model = _build_grad_model(model, last_conv_layer)

    with tf.GradientTape() as tape:
        conv_out, preds = grad_model(batch)
        class_score = preds[:, class_index]

    grads = tape.gradient(class_score, conv_out)
    # Channel importance = mean gradient over spatial dims.
    pooled = tf.reduce_mean(grads, axis=(0, 1, 2))

    conv_out = conv_out[0]
    heatmap = conv_out @ pooled[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.maximum(heatmap, 0)  # ReLU: keep features that raise the score
    max_val = tf.reduce_max(heatmap)
    if max_val > 0:
        heatmap = heatmap / max_val
    return heatmap.numpy()


def _apply_colormap(heatmap: np.ndarray, size: int) -> np.ndarray:
    """Map a [0,1] heatmap to an RGB jet-style colour array of (size, size, 3)."""
    hm = Image.fromarray(np.uint8(heatmap * 255)).resize(
        (size, size), Image.BILINEAR
    )
    hm = np.asarray(hm).astype("float32") / 255.0

    # Lightweight jet colormap (no matplotlib dependency).
    r = np.clip(1.5 - np.abs(4 * hm - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * hm - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * hm - 1), 0, 1)
    return np.stack([r, g, b], axis=-1) * 255.0


def overlay_heatmap(
    display_image: Image.Image, heatmap: np.ndarray, alpha: float = 0.4
) -> Image.Image:
    """Blend the coloured heatmap over the original image."""
    size = display_image.size[0]
    coloured = _apply_colormap(heatmap, size)
    base = np.asarray(display_image).astype("float32")
    blended = base * (1 - alpha) + coloured * alpha
    return Image.fromarray(np.uint8(np.clip(blended, 0, 255)))


def image_to_data_uri(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

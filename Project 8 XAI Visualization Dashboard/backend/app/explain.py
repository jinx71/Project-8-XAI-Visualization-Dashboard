"""Builds a plain-language explanation of a prediction.

Two tiers:
  * If ANTHROPIC_API_KEY is set, asks Claude to write a clinician-readable note
    grounded in the prediction + heatmap coverage statistics.
  * Otherwise, a deterministic template produces a solid offline explanation so
    the app never hard-depends on a paid API (stays free-tier runnable).
"""
import os

import numpy as np


def _heatmap_stats(heatmap: np.ndarray) -> dict:
    """Summarise where the model 'looked' for the report to reference."""
    threshold = 0.5
    hot = heatmap >= threshold
    coverage = float(hot.mean())

    # Centroid of the hot region, expressed as quadrant language.
    if hot.any():
        ys, xs = np.where(hot)
        cy, cx = ys.mean() / heatmap.shape[0], xs.mean() / heatmap.shape[1]
        vert = "upper" if cy < 0.4 else "lower" if cy > 0.6 else "central"
        horz = "left" if cx < 0.4 else "right" if cx > 0.6 else "central"
        region = f"{vert} {horz}".replace("central central", "central")
    else:
        region = "no strongly activated"

    return {"coverage": coverage, "region": region}


def _template_explanation(
    label: str, confidence: float, stats: dict
) -> str:
    pct = f"{confidence * 100:.1f}%"
    cov = f"{stats['coverage'] * 100:.0f}%"
    return (
        f"The model classified this image as **{label}** with {pct} confidence. "
        f"The Grad-CAM heatmap shows the prediction was driven mainly by the "
        f"{stats['region']} region of the image, which accounts for about {cov} "
        f"of the strongly activated area. Warmer colours mark the pixels that "
        f"most increased the score for this class. This is a model "
        f"interpretation, not a diagnosis, and should be reviewed by a "
        f"qualified professional."
    )


def _claude_explanation(label: str, confidence: float, stats: dict) -> str:
    # Imported lazily so the package isn't required in offline deployments.
    from anthropic import Anthropic

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    prompt = (
        f"A CNN classified a cell microscopy image as '{label}' with "
        f"{confidence * 100:.1f}% confidence. A Grad-CAM saliency map shows the "
        f"decision was concentrated in the {stats['region']} region "
        f"({stats['coverage'] * 100:.0f}% strong activation). Write a concise, "
        f"3-4 sentence plain-language explanation for a clinician. Explain what "
        f"the heatmap indicates about the model's focus, and end with a clear "
        f"reminder that this is a decision-support output, not a diagnosis. Do "
        f"not invent clinical findings beyond what the data supports."
    )
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def build_explanation(
    label: str, confidence: float, heatmap: np.ndarray
) -> str:
    stats = _heatmap_stats(heatmap)
    if os.environ.get("ANTHROPIC_API_KEY"):
        try:
            return _claude_explanation(label, confidence, stats)
        except Exception:
            # Never fail the request because the LLM call did — fall back.
            return _template_explanation(label, confidence, stats)
    return _template_explanation(label, confidence, stats)

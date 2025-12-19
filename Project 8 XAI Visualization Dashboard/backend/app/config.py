"""Environment-driven application settings."""
import os


class Settings:
    # Path to a saved Keras model (.h5 or SavedModel dir). When empty, the
    # service falls back to a pretrained EfficientNetV2B0 (ImageNet) so the app
    # runs end-to-end without thesis weights.
    MODEL_PATH: str = os.environ.get("MODEL_PATH", "")

    # Comma-separated class names. For the SIPaKMed 5-class thesis model set:
    #   CLASS_NAMES=Dyskeratotic,Koilocytotic,Metaplastic,Parabasal,Superficial-Intermediate
    CLASS_NAMES: list[str] = [
        c.strip()
        for c in os.environ.get("CLASS_NAMES", "").split(",")
        if c.strip()
    ]

    # Square input size the model expects.
    INPUT_SIZE: int = int(os.environ.get("INPUT_SIZE", "224"))

    # Name of the last conv layer to hook for GradCAM. Empty = auto-detect the
    # last 4D layer in the model.
    LAST_CONV_LAYER: str = os.environ.get("LAST_CONV_LAYER", "")

    # CORS origins for the frontend.
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in os.environ.get(
            "CORS_ORIGINS", "http://localhost:5173"
        ).split(",")
        if o.strip()
    ]

    # Max upload size in megabytes.
    MAX_UPLOAD_MB: int = int(os.environ.get("MAX_UPLOAD_MB", "10"))

    @property
    def demo_mode(self) -> bool:
        return not self.MODEL_PATH


settings = Settings()

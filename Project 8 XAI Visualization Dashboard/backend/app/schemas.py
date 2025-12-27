"""Pydantic models for API responses."""
from pydantic import BaseModel


class ClassProbability(BaseModel):
    label: str
    probability: float


class PredictionData(BaseModel):
    predicted_label: str
    confidence: float
    probabilities: list[ClassProbability]
    # Base64-encoded PNGs (data-URI ready) returned to the frontend.
    original_image: str
    gradcam_overlay: str
    explanation: str
    demo_mode: bool


class ApiResponse(BaseModel):
    success: bool
    data: PredictionData | None = None
    message: str = ""


class HealthData(BaseModel):
    status: str
    demo_mode: bool
    classes: list[str]
    input_size: int


class HealthResponse(BaseModel):
    success: bool
    data: HealthData
    message: str = ""

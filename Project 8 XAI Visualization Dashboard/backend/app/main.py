"""FastAPI application: image in -> prediction + GradCAM + explanation out."""
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .explain import build_explanation
from .gradcam import compute_heatmap, image_to_data_uri, overlay_heatmap
from .model_service import model_service
from .schemas import (
    ApiResponse,
    HealthData,
    HealthResponse,
    PredictionData,
)

app = FastAPI(title="XAI Visualisation Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(
        success=True,
        data=HealthData(
            status="ok",
            demo_mode=settings.demo_mode,
            classes=model_service.class_names,
            input_size=settings.INPUT_SIZE,
        ),
    )


@app.post("/api/predict", response_model=ApiResponse)
async def predict(file: UploadFile = File(...)) -> ApiResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")

    raw = await file.read()
    if len(raw) > settings.MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Image exceeds {settings.MAX_UPLOAD_MB}MB limit.",
        )

    try:
        batch, display_image = model_service.preprocess_image(raw)
        preds = model_service.predict(batch)
        ranked = model_service.label_probabilities(preds)

        top_label = ranked[0]["label"]
        top_conf = ranked[0]["probability"]
        class_index = int(preds.argmax())

        heatmap = compute_heatmap(
            model_service.model, batch, model_service.last_conv_layer, class_index
        )
        overlay = overlay_heatmap(display_image, heatmap)
        explanation = build_explanation(top_label, top_conf, heatmap)

        data = PredictionData(
            predicted_label=top_label,
            confidence=top_conf,
            probabilities=ranked,
            original_image=image_to_data_uri(display_image),
            gradcam_overlay=image_to_data_uri(overlay),
            explanation=explanation,
            demo_mode=settings.demo_mode,
        )
        return ApiResponse(success=True, data=data, message="Prediction complete.")

    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}")

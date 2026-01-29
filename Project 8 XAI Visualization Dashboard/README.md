# XAI Visualisation Dashboard

A full-stack web application that turns a CNN image classifier into an
**explainable** tool: upload an image, and the app returns the model's
prediction, a **Grad-CAM** heatmap showing *where* the model looked, and a
**plain-language report** explaining the decision.

Packaged from MSc thesis research (*Explainable AI for Cervical Cell
Classification*) into a deployable product — research-grade XAI as a web app.

![screenshot placeholder](docs/screenshot.png)

**Live demo:** _add Vercel + Render URLs here_

---

## Why it matters

Most classifiers are black boxes. This dashboard makes the reasoning visible:
the Grad-CAM overlay localises the pixels that drove the prediction, and the
report translates the heatmap statistics into a clinician-readable summary. The
explanation is **grounded** in real saliency data (activation region and
coverage), not invented — the standard you want in a regulated/medical context.

## Tech stack

| Layer    | Technology                                            |
| -------- | ----------------------------------------------------- |
| Frontend | React, TypeScript, Tailwind CSS, Recharts, Axios, Vite |
| Backend  | Python, FastAPI, TensorFlow / Keras, Pillow, NumPy     |
| XAI      | Grad-CAM (gradient-based saliency)                     |
| AI report| Anthropic Claude API (optional; template fallback)     |

## Two modes

The backend runs identically in either mode — switch via one env var.

- **Demo mode** (default): no thesis weights needed. Loads a pretrained
  `EfficientNetV2B0` (ImageNet) so the full pipeline works out of the box.
  Recruiters can run it immediately.
- **Thesis mode**: set `MODEL_PATH` to your saved Keras model and `CLASS_NAMES`
  to the SIPaKMed 5 classes to serve the real cervical-cell classifier.

## Project structure

```
xai-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + routes
│   │   ├── config.py          # env-driven settings
│   │   ├── model_service.py   # model load + inference
│   │   ├── gradcam.py         # Grad-CAM heatmap generation
│   │   ├── explain.py         # plain-language report (Claude or template)
│   │   └── schemas.py         # Pydantic response models
│   ├── models/                # drop thesis weights here
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/client.ts      # typed Axios client
        ├── components/        # UploadZone, HeatmapViewer, PredictionPanel, ReportCard
        └── App.tsx
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # edit MODEL_PATH for thesis mode
uvicorn app.main:app --reload --port 8000
```

API docs auto-generate at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
cp .env.example .env          # VITE_API_URL defaults to localhost:8000
npm run dev                   # http://localhost:5173
```

## API

| Method | Endpoint       | Description                                   |
| ------ | -------------- | --------------------------------------------- |
| GET    | `/api/health`  | Status, mode, class list, input size          |
| POST   | `/api/predict` | Multipart image → prediction + heatmap + report |

All responses follow `{ success, data, message }`.

## Switching to your thesis model

1. Copy your Keras model into `backend/models/` (`.h5`, `.keras`, or SavedModel dir).
2. In `.env`:
   ```
   MODEL_PATH=models/your_model.h5
   CLASS_NAMES=Dyskeratotic,Koilocytotic,Metaplastic,Parabasal,Superficial-Intermediate
   ```
3. (Optional) set `LAST_CONV_LAYER` if auto-detection picks the wrong layer.
4. (Optional) set `ANTHROPIC_API_KEY` for Claude-generated reports.

## Deployment

- **Frontend** → Vercel (set `VITE_API_URL` to the deployed backend URL).
- **Backend** → Render or Railway. The TensorFlow image is large; prefer a
  service with ≥2GB RAM, or export the model to TF-Lite / ONNX for a lighter
  runtime.

## License

MIT

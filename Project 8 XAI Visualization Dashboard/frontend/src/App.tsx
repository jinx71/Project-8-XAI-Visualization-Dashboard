import { useEffect, useState } from 'react';
import { fetchHealth, predictImage } from './api/client';
import type { HealthData, PredictionData } from './api/client';
import HeatmapViewer from './components/HeatmapViewer';
import PredictionPanel from './components/PredictionPanel';
import ReportCard from './components/ReportCard';
import UploadZone from './components/UploadZone';

export default function App() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [result, setResult] = useState<PredictionData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchHealth().then(setHealth).catch(() => setHealth(null));
  }, []);

  const handleFile = async (file: File) => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await predictImage(file);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-5xl px-5 py-10">
        <header className="mb-8">
          <div className="flex flex-wrap items-center gap-3">
            <h1 className="text-3xl font-bold tracking-tight">
              XAI Visualisation Dashboard
            </h1>
            {health?.demo_mode && (
              <span className="rounded-full border border-amber-500/40 bg-amber-500/10 px-3 py-1 text-xs font-medium text-amber-300">
                Demo mode · ImageNet
              </span>
            )}
          </div>
          <p className="mt-2 max-w-2xl text-slate-400">
            Upload an image to see the model&apos;s prediction, a Grad-CAM
            heatmap of where it focused, and a plain-language explanation of the
            decision.
          </p>
        </header>

        <UploadZone onFile={handleFile} disabled={loading} />

        {loading && (
          <div className="mt-8 flex items-center justify-center gap-3 text-slate-400">
            <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-600 border-t-cyan-400" />
            Running inference and computing saliency…
          </div>
        )}

        {error && (
          <div
            role="alert"
            className="mt-8 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-300"
          >
            {error}
          </div>
        )}

        {result && !loading && (
          <div className="mt-8 grid gap-5 md:grid-cols-2">
            <HeatmapViewer
              original={result.original_image}
              overlay={result.gradcam_overlay}
            />
            <PredictionPanel
              label={result.predicted_label}
              confidence={result.confidence}
              probabilities={result.probabilities}
            />
            <div className="md:col-span-2">
              <ReportCard explanation={result.explanation} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

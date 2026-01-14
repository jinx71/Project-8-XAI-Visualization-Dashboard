import { useState } from 'react';

interface HeatmapViewerProps {
  original: string;
  overlay: string;
}

export default function HeatmapViewer({ original, overlay }: HeatmapViewerProps) {
  const [view, setView] = useState<'overlay' | 'original'>('overlay');

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-400">
          Grad-CAM Saliency
        </h2>
        <div className="flex rounded-lg bg-slate-800 p-1 text-xs">
          {(['overlay', 'original'] as const).map((option) => (
            <button
              key={option}
              onClick={() => setView(option)}
              className={`rounded-md px-3 py-1 font-medium capitalize transition-colors ${
                view === option
                  ? 'bg-cyan-500 text-slate-950'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-hidden rounded-xl bg-slate-950">
        <img
          src={view === 'overlay' ? overlay : original}
          alt={
            view === 'overlay'
              ? 'Grad-CAM heatmap overlaid on the input cell image'
              : 'Original input cell image'
          }
          className="mx-auto block w-full max-w-sm"
        />
      </div>

      <p className="mt-3 text-xs leading-relaxed text-slate-500">
        Warmer regions show pixels that most increased the model&apos;s score for
        the predicted class.
      </p>
    </div>
  );
}

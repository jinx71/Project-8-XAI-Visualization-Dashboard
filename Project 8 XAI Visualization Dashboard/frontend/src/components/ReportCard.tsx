interface ReportCardProps {
  explanation: string;
}

// Renders simple **bold** spans from the explanation text without a full
// markdown dependency.
function renderInline(text: string) {
  return text.split(/(\*\*[^*]+\*\*)/g).map((chunk, i) => {
    if (chunk.startsWith('**') && chunk.endsWith('**')) {
      return (
        <strong key={i} className="font-semibold text-slate-100">
          {chunk.slice(2, -2)}
        </strong>
      );
    }
    return <span key={i}>{chunk}</span>;
  });
}

export default function ReportCard({ explanation }: ReportCardProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-5">
      <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-wider text-slate-400">
        <span
          className="inline-block h-2 w-2 rounded-full bg-cyan-400"
          aria-hidden="true"
        />
        Explainable AI Report
      </h2>
      <p className="text-sm leading-relaxed text-slate-300">
        {renderInline(explanation)}
      </p>
    </div>
  );
}

import { useCallback, useRef, useState } from 'react';

interface UploadZoneProps {
  onFile: (file: File) => void;
  disabled: boolean;
}

export default function UploadZone({ onFile, disabled }: UploadZoneProps) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragging(false);
      if (disabled) return;
      const file = e.dataTransfer.files?.[0];
      if (file?.type.startsWith('image/')) onFile(file);
    },
    [onFile, disabled],
  );

  const handleSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFile(file);
  };

  return (
    <div
      onDrop={handleDrop}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onClick={() => !disabled && inputRef.current?.click()}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if ((e.key === 'Enter' || e.key === ' ') && !disabled) {
          inputRef.current?.click();
        }
      }}
      aria-label="Upload a cell image for classification"
      className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-8 py-16 text-center transition-colors focus:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400 ${
        dragging
          ? 'border-cyan-400 bg-cyan-400/5'
          : 'border-slate-700 hover:border-slate-500'
      } ${disabled ? 'cursor-not-allowed opacity-50' : ''}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleSelect}
        disabled={disabled}
      />
      <svg
        className="mb-4 h-12 w-12 text-slate-500"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        strokeWidth={1.5}
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
        />
      </svg>
      <p className="font-medium text-slate-200">
        Drop a cell image here, or click to browse
      </p>
      <p className="mt-1 text-sm text-slate-500">PNG or JPG, up to 10MB</p>
    </div>
  );
}

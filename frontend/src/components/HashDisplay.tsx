import { useState } from 'react';

interface HashDisplayProps {
  hash: string;
  label?: string;
}

export default function HashDisplay({ hash, label = 'sha-256' }: HashDisplayProps) {
  const [copied, setCopied] = useState(false);

  async function copy() {
    try {
      await navigator.clipboard.writeText(hash);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      // Clipboard API may be unavailable (e.g. insecure context). Fail silently.
    }
  }

  return (
    <div className="rounded-md border border-ink-700 bg-ink-950/60 p-3">
      <div className="flex items-center justify-between mb-1.5">
        <span className="label">{label}</span>
        <button
          type="button"
          onClick={copy}
          className="text-xs text-slate-400 hover:text-accent transition"
        >
          {copied ? 'copied' : 'copy'}
        </button>
      </div>
      <code className="mono break-all text-accent">{hash}</code>
    </div>
  );
}

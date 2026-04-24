interface BoolToggleProps {
  id: string;
  label: string;
  checked: boolean;
  onChange: (next: boolean) => void;
  hint?: string;
}

export default function BoolToggle({ id, label, checked, onChange, hint }: BoolToggleProps) {
  return (
    <div className="flex items-start justify-between gap-4 rounded-md border border-ink-700 bg-ink-800/60 px-3 py-2.5">
      <div className="min-w-0">
        <label htmlFor={id} className="text-sm text-slate-100 font-medium">
          {label}
        </label>
        {hint && <p className="mt-0.5 text-xs text-slate-500">{hint}</p>}
      </div>
      <button
        id={id}
        type="button"
        role="switch"
        aria-checked={checked}
        onClick={() => onChange(!checked)}
        className={[
          'toggle',
          checked ? 'bg-emerald-500/80' : 'bg-ink-600',
        ].join(' ')}
      >
        <span
          className={[
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition',
            checked ? 'translate-x-5' : 'translate-x-0',
          ].join(' ')}
        />
      </button>
    </div>
  );
}

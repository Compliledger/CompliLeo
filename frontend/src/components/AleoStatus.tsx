interface AleoStatusProps {
  proofStatus: string;
  verificationStatus: string;
  program?: string;
  transition?: string;
}

export default function AleoStatus({
  proofStatus,
  verificationStatus,
  program,
  transition,
}: AleoStatusProps) {
  return (
    <div className="rounded-md border border-ink-700 bg-ink-950/60 p-4">
      <div className="flex items-center justify-between mb-3">
        <span className="label">Aleo proof status</span>
        <span className="pill-info">placeholder</span>
      </div>

      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        {program && (
          <div>
            <dt className="label">program</dt>
            <dd className="mono text-slate-200">{program}</dd>
          </div>
        )}
        {transition && (
          <div>
            <dt className="label">transition</dt>
            <dd className="mono text-slate-200">{transition}</dd>
          </div>
        )}
        <div>
          <dt className="label">proof_status</dt>
          <dd>
            <span className="pill-pending mono">{proofStatus}</span>
          </dd>
        </div>
        <div>
          <dt className="label">verification_status</dt>
          <dd>
            <span className="pill-pending mono">{verificationStatus}</span>
          </dd>
        </div>
      </dl>

      <p className="mt-3 text-xs text-slate-500">
        Real Aleo execution is not wired up in this MVP. These fields will be
        populated once the program is executed against the Aleo network.
      </p>
    </div>
  );
}

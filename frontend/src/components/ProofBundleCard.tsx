import { ProofBundle } from '../lib/bundle';
import AleoStatus from './AleoStatus';
import DecisionPill from './DecisionPill';
import HashDisplay from './HashDisplay';

interface ProofBundleCardProps {
  bundle: ProofBundle;
  privateInputs: Readonly<Record<string, unknown>> | object;
}

export default function ProofBundleCard({ bundle, privateInputs }: ProofBundleCardProps) {
  return (
    <article className="card p-5 space-y-4">
      <header className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-slate-100">
            {bundle.module_label}
          </h3>
          <p className="mono text-xs text-slate-500">
            {bundle.aleo_program} :: {bundle.transition_name}
          </p>
        </div>
        <DecisionPill ok={bundle.decision_result} />
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <section>
          <span className="label">Private inputs</span>
          <pre className="mono mt-1.5 rounded-md border border-ink-700 bg-ink-950/60 p-3 text-xs text-slate-300 overflow-auto">
{JSON.stringify(privateInputs, null, 2)}
          </pre>
          <p className="mt-1.5 text-[11px] text-slate-500">
            These values stay private — only the result and proof are revealed.
          </p>
        </section>

        <section className="space-y-3">
          <div>
            <span className="label">Public result</span>
            <p className="mono mt-1.5 rounded-md border border-ink-700 bg-ink-950/60 p-3 text-slate-100">
              {bundle.public_result}
            </p>
          </div>
          <div>
            <span className="label">Reason codes</span>
            <ul className="mt-1.5 flex flex-wrap gap-1.5">
              {bundle.reason_codes.map((code) => (
                <li key={code} className="pill bg-ink-700/70 text-slate-200 mono">
                  {code}
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>

      <HashDisplay hash={bundle.bundle_hash} label="bundle_hash (sha-256)" />

      <AleoStatus
        proofStatus={bundle.proof_status}
        verificationStatus={bundle.verification_status}
        program={bundle.aleo_program}
        transition={bundle.transition_name}
      />
    </article>
  );
}

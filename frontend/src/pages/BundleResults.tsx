import { Link } from 'react-router-dom';
import AleoStatus from '../components/AleoStatus';
import DecisionPill from '../components/DecisionPill';
import HashDisplay from '../components/HashDisplay';
import ProofBundleCard from '../components/ProofBundleCard';
import { useDemoState } from '../lib/demoStore';

export default function BundleResults() {
  const state = useDemoState();
  const { tokenproof, solvencyproof, compliguard } = state.bundles;
  const combined = state.combined;

  if (!tokenproof && !solvencyproof && !compliguard) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-semibold tracking-tight">Proof Bundle Results</h1>
        <div className="card p-8 text-center space-y-4">
          <p className="text-slate-400">
            No proof bundles have been generated yet.
          </p>
          <Link to="/demo" className="btn-primary inline-flex">
            Run the demo →
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">
            Proof Bundle Results
          </h1>
          <p className="text-slate-400 mt-1">
            Per-module bundles and the aggregated combined bundle. Hashes are
            deterministic SHA-256 over canonical JSON of each bundle body.
          </p>
        </div>
        <Link to="/demo" className="btn-secondary">
          ← Back to demo
        </Link>
      </header>

      {combined && (
        <section className="card p-6 space-y-4 border-accent/30">
          <header className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <span className="pill-info mono mb-2 inline-block">combined</span>
              <h2 className="text-2xl font-semibold">Combined Proof Bundle</h2>
              <p className="text-slate-500 mono text-xs mt-0.5">
                {combined.timestamp}
              </p>
            </div>
            <DecisionPill
              ok={combined.decision_result}
              trueLabel="ALL CHECKS PASS"
              falseLabel="ONE OR MORE CHECKS FAIL"
            />
          </header>

          <HashDisplay
            hash={combined.combined_hash}
            label="combined_hash (sha-256)"
          />

          <div>
            <span className="label">Component bundle hashes</span>
            <ul className="mt-2 space-y-1.5">
              {combined.bundles.map((b) => (
                <li
                  key={b.module}
                  className="flex items-center justify-between gap-3 rounded-md border border-ink-700 bg-ink-950/60 p-2.5"
                >
                  <span className="text-sm text-slate-200">{b.module_label}</span>
                  <code className="mono text-xs text-accent truncate">
                    {b.bundle_hash}
                  </code>
                </li>
              ))}
            </ul>
          </div>

          <AleoStatus
            proofStatus={combined.proof_status}
            verificationStatus={combined.verification_status}
          />
        </section>
      )}

      <section className="space-y-4">
        <h2 className="text-xs uppercase tracking-widest text-slate-500">
          Module bundles
        </h2>
        <div className="space-y-4">
          {tokenproof && (
            <ProofBundleCard
              bundle={tokenproof}
              privateInputs={state.tokenInputs}
            />
          )}
          {solvencyproof && (
            <ProofBundleCard
              bundle={solvencyproof}
              privateInputs={state.solvencyInputs}
            />
          )}
          {compliguard && (
            <ProofBundleCard
              bundle={compliguard}
              privateInputs={state.compliInputs}
            />
          )}
        </div>
      </section>
    </div>
  );
}

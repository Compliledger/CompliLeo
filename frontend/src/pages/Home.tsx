import { Link } from 'react-router-dom';
import { MODULE_LABEL, MODULE_TAGLINE, ModuleName, PROGRAM_BY_MODULE } from '../lib/proofs';

const MODULES: ModuleName[] = ['tokenproof', 'solvencyproof', 'compliguard'];

export default function Home() {
  return (
    <div className="space-y-12">
      <section className="space-y-4">
        <span className="pill-info mono">CompliLeo MVP &middot; demo build</span>
        <h1 className="text-4xl sm:text-5xl font-semibold tracking-tight text-slate-50">
          Regulatory requirements,{' '}
          <span className="text-accent">executable as zero-knowledge proofs</span>.
        </h1>
        <p className="max-w-3xl text-slate-400 text-lg leading-relaxed">
          CompliLeo turns rules from the GENIUS Act, CLARITY Act, and SEC/CFTC
          tokenization frameworks into Aleo programs. Issuers and auditors can
          attest to compliance — token admission, solvency, system health —
          without ever exposing the underlying private data.
        </p>
        <div className="flex flex-wrap gap-3 pt-2">
          <Link to="/demo" className="btn-primary">
            Run the demo →
          </Link>
          <a
            href="https://github.com/Compliledger/CompliLeo"
            target="_blank"
            rel="noreferrer"
            className="btn-secondary"
          >
            View on GitHub
          </a>
        </div>
      </section>

      <section>
        <h2 className="text-xs uppercase tracking-widest text-slate-500 mb-4">
          Proof modules
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {MODULES.map((mod) => (
            <article key={mod} className="card p-5 space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">{MODULE_LABEL[mod]}</h3>
                <span className="pill bg-ink-700/70 text-slate-300 mono">
                  zk
                </span>
              </div>
              <p className="text-sm text-slate-400">{MODULE_TAGLINE[mod]}</p>
              <div className="pt-2 border-t border-ink-700/60 mono text-xs text-slate-500 space-y-0.5">
                <div>
                  <span className="text-slate-600">program: </span>
                  {PROGRAM_BY_MODULE[mod].program_name}
                </div>
                <div>
                  <span className="text-slate-600">transition: </span>
                  {PROGRAM_BY_MODULE[mod].transition_name}
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="card p-6">
        <h2 className="text-xs uppercase tracking-widest text-slate-500 mb-4">
          Execution model
        </h2>
        <ol className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { n: '1', t: 'Private inputs', d: 'Issuer / reserve / monitoring data stays local.' },
            { n: '2', t: 'Leo execution', d: 'Aleo programs run off-chain via snarkVM.' },
            { n: '3', t: 'ZK proof', d: 'Proof + public result are produced.' },
            { n: '4', t: 'Verification', d: 'Validators verify on-chain without seeing inputs.' },
          ].map((s) => (
            <li key={s.n} className="rounded-md border border-ink-700 bg-ink-950/50 p-4">
              <div className="mono text-accent text-xs mb-1">step {s.n}</div>
              <div className="font-medium text-slate-100">{s.t}</div>
              <p className="text-xs text-slate-500 mt-1">{s.d}</p>
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}

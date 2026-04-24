import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import BoolToggle from '../components/BoolToggle';
import DecisionPill from '../components/DecisionPill';
import HashDisplay from '../components/HashDisplay';
import {
  buildCombinedBundle,
  buildProofBundle,
  PROOF_STATUS_SIMULATED,
  VERIFICATION_STATUS_PENDING,
} from '../lib/bundle';
import { demoStore, useDemoState } from '../lib/demoStore';
import {
  evaluateCompliGuard,
  evaluateSolvencyProof,
  evaluateTokenProof,
  MODULE_LABEL,
  ModuleName,
  PROGRAM_BY_MODULE,
} from '../lib/proofs';

type StepId = 0 | 1 | 2 | 3;

const STEPS: { id: StepId; title: string; subtitle: string; module?: ModuleName }[] = [
  {
    id: 0,
    title: 'TokenProof',
    subtitle: 'Token issuance & eligibility',
    module: 'tokenproof',
  },
  {
    id: 1,
    title: 'SolvencyProof',
    subtitle: 'Reserves vs. liabilities',
    module: 'solvencyproof',
  },
  {
    id: 2,
    title: 'CompliGuard',
    subtitle: 'System health monitoring',
    module: 'compliguard',
  },
  { id: 3, title: 'Combined Bundle', subtitle: 'Aggregate proof bundle' },
];

export default function RunDemo() {
  const state = useDemoState();
  const navigate = useNavigate();
  const [step, setStep] = useState<StepId>(0);
  const [busy, setBusy] = useState(false);

  const tokenEval = useMemo(() => evaluateTokenProof(state.tokenInputs), [state.tokenInputs]);
  const solvencyEval = useMemo(
    () => evaluateSolvencyProof(state.solvencyInputs),
    [state.solvencyInputs],
  );
  const compliEval = useMemo(() => evaluateCompliGuard(state.compliInputs), [state.compliInputs]);

  async function generateAndAdvance(module: ModuleName) {
    setBusy(true);
    try {
      const moduleInputs =
        module === 'tokenproof'
          ? { module, inputs: state.tokenInputs }
          : module === 'solvencyproof'
          ? { module, inputs: state.solvencyInputs }
          : { module, inputs: state.compliInputs };
      const bundle = await buildProofBundle(moduleInputs as Parameters<typeof buildProofBundle>[0]);
      demoStore.set((prev) => ({
        ...prev,
        bundles: { ...prev.bundles, [module]: bundle },
      }));
      setStep((prev) => (Math.min(prev + 1, 3) as StepId));
    } finally {
      setBusy(false);
    }
  }

  async function buildCombined() {
    setBusy(true);
    try {
      const ordered = [
        state.bundles.tokenproof,
        state.bundles.solvencyproof,
        state.bundles.compliguard,
      ].filter((b): b is NonNullable<typeof b> => Boolean(b));
      const combined = await buildCombinedBundle(ordered);
      demoStore.set((prev) => ({ ...prev, combined }));
      navigate('/results');
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    demoStore.reset();
    setStep(0);
  }

  return (
    <div className="space-y-8">
      <header className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Run Demo</h1>
          <p className="text-slate-400 mt-1">
            Step through the three CompliLeo proof modules and assemble a combined
            proof bundle.
          </p>
        </div>
        <button onClick={reset} className="btn-secondary">
          Reset
        </button>
      </header>

      <Stepper current={step} bundles={state.bundles} />

      {step === 0 && (
        <StepCard
          stepIndex={0}
          module="tokenproof"
          evaluation={tokenEval}
          onGenerate={() => generateAndAdvance('tokenproof')}
          busy={busy}
          generated={Boolean(state.bundles.tokenproof)}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <BoolToggle
              id="issuer_approved"
              label="issuer_approved"
              hint="Has the issuer been approved by the compliance authority?"
              checked={state.tokenInputs.issuer_approved}
              onChange={(v) =>
                demoStore.set((p) => ({
                  ...p,
                  tokenInputs: { ...p.tokenInputs, issuer_approved: v },
                }))
              }
            />
            <BoolToggle
              id="asset_type_supported"
              label="asset_type_supported"
              hint="Is the asset type supported on the platform?"
              checked={state.tokenInputs.asset_type_supported}
              onChange={(v) =>
                demoStore.set((p) => ({
                  ...p,
                  tokenInputs: { ...p.tokenInputs, asset_type_supported: v },
                }))
              }
            />
          </div>
        </StepCard>
      )}

      {step === 1 && (
        <StepCard
          stepIndex={1}
          module="solvencyproof"
          evaluation={solvencyEval}
          onGenerate={() => generateAndAdvance('solvencyproof')}
          busy={busy}
          generated={Boolean(state.bundles.solvencyproof)}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <NumberField
              id="reserves"
              label="reserves (u64)"
              value={state.solvencyInputs.reserves}
              onChange={(v) =>
                demoStore.set((p) => ({
                  ...p,
                  solvencyInputs: { ...p.solvencyInputs, reserves: v },
                }))
              }
            />
            <NumberField
              id="liabilities"
              label="liabilities (u64)"
              value={state.solvencyInputs.liabilities}
              onChange={(v) =>
                demoStore.set((p) => ({
                  ...p,
                  solvencyInputs: { ...p.solvencyInputs, liabilities: v },
                }))
              }
            />
          </div>
        </StepCard>
      )}

      {step === 2 && (
        <StepCard
          stepIndex={2}
          module="compliguard"
          evaluation={compliEval}
          onGenerate={() => generateAndAdvance('compliguard')}
          busy={busy}
          generated={Boolean(state.bundles.compliguard)}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <BoolToggle
              id="anomaly_score_below_threshold"
              label="anomaly_score_below_threshold"
              hint="Is the anomaly detection score below the configured threshold?"
              checked={state.compliInputs.anomaly_score_below_threshold}
              onChange={(v) =>
                demoStore.set((p) => ({
                  ...p,
                  compliInputs: {
                    ...p.compliInputs,
                    anomaly_score_below_threshold: v,
                  },
                }))
              }
            />
            <BoolToggle
              id="critical_alert_open"
              label="critical_alert_open"
              hint="Is a critical compliance alert currently open?"
              checked={state.compliInputs.critical_alert_open}
              onChange={(v) =>
                demoStore.set((p) => ({
                  ...p,
                  compliInputs: { ...p.compliInputs, critical_alert_open: v },
                }))
              }
            />
          </div>
        </StepCard>
      )}

      {step === 3 && <CombinedStep onBuild={buildCombined} busy={busy} />}

      <div className="flex justify-between pt-2">
        <button
          className="btn-secondary"
          disabled={step === 0 || busy}
          onClick={() => setStep((prev) => (Math.max(prev - 1, 0) as StepId))}
        >
          ← Back
        </button>
        {step < 3 && (
          <button
            className="btn-secondary"
            disabled={busy}
            onClick={() => setStep((prev) => (Math.min(prev + 1, 3) as StepId))}
          >
            Skip →
          </button>
        )}
      </div>
    </div>
  );
}

interface StepperProps {
  current: StepId;
  bundles: ReturnType<typeof useDemoState>['bundles'];
}

function Stepper({ current, bundles }: StepperProps) {
  const generated: Record<number, boolean> = {
    0: Boolean(bundles.tokenproof),
    1: Boolean(bundles.solvencyproof),
    2: Boolean(bundles.compliguard),
    3: false,
  };
  return (
    <ol className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {STEPS.map((s) => {
        const isActive = s.id === current;
        const isDone = generated[s.id];
        return (
          <li
            key={s.id}
            className={[
              'rounded-md border p-3 transition',
              isActive
                ? 'border-accent/60 bg-ink-800/80 shadow-[0_0_0_1px_rgba(56,189,248,0.25)]'
                : 'border-ink-700 bg-ink-900/50',
            ].join(' ')}
          >
            <div className="flex items-center gap-2 mb-1">
              <span
                className={[
                  'mono text-xs px-1.5 py-0.5 rounded',
                  isDone
                    ? 'bg-emerald-500/15 text-emerald-300'
                    : isActive
                    ? 'bg-accent/15 text-accent'
                    : 'bg-ink-700 text-slate-400',
                ].join(' ')}
              >
                {isDone ? '✓' : `0${s.id + 1}`}
              </span>
              <span className="font-medium text-slate-100 text-sm">{s.title}</span>
            </div>
            <p className="text-xs text-slate-500">{s.subtitle}</p>
          </li>
        );
      })}
    </ol>
  );
}

interface StepCardProps {
  stepIndex: number;
  module: ModuleName;
  evaluation: { decision_result: boolean; reason_codes: string[] };
  onGenerate: () => void | Promise<void>;
  busy: boolean;
  generated: boolean;
  children: React.ReactNode;
}

function StepCard({
  stepIndex,
  module,
  evaluation,
  onGenerate,
  busy,
  generated,
  children,
}: StepCardProps) {
  const meta = PROGRAM_BY_MODULE[module];
  return (
    <section className="card p-6 space-y-5">
      <header className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="mono text-xs text-accent mb-1">
            step 0{stepIndex + 1} / 04
          </div>
          <h2 className="text-2xl font-semibold">{MODULE_LABEL[module]}</h2>
          <p className="mono text-xs text-slate-500 mt-0.5">
            {meta.program_name} :: {meta.transition_name}
          </p>
        </div>
        <DecisionPill ok={evaluation.decision_result} />
      </header>

      <div>
        <span className="label">Private inputs</span>
        <div className="mt-2">{children}</div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <span className="label">Predicted public result</span>
          <p className="mono mt-1.5 rounded-md border border-ink-700 bg-ink-950/60 p-3 text-slate-100">
            {evaluation.decision_result ? 'TRUE' : 'FALSE'}
          </p>
        </div>
        <div>
          <span className="label">Reason codes</span>
          <ul className="mt-1.5 flex flex-wrap gap-1.5">
            {evaluation.reason_codes.map((code) => (
              <li key={code} className="pill bg-ink-700/70 text-slate-200 mono">
                {code}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="flex items-center justify-end gap-3 pt-2 border-t border-ink-700/60">
        {generated && (
          <span className="pill-ok mono">bundle generated</span>
        )}
        <button onClick={onGenerate} className="btn-primary" disabled={busy}>
          {busy ? 'Generating…' : generated ? 'Regenerate & continue' : 'Generate proof bundle'}
        </button>
      </div>
    </section>
  );
}

function CombinedStep({ onBuild, busy }: { onBuild: () => void; busy: boolean }) {
  const state = useDemoState();
  const ready = Boolean(
    state.bundles.tokenproof && state.bundles.solvencyproof && state.bundles.compliguard,
  );

  return (
    <section className="card p-6 space-y-5">
      <header>
        <div className="mono text-xs text-accent mb-1">step 04 / 04</div>
        <h2 className="text-2xl font-semibold">Combined Proof Bundle</h2>
        <p className="text-slate-400 text-sm mt-1">
          Aggregate the three module bundles into a single hash-anchored bundle
          that can be submitted for Aleo verification.
        </p>
      </header>

      <div className="space-y-3">
        {(['tokenproof', 'solvencyproof', 'compliguard'] as ModuleName[]).map((mod) => {
          const b = state.bundles[mod];
          return (
            <div
              key={mod}
              className="flex items-center justify-between gap-3 rounded-md border border-ink-700 bg-ink-950/50 p-3"
            >
              <div className="min-w-0">
                <div className="font-medium text-slate-100">{MODULE_LABEL[mod]}</div>
                <div className="mono text-xs text-slate-500 truncate">
                  {b ? b.bundle_hash : 'not yet generated'}
                </div>
              </div>
              {b ? (
                <DecisionPill ok={b.decision_result} />
              ) : (
                <span className="pill-pending mono">pending</span>
              )}
            </div>
          );
        })}
      </div>

      <div className="rounded-md border border-ink-700 bg-ink-950/50 p-4 grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div>
          <span className="label">proof_status</span>
          <div className="mt-1">
            <span className="pill-pending mono">{PROOF_STATUS_SIMULATED}</span>
          </div>
        </div>
        <div>
          <span className="label">verification_status</span>
          <div className="mt-1">
            <span className="pill-pending mono">{VERIFICATION_STATUS_PENDING}</span>
          </div>
        </div>
      </div>

      {state.combined && (
        <HashDisplay
          hash={state.combined.combined_hash}
          label="combined_hash (sha-256)"
        />
      )}

      <div className="flex items-center justify-end gap-3 pt-2 border-t border-ink-700/60">
        <button
          onClick={onBuild}
          className="btn-primary"
          disabled={!ready || busy}
        >
          {busy ? 'Building…' : 'Build combined bundle & view results'}
        </button>
      </div>

      {!ready && (
        <p className="text-xs text-amber-300/90">
          Generate all three module bundles before building the combined bundle.
        </p>
      )}
    </section>
  );
}

interface NumberFieldProps {
  id: string;
  label: string;
  value: number;
  onChange: (v: number) => void;
}

function NumberField({ id, label, value, onChange }: NumberFieldProps) {
  return (
    <div>
      <label htmlFor={id} className="label">
        {label}
      </label>
      <input
        id={id}
        type="number"
        min={0}
        step={1}
        value={Number.isFinite(value) ? value : 0}
        onChange={(e) => {
          const n = Number(e.target.value);
          onChange(Number.isFinite(n) && n >= 0 ? Math.floor(n) : 0);
        }}
        className="input mono mt-1.5"
      />
    </div>
  );
}

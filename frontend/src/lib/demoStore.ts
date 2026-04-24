// Minimal in-memory store for demo state shared between Run Demo and
// Proof Bundle Results pages. Avoids pulling in a state-management library
// for a 3-page MVP.
import { useSyncExternalStore } from 'react';
import {
  CompliGuardInputs,
  SolvencyProofInputs,
  TokenProofInputs,
} from './proofs';
import { CombinedBundle, ProofBundle } from './bundle';

export interface DemoSnapshot {
  tokenInputs: TokenProofInputs;
  solvencyInputs: SolvencyProofInputs;
  compliInputs: CompliGuardInputs;
  bundles: {
    tokenproof?: ProofBundle;
    solvencyproof?: ProofBundle;
    compliguard?: ProofBundle;
  };
  combined?: CombinedBundle;
}

const DEFAULT: DemoSnapshot = {
  tokenInputs: { issuer_approved: true, asset_type_supported: true },
  solvencyInputs: { reserves: 1_000_000, liabilities: 750_000 },
  compliInputs: {
    anomaly_score_below_threshold: true,
    critical_alert_open: false,
  },
  bundles: {},
  combined: undefined,
};

let state: DemoSnapshot = DEFAULT;
const listeners = new Set<() => void>();

function emit() {
  listeners.forEach((l) => l());
}

export const demoStore = {
  get(): DemoSnapshot {
    return state;
  },
  set(updater: (prev: DemoSnapshot) => DemoSnapshot) {
    state = updater(state);
    emit();
  },
  reset() {
    state = { ...DEFAULT, bundles: {}, combined: undefined };
    emit();
  },
  subscribe(listener: () => void) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  },
};

export function useDemoState(): DemoSnapshot {
  return useSyncExternalStore(demoStore.subscribe, demoStore.get, demoStore.get);
}

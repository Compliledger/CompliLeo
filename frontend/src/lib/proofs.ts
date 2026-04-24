// Domain types and pure evaluation logic for the CompliLeo MVP frontend.
// These mirror the backend services in `backend/app/services/*` and the
// Aleo program metadata in `backend/app/services/aleo_adapter.py`, so the
// demo can run standalone without a backend.

export type ModuleName = 'tokenproof' | 'solvencyproof' | 'compliguard';

export interface TokenProofInputs {
  issuer_approved: boolean;
  asset_type_supported: boolean;
}

export interface SolvencyProofInputs {
  reserves: number;
  liabilities: number;
}

export interface CompliGuardInputs {
  anomaly_score_below_threshold: boolean;
  critical_alert_open: boolean;
}

export type ModuleInputs =
  | { module: 'tokenproof'; inputs: TokenProofInputs }
  | { module: 'solvencyproof'; inputs: SolvencyProofInputs }
  | { module: 'compliguard'; inputs: CompliGuardInputs };

export interface EvaluationResult {
  decision_result: boolean;
  reason_codes: string[];
}

export interface ProgramMetadata {
  program_name: string;
  transition_name: string;
}

export const PROGRAM_BY_MODULE: Record<ModuleName, ProgramMetadata> = {
  tokenproof: {
    program_name: 'tokenproofx1.aleo',
    transition_name: 'check_token_admission',
  },
  solvencyproof: {
    program_name: 'solvencypx1.aleo',
    transition_name: 'check_solvency',
  },
  compliguard: {
    program_name: 'compliguardx1.aleo',
    transition_name: 'check_system_health',
  },
};

export const MODULE_LABEL: Record<ModuleName, string> = {
  tokenproof: 'TokenProof',
  solvencyproof: 'SolvencyProof',
  compliguard: 'CompliGuard',
};

export const MODULE_TAGLINE: Record<ModuleName, string> = {
  tokenproof: 'Token issuance & eligibility admission',
  solvencyproof: 'Reserves vs. liabilities attestation',
  compliguard: 'System health & anomaly monitoring',
};

// ----- Pure evaluators (mirror backend/app/services/*_service.py) ----------

export function evaluateTokenProof(inputs: TokenProofInputs): EvaluationResult {
  const reasons: string[] = [];
  if (!inputs.issuer_approved) reasons.push('ISSUER_NOT_APPROVED');
  if (!inputs.asset_type_supported) reasons.push('ASSET_TYPE_UNSUPPORTED');
  const valid = inputs.issuer_approved && inputs.asset_type_supported;
  if (valid) reasons.push('TOKEN_ELIGIBLE');
  return { decision_result: valid, reason_codes: reasons };
}

export function evaluateSolvencyProof(inputs: SolvencyProofInputs): EvaluationResult {
  const reasons: string[] = [];
  const solvent = inputs.reserves >= inputs.liabilities;
  reasons.push(solvent ? 'RESERVES_SUFFICIENT' : 'RESERVES_INSUFFICIENT');
  return { decision_result: solvent, reason_codes: reasons };
}

export function evaluateCompliGuard(inputs: CompliGuardInputs): EvaluationResult {
  const reasons: string[] = [];
  if (!inputs.anomaly_score_below_threshold) reasons.push('ANOMALY_SCORE_ABOVE_THRESHOLD');
  if (inputs.critical_alert_open) reasons.push('CRITICAL_ALERT_OPEN');
  const healthy = inputs.anomaly_score_below_threshold && !inputs.critical_alert_open;
  if (healthy) reasons.push('SYSTEM_HEALTHY');
  return { decision_result: healthy, reason_codes: reasons };
}

export function evaluate(module: ModuleInputs): EvaluationResult {
  switch (module.module) {
    case 'tokenproof':
      return evaluateTokenProof(module.inputs);
    case 'solvencyproof':
      return evaluateSolvencyProof(module.inputs);
    case 'compliguard':
      return evaluateCompliGuard(module.inputs);
  }
}

// ----- Public-result formatting -------------------------------------------

export function publicResultText(module: ModuleName, ok: boolean): string {
  switch (module) {
    case 'tokenproof':
      return ok ? 'Token Valid: TRUE' : 'Token Valid: FALSE';
    case 'solvencyproof':
      return ok ? 'Solvent: TRUE' : 'Solvent: FALSE';
    case 'compliguard':
      return ok ? 'System Healthy: TRUE' : 'System Healthy: FALSE';
  }
}

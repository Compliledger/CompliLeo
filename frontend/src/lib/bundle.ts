// Deterministic proof bundle construction. Mirrors the layout produced by
// `backend/app/services/proof_bundle_service.py`: a canonical-JSON SHA-256
// over all body fields, with placeholder Aleo proof / verification status.

import {
  evaluate,
  MODULE_LABEL,
  ModuleInputs,
  ModuleName,
  PROGRAM_BY_MODULE,
  publicResultText,
} from './proofs';

export const PROOF_STATUS_SIMULATED = 'simulated';
export const VERIFICATION_STATUS_PENDING = 'pending_aleo_execution';
const INPUT_COMMITMENT_PLACEHOLDER = 'placeholder_input_commitment';

export interface ProofBundle {
  module: ModuleName;
  module_label: string;
  decision_result: boolean;
  public_result: string;
  reason_codes: string[];
  timestamp: string;
  input_commitment: string;
  aleo_program: string;
  transition_name: string;
  proof_status: string;
  verification_status: string;
  bundle_hash: string;
}

export interface CombinedBundle {
  bundles: ProofBundle[];
  decision_result: boolean;
  timestamp: string;
  combined_hash: string;
  proof_status: string;
  verification_status: string;
}

// Canonical JSON: sorted keys, no whitespace. Matches Python's
// json.dumps(..., sort_keys=True, separators=(",", ":"))
function canonicalJson(value: unknown): string {
  if (value === null || typeof value !== 'object') {
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return '[' + value.map(canonicalJson).join(',') + ']';
  }
  const obj = value as Record<string, unknown>;
  const keys = Object.keys(obj).sort();
  return (
    '{' +
    keys
      .map((k) => JSON.stringify(k) + ':' + canonicalJson(obj[k]))
      .join(',') +
    '}'
  );
}

async function sha256Hex(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(digest))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('');
}

export async function buildProofBundle(
  module: ModuleInputs,
  options: { timestamp?: string } = {},
): Promise<ProofBundle> {
  const { decision_result, reason_codes } = evaluate(module);
  const meta = PROGRAM_BY_MODULE[module.module];
  const ts = options.timestamp ?? new Date().toISOString();

  const body = {
    module: module.module,
    decision_result,
    reason_codes: [...reason_codes],
    timestamp: ts,
    input_commitment: INPUT_COMMITMENT_PLACEHOLDER,
    aleo_program: meta.program_name,
    transition_name: meta.transition_name,
    proof_status: PROOF_STATUS_SIMULATED,
    verification_status: VERIFICATION_STATUS_PENDING,
  };

  const bundle_hash = await sha256Hex(canonicalJson(body));

  return {
    ...body,
    module_label: MODULE_LABEL[module.module],
    public_result: publicResultText(module.module, decision_result),
    bundle_hash,
  };
}

export async function buildCombinedBundle(
  bundles: ProofBundle[],
  options: { timestamp?: string } = {},
): Promise<CombinedBundle> {
  const ts = options.timestamp ?? new Date().toISOString();
  const decision_result = bundles.every((b) => b.decision_result);
  const body = {
    bundle_hashes: bundles.map((b) => b.bundle_hash),
    modules: bundles.map((b) => b.module),
    decision_result,
    timestamp: ts,
    proof_status: PROOF_STATUS_SIMULATED,
    verification_status: VERIFICATION_STATUS_PENDING,
  };
  const combined_hash = await sha256Hex(canonicalJson(body));
  return {
    bundles,
    decision_result,
    timestamp: ts,
    combined_hash,
    proof_status: PROOF_STATUS_SIMULATED,
    verification_status: VERIFICATION_STATUS_PENDING,
  };
}

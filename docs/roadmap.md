# CompliLeo Roadmap

CompliLeo is intentionally scoped as a minimal proof-of-concept.
Subsequent phases progressively connect it to the real Aleo network.

## Phase 1–6 (delivered)

* Three minimal Leo programs (`tokenproofx1`, `solvencypx1`,
  `compliguardx1`).
* FastAPI backend with proof-evaluation and proof-bundle endpoints.
* Aleo program registry + simulated Aleo adapter.
* React + Vite demo frontend.
* Demo documentation.

## Phase 7 — Real Aleo Execution Path *(this phase)*

The backend gains a pluggable execution seam selected by the
`ALEO_EXECUTION_MODE` environment variable:

* **`simulated`** *(default)* — placeholder metadata only. No Leo
  toolchain is required. Safe for CI and laptop development.
* **`local_cli`** — the new
  `backend/app/services/aleo_execution_adapter.py` resolves the
  on-disk Leo program from the program registry and invokes the local
  `leo` CLI (`leo execute` / `leo run`) via `subprocess`. Captured
  output is parsed and returned as structured metadata in the
  `local_execution_result` field of every proof response.

Privacy is preserved end-to-end: private inputs are never logged and
never echoed in responses (`inputs_redacted=True`).

### Future — Testnet mode

A future phase will add an `ALEO_EXECUTION_MODE=testnet` mode that:

1. Generates a real zero-knowledge proof using the local Leo
   toolchain.
2. Signs and submits the resulting transition to the Aleo network
   using `ALEO_PRIVATE_KEY` / `ALEO_ACCOUNT_ADDRESS` from the
   environment.
3. Returns the on-chain transaction id as the `proof_reference` and
   updates `verification_status` based on validator confirmation.

> ⚠️ **No real financial data should be used in this MVP.** The
> programs and the local CLI path are intended for demonstration only;
> network submission must wait for the testnet phase and a full
> security review of the integration.

## Beyond Phase 7

* Expanded regulatory mappings (GENIUS, CLARITY, SEC/CFTC).
* Richer proof composition across modules.
* Selective disclosure / verifiable credentials.
* Integration with stablecoin and payment systems.
* Full CompliStack architecture.
# CompliLeo — Roadmap

> Multi-phase plan for evolving CompliLeo from a simulated MVP into a
> production-grade ZK proof execution layer for regulated tokenized
> markets. Time / effort estimates are intentionally not included.

---

## Phase 1 — MVP Sliver *(current)*

The grant/demo sliver shipped in this repository.

- Three Leo programs in `aleo/`:
  - `tokenproofx1.aleo :: verify_token`
  - `solvencypx1.aleo :: prove_solvency`
  - `compliguardx1.aleo :: prove_health`
- FastAPI backend with proof evaluators, deterministic proof-bundle
  builder (canonical-JSON SHA-256), and an Aleo program registry
  exposed over HTTP.
- React / Vite / Tailwind demo frontend with a 4-step wizard
  (TokenProof → SolvencyProof → CompliGuard → Combined bundle).
- Aleo adapter prepares typed Leo inputs and returns a **simulated**
  proof status (`proof_status: "simulated"`,
  `verification_status: "pending_aleo_execution"`).
- Documentation: `README.md`, `demo-notes.md`, `architecture.md`, and
  this `docs/` directory.

**Exit criteria.** End-to-end demo runnable from frontend, backend, or
Leo CLI; deterministic proof bundles reproducible by any consumer.

---

## Phase 2 — Real Leo Execution

Replace the simulated execution path with real Leo program execution
driven from the backend Aleo adapter.

- Use each program's `local_path` from the registry to load and (where
  needed) compile the Leo program.
- Invoke the named transition (`verify_token`, `prove_solvency`,
  `prove_health`) via `leo execute` / `snarkVM` / `snarkOS` against a
  local runner using the typed inputs already prepared by
  `aleo_adapter.prepare_*_input`.
- Return the real proof artifact and public output to the bundle
  layer; populate `input_commitment` from the real execution.
- Keep the HTTP API surface, bundle layout, and frontend untouched.

**Exit criteria.** A real Aleo proof is produced for each of the three
modules from a backend call, with the same deterministic bundle hash
behavior as today.

---

## Phase 3 — Aleo Testnet Proof Verification

Take the proofs produced in Phase 2 to the Aleo testnet for real
network verification.

- Submit each transition to Aleo testnet (or verify against testnet
  validators where appropriate).
- Replace placeholder `verification_status` with values derived from
  testnet verification.
- Capture testnet transaction / verification identifiers in the proof
  bundle so consumers can independently re-verify.
- Add a thin status-reconciliation path (frontend + backend) to surface
  verification state to demo users.

**Exit criteria.** The CompliLeo demo runs against Aleo testnet with
real proofs and real verification status, end-to-end, for all three
modules.

---

## Phase 4 — Stablecoin Issuer Pilot

Move from a self-contained demo to a structured pilot with a regulated
private stablecoin issuer.

- Define a recurring proof cadence (e.g. SolvencyProof every reporting
  window, CompliGuard continuously) with the pilot partner.
- Wire the issuer's existing systems to feed typed private inputs into
  the backend (without disclosing them in cleartext to CompliLeo).
- Deliver hash-anchored proof bundles + Aleo verification artifacts to
  the pilot partner's auditors / counterparties / internal regulators.
- Capture pilot feedback into the regulatory mapping and Leo programs.

**Exit criteria.** A regulated private stablecoin issuer runs CompliLeo
on real internal data on a recurring schedule and consumes the public
proof bundles in their compliance workflow.

---

## Phase 5 — Expanded CompliStack Modules

Grow beyond the three MVP primitives into the broader CompliStack
module catalog for regulated tokenized markets.

- Add new ZK proof modules covering additional regulatory primitives
  (e.g. transaction-level eligibility, sanctions-list non-membership,
  regulatory-reporting attestations, custody attestations).
- Introduce richer rule shapes (thresholds, composite conditions,
  weighted scores) where the boolean form is no longer expressive
  enough.
- Introduce composability: aggregate multiple module proofs into a
  single Aleo proof where the regulatory question demands it.
- Selective-disclosure / verifiable-credential flows so consumers can
  re-use proof results across systems.
- Open the registry pattern up so partner programs can be plugged in
  without changing the orchestration layer.

**Exit criteria.** CompliLeo serves as the ZK execution layer for a
multi-module CompliStack covering the full regulated tokenized-market
lifecycle.

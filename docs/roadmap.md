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

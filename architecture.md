# CompliLeo Architecture

CompliLeo is a proof-orchestration MVP that turns regulatory
requirements into executable zero-knowledge proof programs on Aleo.
This document describes the high-level architecture and the pluggable
seam that connects the backend to real Aleo execution.

## Components

| Component | Responsibility |
|---|---|
| `frontend/` | React + Vite demo UI. Walks a user through the three proofs and renders the proof bundle. |
| `backend/app/main.py` | FastAPI entrypoint. Mounts the proof, proof-bundle, and Aleo program-registry routers. |
| `backend/app/services/tokenproof_service.py`, `solvencyproof_service.py`, `compliguard_service.py` | Pure Python evaluators. Encode the regulatory rule for each proof module. |
| `backend/app/services/aleo_program_registry.py` | Single source of truth for every local Leo program (name, transition, on-disk path). |
| `backend/app/services/aleo_adapter.py` | Public adapter consumed by the routers and the proof-bundle service. Produces `aleo` metadata for every response. |
| `backend/app/services/aleo_execution_adapter.py` | Mode-aware execution shim. Either returns simulated metadata or shells out to the local Leo CLI. |
| `backend/app/services/proof_bundle_service.py` | Builds a deterministic, hash-anchored bundle for the cross-module proof view. |
| `aleo/` | Three minimal Leo programs (`tokenproofx1`, `solvencypx1`, `compliguardx1`). |

## Request flow

```
HTTP request
   │
   ▼
FastAPI router  ──►  *_service.evaluate()        (decision + reason codes)
   │
   ├──►  aleo_adapter.build_proof_metadata()
   │           │
   │           ├── execution_mode == "simulated"   → placeholder metadata
   │           └── execution_mode == "local_cli"   → aleo_execution_adapter.execute()
   │                                                   └── subprocess → leo CLI
   ▼
Response (decision + `aleo` metadata block)
```

## Real Aleo Execution Path

The backend exposes a single environment-driven seam,
`ALEO_EXECUTION_MODE`, which selects how proofs are produced:

* **`simulated`** *(default)* — `aleo_adapter` returns placeholder
  proof metadata. No Leo toolchain is required. This is the default
  for CI and local development.
* **`local_cli`** — `aleo_execution_adapter` resolves the on-disk Leo
  program from `aleo_program_registry` and shells out to `leo execute`
  (or `leo run` on older toolchains) for each transition. The captured
  stdout, parsed result, and structured execution status are returned
  in the `local_execution_result` field of the response.
* **`testnet`** *(future, not implemented)* — will submit generated
  proofs to the Aleo network for verification using
  `ALEO_PRIVATE_KEY` / `ALEO_ACCOUNT_ADDRESS` from the environment.

### Privacy guarantees

Private inputs are **never** logged and **never** echoed in API
responses. The `inputs_redacted` flag inside `local_execution_result`
makes this contract explicit — only the *names* of the inputs are
recorded, never their values.

> ⚠️ **No real financial data should be used in this MVP.** The
> programs and the local CLI path are intended for demonstration only.

See `.env.example` for all configurable variables and `docs/roadmap.md`
for the planned progression toward full testnet execution.

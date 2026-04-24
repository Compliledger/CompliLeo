# CompliLeo — Technical Architecture

> The technical architecture, execution model, backend orchestration, and
> Aleo adapter design for the CompliLeo MVP, plus the path to real Aleo
> execution / testnet verification.

CompliLeo is a **ZK proof execution layer for regulated private financial
systems**. This document describes how its pieces fit together.

---

## Architecture Diagram

```mermaid
flowchart TD
    subgraph Consumers["Verification Consumers"]
        ISSUER[Stablecoin / token issuer]
        AUDITOR[Auditor / regulator]
        COUNTERPARTY[Counterparty / application]
    end

    subgraph Frontend["Frontend (React / Vite / Tailwind)"]
        UI[Demo wizard\nTokenProof → SolvencyProof → CompliGuard → Bundle]
    end

    subgraph Backend["Backend (FastAPI orchestration)"]
        API[HTTP API\n/api/tokenproof/evaluate\n/api/solvencyproof/evaluate\n/api/compliguard/evaluate\n/api/proof-bundle/create\n/api/aleo/programs]
        SVC[Proof evaluators\n(pure boolean logic mirroring Leo)]
        BUNDLE[Proof-bundle builder\n(canonical-JSON SHA-256)]
        ADAPTER[Aleo adapter\nprepare_*_input + simulated proof status]
        REGISTRY[(Aleo program registry\naleo_program_registry.py)]
    end

    subgraph Aleo["Aleo Programs (Leo source in aleo/)"]
        TP[tokenproofx1.aleo\n:: verify_token]
        SP[solvencypx1.aleo\n:: prove_solvency]
        CG[compliguardx1.aleo\n:: prove_health]
    end

    subgraph Network["Aleo Network Verification\n(future phase — real execution)"]
        EXEC[snarkVM / snarkOS execution]
        VERIFY[Validator verification of ZK proof]
    end

    UI -->|private inputs| API
    API --> SVC
    API --> BUNDLE
    API --> ADAPTER
    ADAPTER --> REGISTRY
    BUNDLE --> REGISTRY
    REGISTRY -. names + local_path .-> TP
    REGISTRY -. names + local_path .-> SP
    REGISTRY -. names + local_path .-> CG
    ADAPTER -. today: simulated .-> Network
    ADAPTER ==>|future phase| EXEC
    EXEC --> VERIFY
    VERIFY --> Consumers
    BUNDLE -->|public proof bundle| Consumers
```

A simpler text view of the same picture:

```
Private Inputs
        │
        ▼
Frontend (React / Vite / Tailwind)
        │
        ▼
Backend (FastAPI)
  ├─ Proof evaluators
  ├─ Proof-bundle builder (deterministic SHA-256)
  └─ Aleo adapter ──► Aleo program registry
                                │
                                ▼
                  CompliLeo Leo Programs (aleo/)
                  - tokenproofx1.aleo  :: verify_token
                  - solvencypx1.aleo   :: prove_solvency
                  - compliguardx1.aleo :: prove_health
                                │
                                ▼ (today: simulated; next: real)
                  Aleo ZK Execution (snarkVM)
                                │
                                ▼
                  Aleo Network Verification
                                │
                                ▼
                  Verification Consumers
                  (issuer, auditor / regulator, counterparty)
```

---

## Execution Model

CompliLeo follows the canonical Aleo execution shape:

```
Private Inputs
   → CompliLeo Leo Programs
       → Aleo ZK Execution
           → Aleo Network Verification
               → Verification Consumers
```

| Stage | What happens | Today | Future |
|---|---|---|---|
| **Private Inputs** | Issuer / system supplies the typed private values for one CompliLeo proof (`bool`, `u64`). | Collected via the React demo or HTTP API. | Same shape, supplied by issuer systems. |
| **CompliLeo Leo Programs** | The relevant Leo program (`tokenproofx1.aleo`, `solvencypx1.aleo`, `compliguardx1.aleo`) encodes the rule. | Source lives in `aleo/`; runs locally with `leo run`. | Same source, compiled and executed end-to-end. |
| **Aleo ZK Execution** | snarkVM executes the transition over private inputs and produces a proof + public output. | Simulated by the backend's Aleo adapter — boolean logic mirrors the Leo program; `proof_status: "simulated"`. | Real snarkVM/`leo`/`snarkOS` execution invoked from the adapter. |
| **Aleo Network Verification** | Validators verify the proof; the public output becomes observable. | `verification_status: "pending_aleo_execution"` placeholder. | Real on-chain (or off-chain) verification status returned from the network. |
| **Verification Consumers** | Issuers, auditors, regulators, and counterparties consume the public proof result + bundle hash. | Consume the deterministic proof bundle from the backend. | Same bundle, now anchored by a real Aleo proof. |

The point of the model is the **separation between private inputs and
public proof result**. Inputs never leave the prover. The result is
public, verifiable, and repeatable.

---

## Backend Orchestration

The FastAPI backend (`backend/app/`) is small on purpose. It has four
responsibilities:

1. **Validate typed inputs** for each CompliLeo module via Pydantic
   models in `app/models.py`.
2. **Evaluate the rule** with a pure Python function that mirrors the
   Leo program one-for-one (`app/services/*_service.py`). Mirroring is
   deliberate: the same boolean logic exists in two places — Leo for
   ZK execution, Python for orchestration — and keeping them aligned
   is part of the demo contract.
3. **Build the proof bundle** in `app/services/proof_bundle_service.py`.
   The bundle records the module, public decision, reason codes, a
   timestamp, the Aleo program + transition that *would* attest to the
   decision, and a deterministic `bundle_hash` computed as `SHA-256`
   over the canonical JSON of all other fields (sorted keys, no
   whitespace).
4. **Expose the Aleo program registry** via
   `GET /api/aleo/programs` and `GET /api/aleo/programs/{module}` so
   any consumer can introspect the wiring.

The backend deliberately does **not** include a database, auth,
external integrations, or any AI/ML component. Everything is
deterministic and reproducible from inputs alone.

---

## Aleo Adapter

[`backend/app/services/aleo_adapter.py`](./backend/app/services/aleo_adapter.py)
is the seam between orchestration and ZK execution.

It exposes:

- `prepare_tokenproof_input(req) -> dict` → typed Leo args for
  `tokenproofx1.aleo :: verify_token`
- `prepare_solvencyproof_input(req) -> dict` → typed Leo args for
  `solvencypx1.aleo :: prove_solvency` (with `u64` suffixing)
- `prepare_compliguard_input(req) -> dict` → typed Leo args for
  `compliguardx1.aleo :: prove_health`
- A simulated proof-status producer used to stamp the proof bundle.

It reads program names, transitions, and local source paths from
`aleo_program_registry.py`. **Nothing in the codebase hardcodes a
program name outside the registry.** That is the property that lets
real Aleo execution slot in without touching any other layer.

Today the adapter:

- Returns `proof_status: "simulated"` and
  `verification_status: "pending_aleo_execution"`.
- Does not call the Aleo network, does not load `snarkVM`, does not
  sign anything with a wallet.

Tomorrow the adapter:

- Loads each Leo program from `local_path`.
- Invokes the named transition with the prepared typed inputs.
- Returns the real proof status, on-chain verification status, and
  input commitment, all in the same field positions the bundle layout
  already exposes.

---

## Future Real-Execution Path

The next phase is real Aleo execution and testnet verification. The
work decomposes into three concrete steps, each isolated to the
adapter layer:

1. **Leo program loading.** Use the registry's `local_path` (or
   compiled artifact path) to load each program. No new program
   identifiers — the names already match `program.json` and the
   `program <name>` declaration in `main.leo`.
2. **Real transition execution.** Invoke `verify_token`,
   `prove_solvency`, and `prove_health` via `leo execute` /
   `snarkOS` / `snarkVM` against the Aleo testnet (or a local
   runner) using the typed inputs already prepared by
   `prepare_*_input`. Capture the resulting proof and public output.
3. **Real verification status.** Replace the placeholder
   `proof_status`, `verification_status`, and `input_commitment`
   fields in the proof bundle with values derived from real proof
   generation and verification. The bundle layout, hashing scheme,
   and HTTP API surface stay identical.

The roadmap for that work — including the stablecoin issuer pilot
that follows it — is in [`docs/roadmap.md`](./docs/roadmap.md).

---

## Why This Shape

Three properties drove the architecture:

- **A small, obvious seam to real Aleo execution.** The adapter
  pattern + registry means the future work is concentrated in one
  module.
- **Deterministic, hash-anchored proof bundles.** Any consumer can
  recompute `bundle_hash` from the public payload, today and after
  real Aleo execution lands.
- **Verification without disclosure.** Public results, private
  inputs — the same shape the Aleo execution model gives natively.

Together, those make CompliLeo a credible ZK proof execution layer
for regulated private financial verification, ready to be promoted
from a simulated MVP to a real-execution implementation without
re-architecting anything above the adapter line.

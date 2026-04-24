# CompliLeo

> **CompliLeo turns regulatory requirements from the GENIUS Act, the
> CLARITY Act, and the SEC/CFTC tokenization framework into executable
> zero-knowledge proof programs on Aleo.**

CompliLeo is a minimal MVP that demonstrates how compliance logic for
regulated tokenized markets can be expressed as **ZK proof programs**
written in [Leo](https://leo-lang.org/) and executed on the
[Aleo network](https://aleo.org/), so that regulated private stablecoin
and tokenized-asset systems can prove the conditions a regulator cares
about **without disclosing the underlying private financial data**.

This repository is a grant/demo sliver of the broader CompliStack vision —
not the full platform.

---

## What CompliLeo Is

CompliLeo is a **ZK proof execution layer for regulated private financial
systems**. It is *not*:

- an AI auditor,
- a blockchain analytics tool,
- a surveillance product, or
- a wallet / payment rail.

It is a small set of Leo programs, an orchestration backend, and a demo
frontend that together show how a regulated issuer or platform can answer
questions like:

- *"Is this tokenized asset eligible to enter our system?"*
- *"Are reserves sufficient to cover liabilities right now?"*
- *"Is the compliance system itself operating within healthy bounds?"*

…with a **public proof result** (true / false) backed by **private inputs**
that never leave the prover.

---

## Why Regulation Is the Driver

Regulated tokenized markets are converging on three requirements:

1. **Verifiability** — issuers, platforms, and counterparties must be
   able to demonstrate compliance to regulators and to each other.
2. **Privacy** — reserves, customer balances, internal risk telemetry,
   and counterparty exposures cannot be broadcast in cleartext.
3. **Continuity** — checks must be repeatable on a recurring basis, not
   just at one-off audit time.

Traditional disclosure-based compliance breaks at least one of those.
**Zero-knowledge proofs** satisfy all three: a proof can be verified by
anyone, the inputs stay private, and the same program can be run again
every block, every day, every reporting period.

CompliLeo encodes that pattern for three regulatory primitives drawn
from current U.S. digital asset frameworks.

---

## GENIUS / CLARITY / SEC-CFTC Alignment

| Framework | What it requires | CompliLeo program |
|---|---|---|
| **GENIUS Act** (stablecoins) | Approved issuers, adequate reserve backing of outstanding liabilities | **SolvencyProof** — proves `reserves >= liabilities` without revealing either figure |
| **CLARITY Act** (digital asset market structure) | Asset classification and supported-asset gating before admission | **TokenProof** — proves an asset's issuer is approved and its asset type is supported |
| **SEC / CFTC tokenization framework** | Operational integrity and ongoing monitoring of the tokenized-market lifecycle | **CompliGuard** — proves the compliance system is healthy (anomaly score within bounds, no critical alert open) |

A full mapping is in [`docs/regulatory-mapping.md`](./docs/regulatory-mapping.md).
This is a high-level engineering mapping, not legal advice.

---

## How the MVP Works

The MVP has three layers that line up end-to-end:

```
Frontend (React / Vite / Tailwind)
        │
        ▼
Backend (FastAPI orchestration + Aleo adapter)
        │
        ▼
Aleo Programs (Leo source in aleo/)
        │
        ▼  (today: simulated;  next: real Aleo execution + testnet verification)
Aleo Network Verification
```

For each proof module the flow is the same:

1. The user enters **private inputs** in the frontend (or via the API).
2. The backend evaluates the same boolean rule that the Leo program
   encodes and returns a **public proof result** plus reason codes.
3. The backend builds a **deterministic proof bundle** (canonical-JSON
   SHA-256 hash) stamped with the Aleo program name and transition that
   *would* attest to the result.
4. The backend's **Aleo adapter** prepares typed Leo inputs and currently
   returns a `simulated` proof status. This is the seam where real Aleo
   execution will plug in.

A full per-step demo script is in [`demo-notes.md`](./demo-notes.md), and
the architecture and execution model are in
[`architecture.md`](./architecture.md).

---

## Backend Architecture

The FastAPI service in [`backend/`](./backend/) exposes proof-evaluation
endpoints, a deterministic proof-bundle builder, and a read API over the
Aleo program registry.

| Method | Path | Purpose |
|---|---|---|
| `GET`  | `/health` | Liveness probe |
| `POST` | `/api/tokenproof/evaluate` | Evaluate token admission |
| `POST` | `/api/solvencyproof/evaluate` | Evaluate reserve adequacy |
| `POST` | `/api/compliguard/evaluate` | Evaluate system health |
| `POST` | `/api/proof-bundle/create` | Build a hash-anchored proof bundle |
| `GET`  | `/api/aleo/programs` | List registered Aleo programs |
| `GET`  | `/api/aleo/programs/{module}` | Get one program's metadata |

Key design points:

- **Single source of truth** for Aleo programs:
  [`backend/app/services/aleo_program_registry.py`](./backend/app/services/aleo_program_registry.py)
  records each program's name, transition, local Leo source path, and
  description. Nothing in the codebase hardcodes a program name outside
  the registry.
- **Aleo adapter**:
  [`backend/app/services/aleo_adapter.py`](./backend/app/services/aleo_adapter.py)
  reads the registry and exposes `prepare_*_input(...)` helpers that
  format typed Leo inputs (`bool`, `u64`). Today the adapter returns a
  simulated proof status; tomorrow the same surface will drive real
  execution.
- **Deterministic bundles**: `bundle_hash` is `SHA-256` over
  canonical JSON (sorted keys, no whitespace) of the bundle payload, so
  any client can independently reproduce the same hash for the same
  logical bundle.

See [`backend/README.md`](./backend/README.md) for endpoint examples and
local-dev instructions.

---

## Aleo Program Architecture

The [`aleo/`](./aleo/) directory contains three intentionally-tiny Leo
programs. Each one encodes one CompliLeo proof concept and exposes a
single transition:

| Module | Program | Transition | Inputs | Output |
|---|---|---|---|---|
| `tokenproof` | `tokenproofx1.aleo` | `verify_token` | `issuer_approved: bool`, `asset_type_supported: bool` | `bool` (`true` iff both) |
| `solvencyproof` | `solvencypx1.aleo` | `prove_solvency` | `reserves: u64`, `liabilities: u64` | `bool` (`true` iff `reserves >= liabilities`) |
| `compliguard` | `compliguardx1.aleo` | `prove_health` | `anomaly_score_below_threshold: bool`, `critical_alert_open: bool` | `bool` (`true` iff anomaly within bounds AND no critical alert) |

Each program is its own Leo project (`program.json` + `src/main.leo`)
and is small on purpose — small enough to make end-to-end Aleo
execution tractable, broad enough to cover the three regulatory
primitives above. See [`aleo/README.md`](./aleo/README.md) and each
program's own `README.md` for inputs and demo scenarios.

---

## Frontend Demo Flow

A React + Vite + TypeScript + Tailwind demo lives in
[`frontend/`](./frontend/). It is a guided 4-step walkthrough:

1. **TokenProof** — enter `issuer_approved` and `asset_type_supported`,
   see the public result, and a bundle stamped with
   `tokenproofx1.aleo :: verify_token`.
2. **SolvencyProof** — enter `reserves` and `liabilities`, see whether
   the system is solvent without disclosing the values, and a bundle
   stamped with `solvencypx1.aleo :: prove_solvency`.
3. **CompliGuard** — enter the system-health flags, see whether the
   compliance system itself is healthy, and a bundle stamped with
   `compliguardx1.aleo :: prove_health`.
4. **Combined proof bundle** — aggregate the three bundles into a single
   hash-anchored object that represents the compliance posture of the
   system at this point in time.

The frontend mirrors the backend's evaluators and canonical-JSON hashing
client-side, so the demo runs standalone.

```bash
cd frontend
npm install
npm run dev
```

See [`frontend/README.md`](./frontend/README.md) for details.

---

## Current Status: Simulated Proof Adapter

CompliLeo is intentionally shipped in two stages.

**Today (this MVP):**

- Leo source for all three programs is in the repo and runs locally
  with the Leo CLI.
- The backend evaluates the same boolean rules and emits deterministic
  proof bundles.
- The Aleo adapter prepares typed Leo inputs and stamps bundles with
  `proof_status: "simulated"` and
  `verification_status: "pending_aleo_execution"`.
- No Aleo network calls, no wallet signing, no on-chain verification.

This is deliberate: the wiring path, program names, transitions, input
types, and bundle layout are all in place so the seam where real Aleo
execution plugs in is small and obvious.

---

## Next Step: Real Aleo Execution / Testnet Verification

The next phase replaces the simulated adapter with real execution:

1. Use each program's `local_path` from the registry to load and
   compile the Leo program.
2. Invoke the named transition against the Aleo testnet (or a local
   `snarkOS` / `leo` runner) with the typed inputs already prepared by
   `aleo_adapter.prepare_*_input`.
3. Replace the placeholder `proof_status`, `verification_status`, and
   `input_commitment` fields with values produced by real proof
   generation and on-chain verification.

No public surface of the API, the adapter, or the proof-bundle layout
needs to change for that step. See [`docs/roadmap.md`](./docs/roadmap.md)
for the full multi-phase plan.

---

## Repository Layout

```
CompliLeo/
├── README.md                       # this file
├── demo-notes.md                   # 60-sec pitch, 3-min walkthrough, demo flow
├── architecture.md                 # technical architecture + execution model
├── docs/
│   ├── regulatory-mapping.md       # GENIUS / CLARITY / SEC-CFTC mapping
│   ├── roadmap.md                  # Phase 1 → Phase 5 roadmap
│   ├── sample-payloads.md          # example requests / responses
│   └── screenshots.md              # screenshot placeholders + capture guide
├── aleo/                           # Leo programs (TokenProof, SolvencyProof, CompliGuard)
├── backend/                        # FastAPI orchestration + Aleo adapter
└── frontend/                       # React / Vite / Tailwind demo
```

---

## License

MIT — see [`LICENSE`](./LICENSE).

---

## Contact

Maranda Harris — Founder, CompliLedger.

CompliLeo is the ZK execution layer of the broader CompliStack vision
for regulated tokenized markets.

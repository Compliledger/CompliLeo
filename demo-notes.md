# CompliLeo — Demo Notes

> Pitch script, walkthrough script, and demo flow for grant reviewers,
> technical evaluators, and ecosystem collaborators.

---

## 60-Second Pitch

> Regulated tokenized markets need to prove compliance — solvency,
> issuer approval, system integrity — without broadcasting customer
> balances, reserves, or internal risk telemetry in cleartext.
>
> **CompliLeo turns those regulatory requirements into executable
> zero-knowledge proof programs on Aleo.** It encodes the rules from
> the GENIUS Act, the CLARITY Act, and the SEC/CFTC tokenization
> framework as small, auditable Leo programs, orchestrates them through
> a FastAPI backend, and packages each result as a deterministic,
> hash-anchored proof bundle.
>
> Today the MVP ships three proofs end-to-end — **TokenProof**,
> **SolvencyProof**, and **CompliGuard** — runnable from a clean React
> demo, with a simulated Aleo adapter as the seam where real Aleo
> testnet execution plugs in next. The result is a repeatable,
> privacy-preserving compliance layer for regulated private stablecoin
> and tokenized-asset systems: **verification without disclosure**.

---

## 3-Minute Walkthrough

**(0:00 — 0:30) The problem.**
Regulated private stablecoins and tokenized markets are pulled in two
directions: regulators demand verifiable compliance, and the systems
themselves are moving toward privacy-preserving architectures.
Traditional disclosure-based audits don't survive that combination.
Zero-knowledge proofs do.

**(0:30 — 1:00) The shape of the solution.**
CompliLeo is the ZK execution layer for that gap. Three Leo programs,
each encoding one regulatory primitive: token admission, reserve
adequacy, and system health. Each one takes **private inputs**, runs
the rule, and emits a **public boolean proof result**. Inputs never
leave the prover; only the result is observable.

**(1:00 — 2:00) The MVP, end-to-end.**
- Open the React demo. Step 1: TokenProof — flip `issuer_approved`
  and `asset_type_supported`, watch the public result and a proof
  bundle stamped with `tokenproofx1.aleo :: verify_token`.
- Step 2: SolvencyProof — type real reserves and liabilities; the
  output is just `solvent: true` or `false`. The numbers themselves
  never appear in the bundle.
- Step 3: CompliGuard — flip the system-health flags; the output
  proves the compliance system itself is operating cleanly.
- Step 4: combine all three into a single hash-anchored bundle that
  represents the system's compliance posture at this moment.

**(2:00 — 2:30) Backend + Aleo wiring.**
Behind the scenes, FastAPI orchestrates each evaluation, and an Aleo
adapter prepares typed Leo inputs (`bool`, `u64`) against an Aleo
program registry that already names the real `tokenproofx1.aleo`,
`solvencypx1.aleo`, and `compliguardx1.aleo` programs in the repo.
Today the adapter returns `proof_status: "simulated"`. Tomorrow it
returns a real Aleo proof.

**(2:30 — 3:00) Why this matters / what's next.**
The same pattern extends to every recurring compliance check a
regulated tokenized system has to perform — and every one of those is
a recurring ZK execution use case for Aleo. **Phase 2 wires real Leo
execution. Phase 3 verifies proofs on Aleo testnet. Phase 4 is a
stablecoin-issuer pilot. Phase 5 expands the CompliStack module
catalog.** Roadmap is in [`docs/roadmap.md`](./docs/roadmap.md).

---

## Exact Demo Flow

The demo can be run from the **frontend wizard**, the **backend HTTP
API**, or directly with the **Leo CLI**. All three paths exercise the
same logic.

### Step 1 — TokenProof (`tokenproofx1.aleo :: verify_token`)

**Narrative.** Before a tokenized asset is admitted, the issuer must be
approved and the asset type must be supported. CompliLeo proves both
gates were cleared.

| Path | Command / action |
|---|---|
| Frontend | Demo wizard → step 1 → set both toggles, click *Evaluate* |
| Backend | `POST /api/tokenproof/evaluate` with `{"issuer_approved": true, "asset_type_supported": true}` |
| Leo CLI | `cd aleo/tokenproofx1 && leo run verify_token true true` |

Pass: both `true` → `valid: true`, reason `TOKEN_ELIGIBLE`.
Fail: any `false` → `valid: false`, reason explains which gate failed.

### Step 2 — SolvencyProof (`solvencypx1.aleo :: prove_solvency`)

**Narrative.** Stablecoin and tokenized-asset frameworks require
reserves to back outstanding liabilities. CompliLeo proves
`reserves >= liabilities` without revealing either number.

| Path | Command / action |
|---|---|
| Frontend | Demo wizard → step 2 → enter reserves and liabilities |
| Backend | `POST /api/solvencyproof/evaluate` with `{"reserves": 1000000, "liabilities": 750000}` |
| Leo CLI | `cd aleo/solvencypx1 && leo run prove_solvency 1000000u64 750000u64` |

Pass: reserves ≥ liabilities → `solvent: true`.
Fail: reserves < liabilities → `solvent: false`.

### Step 3 — CompliGuard (`compliguardx1.aleo :: prove_health`)

**Narrative.** Downstream proofs are only trustworthy when the
compliance system itself is healthy. CompliGuard proves the anomaly
score is within bounds AND no critical alert is open.

| Path | Command / action |
|---|---|
| Frontend | Demo wizard → step 3 → set the two health flags |
| Backend | `POST /api/compliguard/evaluate` with `{"anomaly_score_below_threshold": true, "critical_alert_open": false}` |
| Leo CLI | `cd aleo/compliguardx1 && leo run prove_health true false` |

Pass: anomaly within bounds AND no critical alert → `healthy: true`.
Fail: either condition violated → `healthy: false`.

### Step 4 — Combined proof bundle

**Narrative.** Each proof produces a deterministic bundle. The combined
view aggregates them into a single hash-anchored object representing
the system's compliance posture.

| Path | Command / action |
|---|---|
| Frontend | Demo wizard → step 4 → review combined bundle |
| Backend | `POST /api/proof-bundle/create` once per module, then aggregate |

Sample request/response payloads for every step are in
[`docs/sample-payloads.md`](./docs/sample-payloads.md).

---

## Private Inputs vs. Public Proof Result

This distinction is the entire point of CompliLeo. For each program:

| Module | Private inputs (never disclosed) | Public proof result |
|---|---|---|
| **TokenProof** | `issuer_approved`, `asset_type_supported` | `valid: bool` + reason codes |
| **SolvencyProof** | `reserves: u64`, `liabilities: u64` | `solvent: bool` + reason codes |
| **CompliGuard** | `anomaly_score_below_threshold`, `critical_alert_open` | `healthy: bool` + reason codes |

In the proof-bundle stage:

- The bundle records the **public** result and the program/transition
  that would attest to it.
- Private inputs are not embedded; instead the bundle carries an
  `input_commitment` field (placeholder today, real input commitment
  once Aleo execution is wired in).
- The deterministic `bundle_hash` lets any party independently verify
  that the bundle they're looking at is the bundle that was issued.

The Aleo execution model preserves the same separation natively:
inputs stay on the prover, the network sees only the proof and the
public output.

---

## How These Proofs Map to Regulated Private Stablecoin Systems

Regulated private stablecoin systems have a recurring set of obligations
that map directly onto the three CompliLeo modules:

| Regulated stablecoin obligation | CompliLeo module | What the proof says |
|---|---|---|
| Only approved issuers may mint; only supported asset classes are admitted | **TokenProof** | "This asset cleared issuer approval AND asset-type gating" — no need to disclose issuer identity or internal whitelists |
| Outstanding tokens must be fully reserve-backed at all times | **SolvencyProof** | "Reserves are at least equal to liabilities right now" — without disclosing reserve composition or liability totals |
| Operational integrity of the compliance/monitoring stack must be ongoing, not point-in-time | **CompliGuard** | "The compliance system itself is healthy: no critical alert open and anomaly score within bounds" — without disclosing telemetry |
| Repeatable, machine-checkable compliance posture | **Combined proof bundle** | A single hash-anchored object regulators, counterparties, or platforms can consume on a recurring cadence |

The same shape generalizes to tokenized treasuries, money market funds,
deposit tokens, and other regulated tokenized assets. CompliLeo is the
proof-execution layer; the issuer keeps the data.

---

## What's Out of Scope for This MVP

- Real Aleo network execution / wallet signing / on-chain verification
  (next phase — see [`docs/roadmap.md`](./docs/roadmap.md))
- Database / persistence
- Authentication / authorization
- External data integrations (issuer registries, reserve feeds)
- Composing the three proofs into a single aggregated Aleo proof
- Selective-disclosure / verifiable-credential flows

---

## Frameworks Referenced

- **GENIUS Act** — *Guiding and Establishing National Innovation for
  U.S. Stablecoins*: reserve adequacy, issuer approval.
- **CLARITY Act** — *Digital Asset Market Clarity Act*: asset
  classification and supported-asset gating.
- **SEC / CFTC tokenization framework** — operational integrity,
  monitoring, and market-structure expectations for tokenized assets.

A high-level mapping is in
[`docs/regulatory-mapping.md`](./docs/regulatory-mapping.md). This
document is engineering context, not legal advice.

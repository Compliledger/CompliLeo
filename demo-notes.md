# CompliLeo — Demo Notes

> **CompliLeo turns regulatory requirements from GENIUS, CLARITY, and SEC/CFTC tokenization frameworks into executable zero-knowledge proof programs on Aleo.**

This document captures the key talking points, demo flow, and design decisions for the CompliLeo MVP grant presentation.

---

## What This Is

CompliLeo is a **minimal Leo/Aleo MVP** consisting of three standalone zero-knowledge proof programs. Each program encodes a single, auditable compliance check drawn from emerging U.S. digital asset regulatory frameworks (GENIUS, CLARITY, SEC/CFTC).

This is a **grant/demo sliver** — a proof of concept for the larger CompliStack platform.

---

## Demo Flow

### Step 1 — Token Admission (`tokenproofx1.aleo`)

**Narrative:** Before any tokenized asset is accepted onto a compliant ledger, two gates must be cleared: the issuer must be approved and the asset type must be supported. This program proves both gates are satisfied — in zero knowledge.

```bash
cd tokenproofx1.aleo

# Happy path: both conditions met → outputs true
leo run check_token_admission true true

# Failure: issuer not approved → outputs false
leo run check_token_admission false true
```

**Regulatory tie-in:** Issuer approval maps to permissioned-issuer requirements in the GENIUS Act; asset-type support maps to the CLARITY Act's classification gating.

---

### Step 2 — Solvency Check (`solvencypx1.aleo`)

**Narrative:** Stablecoin and tokenized-asset frameworks require issuers to maintain sufficient reserves. This program proves reserves ≥ liabilities without revealing the actual figures.

```bash
cd solvencypx1.aleo

# Solvent: reserves exceed liabilities → outputs true
leo run check_solvency 1000000u64 750000u64

# Insolvent: liabilities exceed reserves → outputs false
leo run check_solvency 500000u64 750000u64

# Exactly solvent: reserves equal liabilities → outputs true
leo run check_solvency 750000u64 750000u64
```

**Regulatory tie-in:** Maps to the reserve-adequacy requirements in the GENIUS Act and SEC tokenization guidance.

---

### Step 3 — System Health Guard (`compliguardx1.aleo`)

**Narrative:** Compliance infrastructure itself must be monitored. If the system's anomaly score is elevated or a critical alert is open, downstream proofs cannot be trusted. This guard ensures the compliance engine is healthy before other proofs are relied upon.

```bash
cd compliguardx1.aleo

# Healthy: anomaly within bounds, no critical alert → outputs true
leo run check_system_health true false

# Unhealthy: critical alert open → outputs false
leo run check_system_health true true

# Unhealthy: anomaly score over threshold → outputs false
leo run check_system_health false false
```

**Regulatory tie-in:** Maps to operational resilience and compliance monitoring obligations under SEC/CFTC frameworks.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Three separate programs | Keeps each proof minimal, composable, and independently auditable |
| `bool` inputs and outputs | Simplest possible signal — regulatory yes/no at the ZK layer |
| `u64` for monetary values | Sufficient range for reserve/liability amounts in proof context |
| No frontend/backend | MVP scope; UI and API layers are future milestones |
| MIT license | Open for review, grant evaluation, and ecosystem collaboration |

---

## What Comes Next (Out of Scope for This MVP)

- Composing the three proofs into a single aggregate compliance proof
- On-chain record storage using `mapping` and `record` types
- Integration with real issuer registries or reserve data feeds
- Frontend dashboard for compliance officers
- Wallet-based proof submission flows

---

## Frameworks Referenced

- **GENIUS Act** (Guiding and Establishing National Innovation for U.S. Stablecoins) — reserve and issuer requirements
- **CLARITY Act** (Digital Asset Market Clarity Act) — asset classification and supported-type rules
- **SEC / CFTC Tokenization Guidance** — operational resilience, anomaly monitoring, and compliance health obligations

---

*This document is intended for grant reviewers, technical evaluators, and early ecosystem collaborators.*

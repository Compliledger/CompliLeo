# CompliLeo

> **CompliLeo turns regulatory requirements from GENIUS, CLARITY, and SEC/CFTC tokenization frameworks into executable zero-knowledge proof programs on Aleo.**

CompliLeo is a minimal MVP demonstrating how compliance logic can be encoded as on-chain, privacy-preserving proofs using the [Leo programming language](https://leo-lang.org/) on the [Aleo network](https://aleo.org/). This is a grant/demo sliver — not the full CompliStack platform.

---

## Programs

### 1. `tokenproofx1.aleo` — Token Admission Proof

Proves whether a tokenized asset satisfies basic admission rules.

| Input | Type | Description |
|---|---|---|
| `issuer_approved` | `bool` | Whether the issuer has been approved by the compliance authority |
| `asset_type_supported` | `bool` | Whether the asset type is supported on the platform |

**Output:** `bool` — `true` only when both conditions are satisfied.

**Transition:** `check_token_admission`

```leo
transition check_token_admission(
    issuer_approved: bool,
    asset_type_supported: bool
) -> bool {
    return issuer_approved && asset_type_supported;
}
```

---

### 2. `solvencypx1.aleo` — Solvency Proof

Proves whether reserves are greater than or equal to liabilities.

| Input | Type | Description |
|---|---|---|
| `reserves` | `u64` | Total reserve amount held |
| `liabilities` | `u64` | Total outstanding liabilities |

**Output:** `bool` — `true` when `reserves >= liabilities`.

**Transition:** `check_solvency`

```leo
transition check_solvency(
    reserves: u64,
    liabilities: u64
) -> bool {
    return reserves >= liabilities;
}
```

---

### 3. `compliguardx1.aleo` — System Health Proof

Proves whether the compliance system itself is operating within defined health conditions.

| Input | Type | Description |
|---|---|---|
| `anomaly_score_below_threshold` | `bool` | Whether the anomaly detection score is below the configured threshold |
| `critical_alert_open` | `bool` | Whether a critical compliance alert is currently open |

**Output:** `bool` — `true` only when the anomaly score is within bounds AND no critical alert is open.

**Transition:** `check_system_health`

```leo
transition check_system_health(
    anomaly_score_below_threshold: bool,
    critical_alert_open: bool
) -> bool {
    return anomaly_score_below_threshold && !critical_alert_open;
}
```

---

## Repository Structure

```
CompliLeo/
├── README.md
├── demo-notes.md
├── tokenproofx1.aleo/
│   ├── program.json
│   └── src/
│       └── main.leo
├── solvencypx1.aleo/
│   ├── program.json
│   └── src/
│       └── main.leo
└── compliguardx1.aleo/
    ├── program.json
    └── src/
        └── main.leo
```

---

## Regulatory Framing

Each program encodes a slice of the regulatory requirements emerging from:

- **GENIUS Act** — Stablecoin reserve and issuer approval requirements
- **CLARITY Act** — Digital asset classification and supported asset-type rules
- **SEC / CFTC tokenization frameworks** — Compliance health monitoring and anomaly detection obligations

By running these proofs on Aleo, issuers and auditors can demonstrate compliance **without revealing the underlying sensitive data** — the core value proposition of zero-knowledge cryptography applied to financial regulation.

---

## Getting Started

### Prerequisites

- [Leo CLI](https://developer.aleo.org/leo/installation) ≥ 2.0

### Run a program locally

```bash
# Example: prove token admission
cd tokenproofx1.aleo
leo run check_token_admission true true

# Example: prove solvency
cd solvencypx1.aleo
leo run check_solvency 1000000u64 750000u64

# Example: prove system health
cd compliguardx1.aleo
leo run check_system_health true false
```

---

## Scope

This MVP intentionally excludes:

- Frontend or UI
- Backend services or APIs
- Wallet integrations
- External data integrations

These will be addressed in subsequent CompliStack platform milestones.

---

## License

MIT
🚀 CompliLeo

ZK Proof Programs for Private Financial Verification on Aleo

⸻

🧠 Overview

CompliLeo is a set of zero-knowledge programs built on Aleo that enable private financial systems to prove required conditions without exposing sensitive data.

As digital asset infrastructure evolves under regulatory frameworks such as GENIUS, CLARITY, and SEC/CFTC tokenization guidance, systems must demonstrate:
	•	asset legitimacy
	•	reserve backing
	•	operational integrity

At the same time, emerging systems — including private stablecoins and tokenized markets — are moving toward privacy-preserving architectures.

This creates a fundamental challenge:

How can financial systems remain verifiable without disclosure?

CompliLeo solves this by encoding these requirements as zero-knowledge programs.

⸻

⚙️ What This MVP Demonstrates

This repository contains a minimal, functional “sliver” of CompliLeo, designed to demonstrate real execution on Aleo.

It includes three proof programs:

🔹 TokenProof

Verifies that an asset meets defined issuance and eligibility conditions.

👉 Output:
Token Valid = TRUE / FALSE

⸻

🔹 SolvencyProof

Verifies that reserves are greater than or equal to liabilities.

👉 Output:
Solvent = TRUE / FALSE

⸻

🔹 CompliGuard

Verifies that a system is operating within defined conditions.

👉 Output:
System Healthy = TRUE / FALSE

⸻

🔬 Execution Model (Aleo)

CompliLeo leverages Aleo’s zero-knowledge execution model:
Private Inputs → Private Execution → ZK Proof → On-chain Verification
	•	Inputs remain private
	•	Logic executes off-chain
	•	Proof is submitted to the network
	•	Validators verify correctness without seeing underlying data

👉 Aleo verifies computation, not data

⸻

🧩 Architecture
Private Financial / System Inputs
- Token issuance data
- Reserve and liability data
- Monitoring / risk signals

        ↓

CompliLeo (Leo Programs)
- TokenProof
- SolvencyProof
- CompliGuard

        ↓

Aleo ZK Execution
- Private execution (snarkVM)
- Proof generation

        ↓

Aleo Network Verification
- Proof submission
- Validator verification
- On-chain result

        ↓

Verification Consumers
- Stablecoin issuer
- Auditor / regulator
- Counterparty / application
📈 Why This Matters

Financial systems are increasingly required to meet regulatory obligations while preserving privacy.

CompliLeo demonstrates a new model:

Verification without disclosure

Instead of exposing:
	•	reserves
	•	transaction data
	•	system logs

Systems can prove:
	•	solvency
	•	compliance
	•	operational integrity

using zero-knowledge proofs.

⸻

🔥 Impact on Aleo

CompliLeo introduces recurring ZK execution use cases:
	•	solvency attestations
	•	asset validation
	•	system integrity proofs

These use cases:
	•	drive network activity
	•	increase proof generation demand
	•	expand Aleo into regulated financial infrastructure

⸻

🤝 Ecosystem Fit

CompliLeo is designed to integrate with:
	•	private stablecoin systems
	•	payment infrastructure
	•	tokenized asset platforms
	•	institutional DeFi (ZeFi)

It enables these systems to:
	•	remain private
	•	remain verifiable
	•	meet regulatory expectations

⸻

🧪 MVP Scope

This project is intentionally scoped as a minimal proof-of-concept:
	•	simple Leo programs
	•	no external integrations
	•	no frontend or APIs
	•	no real financial data

👉 The goal is to demonstrate feasibility of ZK-based financial verification on Aleo

⸻

🛣️ Future Work
	•	Expanded regulatory mappings (GENIUS, CLARITY, SEC/CFTC)
	•	Richer proof conditions and composability
	•	Integration with stablecoin and payment systems
	•	Selective disclosure / verifiable credentials
	•	Full CompliStack architecture

⸻

🧠 Key Idea

CompliLeo turns regulatory requirements into executable zero-knowledge proofs.

⸻

🏆 Project Context

This project is part of a broader vision to build CompliStack, a regulatory infrastructure layer for tokenized financial systems.

CompliLeo represents the ZK execution layer of that architecture.

⸻

📬 Contact

Maranda Harris
Founder, CompliLedger

⸻

🔥 Final Note

Private financial systems require a new trust model.
CompliLeo demonstrates what that model looks like on Aleo.


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

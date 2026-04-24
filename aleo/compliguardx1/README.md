# compliguardx1.aleo

Minimal proof-program sliver for Aleo, written in
[Leo](https://leo-lang.org/). It proves that the compliance system
itself is operating within healthy bounds, so that downstream proofs
(token admission, solvency, etc.) can be relied upon.

## Purpose

Encodes a system-health check on the compliance pipeline:

1. the **anomaly-detection score** is below the configured threshold, and
2. **no critical alert** is currently open.

Both inputs remain private; only the boolean verdict is revealed.

## Transition

`prove_health`

### Inputs

| Name                            | Type   | Visibility | Description                                            |
| ------------------------------- | ------ | ---------- | ------------------------------------------------------ |
| `anomaly_score_below_threshold` | `bool` | private    | Anomaly score is within the configured safe bound.     |
| `critical_alert_open`           | `bool` | private    | A critical compliance alert is currently open.         |

### Output

`bool` — `true` iff `anomaly_score_below_threshold && !critical_alert_open`.

## Demo scenarios

| Scenario                       | `anomaly_score_below_threshold` | `critical_alert_open` | Result  |
| ------------------------------ | ------------------------------- | --------------------- | ------- |
| Healthy                        | `true`                          | `false`               | `true`  |
| Critical alert open            | `true`                          | `true`                | `false` |
| Anomaly above threshold        | `false`                         | `false`               | `false` |
| Anomalies AND critical alert   | `false`                         | `true`                | `false` |

### Run with the Leo CLI

```bash
cd aleo/compliguardx1
leo run prove_health true  false  # → true
leo run prove_health true  true   # → false
leo run prove_health false false  # → false
```

## Status

This is a **minimal proof-program sliver** intended for demonstration
and validation. Real execution against Aleo testnet/mainnet will be
wired in after this sliver is validated. The backend currently
references the program name `compliguardx1.aleo` through the Aleo
adapter placeholder.

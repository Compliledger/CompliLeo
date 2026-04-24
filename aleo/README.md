# aleo/

Minimal proof-program slivers for Aleo, written in [Leo](https://leo-lang.org/).

Each subdirectory is a self-contained Leo program with a `program.json`
manifest and a `src/main.leo` source file. They are intentionally tiny —
just enough to demonstrate end-to-end zero-knowledge execution on Aleo
for the three CompliLeo proof concepts.

> **Note:** These programs are not yet wired into the backend. They are
> standalone slivers intended to be built and exercised with the Leo CLI.

## Programs

### `tokenproofx1/` → `tokenproofx1.aleo`

Token admission proof. Returns `true` only when both gatekeeping
conditions hold.

- **Inputs**
  - `issuer_approved: bool`
  - `asset_type_supported: bool`
- **Output:** `bool` (`issuer_approved && asset_type_supported`)
- **Transition:** `check_token_admission`

### `solvencypx1/` → `solvencypx1.aleo`

Solvency proof. Returns `true` when reserves cover liabilities.

- **Inputs**
  - `reserves: u64`
  - `liabilities: u64`
- **Output:** `bool` (`reserves >= liabilities`)
- **Transition:** `check_solvency`

### `compliguardx1/` → `compliguardx1.aleo`

System health proof. Returns `true` when the compliance system itself
is operating within healthy bounds.

- **Inputs**
  - `anomaly_score_below_threshold: bool`
  - `critical_alert_open: bool`
- **Output:** `bool` (`anomaly_score_below_threshold && !critical_alert_open`)
- **Transition:** `check_system_health`

## Running locally

With the [Leo CLI](https://developer.aleo.org/leo/installation) installed:

```bash
cd aleo/tokenproofx1
leo run check_token_admission true true

cd ../solvencypx1
leo run check_solvency 1000000u64 750000u64

cd ../compliguardx1
leo run check_system_health true false
```

## Status

These are **minimal proof-program slivers** intended for demonstration
and grant-milestone purposes. They are deliberately not integrated with
the backend in this repository — backend wiring will be added in a
subsequent change.

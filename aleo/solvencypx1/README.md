# solvencypx1.aleo

Minimal proof-program sliver for Aleo, written in
[Leo](https://leo-lang.org/). It proves the reserve-adequacy property
required by stablecoin and tokenized-asset frameworks: that an entity's
reserves are at least as large as its liabilities.

## Purpose

Encodes the core solvency check used in stablecoin and reserve-backed
token frameworks (GENIUS, CLARITY): `reserves >= liabilities`. Both
figures remain private; only the boolean verdict is revealed.

## Transition

`prove_solvency`

### Inputs

| Name          | Type  | Visibility | Description                                       |
| ------------- | ----- | ---------- | ------------------------------------------------- |
| `reserves`    | `u64` | private    | Total reserves held, in the smallest accounting unit. |
| `liabilities` | `u64` | private    | Total outstanding liabilities, in the same unit.  |

### Output

`bool` — `true` iff `reserves >= liabilities`.

## Demo scenarios

| Scenario              | `reserves`    | `liabilities` | Result  |
| --------------------- | ------------- | ------------- | ------- |
| Over-reserved         | `1000000u64`  | `750000u64`   | `true`  |
| Exactly solvent       | `1000000u64`  | `1000000u64`  | `true`  |
| Insolvent             | `500000u64`   | `750000u64`   | `false` |
| Zero reserves         | `0u64`        | `1u64`        | `false` |

### Run with the Leo CLI

```bash
cd aleo/solvencypx1
leo run prove_solvency 1000000u64 750000u64  # → true
leo run prove_solvency 500000u64  750000u64  # → false
```

## Status

This is a **minimal proof-program sliver** intended for demonstration
and validation. Real execution against Aleo testnet/mainnet will be
wired in after this sliver is validated. The backend currently
references the program name `solvencypx1.aleo` through the Aleo
adapter placeholder.

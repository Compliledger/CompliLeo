# tokenproofx1.aleo

Minimal proof-program sliver for Aleo, written in
[Leo](https://leo-lang.org/). It proves whether a tokenized asset
satisfies the basic admission rules required before it can be admitted
to a compliant ledger.

## Purpose

Encodes the two fundamental gatekeeping conditions for token admission
under tokenization frameworks (GENIUS, CLARITY, SEC/CFTC):

1. the **issuer** has been approved by a compliance authority, and
2. the **asset type** is supported by the platform.

Both inputs remain private; only the boolean verdict is revealed.

## Transition

`verify_token`

### Inputs

| Name                   | Type   | Visibility | Description                                        |
| ---------------------- | ------ | ---------- | -------------------------------------------------- |
| `issuer_approved`      | `bool` | private    | Issuer has cleared compliance review.              |
| `asset_type_supported` | `bool` | private    | Asset class is on the platform's supported list.   |

### Output

`bool` — `true` iff `issuer_approved && asset_type_supported`.

## Demo scenarios

| Scenario               | `issuer_approved` | `asset_type_supported` | Result  |
| ---------------------- | ----------------- | ---------------------- | ------- |
| Happy path             | `true`            | `true`                 | `true`  |
| Issuer not approved    | `false`           | `true`                 | `false` |
| Asset type unsupported | `true`            | `false`                | `false` |
| Both fail              | `false`           | `false`                | `false` |

### Run with the Leo CLI

```bash
cd aleo/tokenproofx1
leo run verify_token true true   # → true
leo run verify_token true false  # → false
```

## Status

This is a **minimal proof-program sliver** intended for demonstration
and validation. Real execution against Aleo testnet/mainnet will be
wired in after this sliver is validated. The backend currently
references the program name `tokenproofx1.aleo` through the Aleo
adapter placeholder.

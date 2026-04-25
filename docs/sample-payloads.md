# CompliLeo — Sample Payloads

> Example HTTP requests and responses for every CompliLeo MVP endpoint,
> covering both passing and failing scenarios for each proof module
> plus proof-bundle creation.
>
> All examples target the FastAPI backend at `http://localhost:8000`.
> Aleo execution is currently **simulated** — the `proof_status` and
> `verification_status` fields in proof bundles are placeholders that
> will be replaced by real Aleo execution / testnet verification in a
> future phase (see [`roadmap.md`](./roadmap.md)).

---

## Conventions

- All requests and responses are `application/json`.
- Boolean fields use lowercase `true` / `false`.
- Monetary values for SolvencyProof are non-negative integers (mapped
  to `u64` in Leo).
- Reason codes are stable string identifiers (e.g. `TOKEN_ELIGIBLE`,
  `RESERVES_INSUFFICIENT`) suitable for downstream routing or display.
- The `bundle_hash` shown below is illustrative; clients can recompute
  it as `SHA-256` over the canonical JSON (sorted keys, no whitespace)
  of every other field of the bundle.

---

## TokenProof — `POST /api/tokenproof/evaluate`

Aleo program: `tokenproofx1.aleo` · transition: `verify_token`

### Passing — both gates cleared

**Request**

```http
POST /api/tokenproof/evaluate
Content-Type: application/json

{
  "issuer_approved": true,
  "asset_type_supported": true
}
```

**Response**

```json
{
  "valid": true,
  "reason_codes": ["TOKEN_ELIGIBLE"]
}
```

### Failing — issuer not approved

**Request**

```json
{
  "issuer_approved": false,
  "asset_type_supported": true
}
```

**Response**

```json
{
  "valid": false,
  "reason_codes": ["ISSUER_NOT_APPROVED"]
}
```

### Failing — asset type not supported

**Request**

```json
{
  "issuer_approved": true,
  "asset_type_supported": false
}
```

**Response**

```json
{
  "valid": false,
  "reason_codes": ["ASSET_TYPE_NOT_SUPPORTED"]
}
```

---

## SolvencyProof — `POST /api/solvencyproof/evaluate`

Aleo program: `solvencypx1.aleo` · transition: `prove_solvency`

### Passing — reserves exceed liabilities

**Request**

```json
{
  "reserves": 1000000,
  "liabilities": 750000
}
```

**Response**

```json
{
  "solvent": true,
  "reason_codes": ["RESERVES_SUFFICIENT"]
}
```

### Passing — reserves equal liabilities (boundary)

**Request**

```json
{
  "reserves": 750000,
  "liabilities": 750000
}
```

**Response**

```json
{
  "solvent": true,
  "reason_codes": ["RESERVES_SUFFICIENT"]
}
```

### Failing — liabilities exceed reserves

**Request**

```json
{
  "reserves": 500000,
  "liabilities": 750000
}
```

**Response**

```json
{
  "solvent": false,
  "reason_codes": ["RESERVES_INSUFFICIENT"]
}
```

> Note: the public proof result reveals only `solvent: true/false`. The
> reserve and liability figures are private inputs and do not appear in
> the proof bundle.

---

## CompliGuard — `POST /api/compliguard/evaluate`

Aleo program: `compliguardx1.aleo` · transition: `prove_health`

### Passing — system healthy

**Request**

```json
{
  "anomaly_score_below_threshold": true,
  "critical_alert_open": false
}
```

**Response**

```json
{
  "healthy": true,
  "reason_codes": ["SYSTEM_HEALTHY"]
}
```

### Failing — critical alert open

**Request**

```json
{
  "anomaly_score_below_threshold": true,
  "critical_alert_open": true
}
```

**Response**

```json
{
  "healthy": false,
  "reason_codes": ["CRITICAL_ALERT_OPEN"]
}
```

### Failing — anomaly score over threshold

**Request**

```json
{
  "anomaly_score_below_threshold": false,
  "critical_alert_open": false
}
```

**Response**

```json
{
  "healthy": false,
  "reason_codes": ["ANOMALY_SCORE_OVER_THRESHOLD"]
}
```

---

## Proof Bundle — `POST /api/proof-bundle/create`

Builds a deterministic, hash-anchored proof bundle for one CompliLeo
module evaluation. The `module` field selects which Aleo program /
transition the bundle is stamped against, using the backend's Aleo
program registry.

### TokenProof — passing bundle

**Request**

```json
{
  "module": "tokenproof",
  "decision_result": true,
  "reason_codes": ["TOKEN_ELIGIBLE"]
}
```

**Response**

```json
{
  "module": "tokenproof",
  "decision_result": true,
  "reason_codes": ["TOKEN_ELIGIBLE"],
  "timestamp": "2026-04-24T13:00:00+00:00",
  "input_commitment": "placeholder_input_commitment",
  "aleo_program": "tokenproofx1.aleo",
  "transition_name": "verify_token",
  "proof_status": "simulated",
  "verification_status": "pending_aleo_execution",
  "bundle_hash": "<sha256 hex>"
}
```

### SolvencyProof — failing bundle

**Request**

```json
{
  "module": "solvencyproof",
  "decision_result": false,
  "reason_codes": ["RESERVES_INSUFFICIENT"]
}
```

**Response**

```json
{
  "module": "solvencyproof",
  "decision_result": false,
  "reason_codes": ["RESERVES_INSUFFICIENT"],
  "timestamp": "2026-04-24T13:00:00+00:00",
  "input_commitment": "placeholder_input_commitment",
  "aleo_program": "solvencypx1.aleo",
  "transition_name": "prove_solvency",
  "proof_status": "simulated",
  "verification_status": "pending_aleo_execution",
  "bundle_hash": "<sha256 hex>"
}
```

### CompliGuard — passing bundle

**Request**

```json
{
  "module": "compliguard",
  "decision_result": true,
  "reason_codes": ["SYSTEM_HEALTHY"]
}
```

**Response**

```json
{
  "module": "compliguard",
  "decision_result": true,
  "reason_codes": ["SYSTEM_HEALTHY"],
  "timestamp": "2026-04-24T13:00:00+00:00",
  "input_commitment": "placeholder_input_commitment",
  "aleo_program": "compliguardx1.aleo",
  "transition_name": "prove_health",
  "proof_status": "simulated",
  "verification_status": "pending_aleo_execution",
  "bundle_hash": "<sha256 hex>"
}
```

---

## Aleo Program Registry — `GET /api/aleo/programs`

Lists every CompliLeo Leo program the backend knows about, sourced
from `backend/app/services/aleo_program_registry.py`.

**Response (illustrative)**

```json
[
  {
    "module": "tokenproof",
    "program_name": "tokenproofx1.aleo",
    "transition_name": "verify_token",
    "local_path": "../../aleo/tokenproofx1/src/main.leo",
    "description": "Proves an asset cleared issuer approval and asset-type gating."
  },
  {
    "module": "solvencyproof",
    "program_name": "solvencypx1.aleo",
    "transition_name": "prove_solvency",
    "local_path": "../../aleo/solvencypx1/src/main.leo",
    "description": "Proves reserves are at least equal to liabilities."
  },
  {
    "module": "compliguard",
    "program_name": "compliguardx1.aleo",
    "transition_name": "prove_health",
    "local_path": "../../aleo/compliguardx1/src/main.leo",
    "description": "Proves the compliance system itself is healthy."
  }
]
```

A request for an unknown module (e.g. `GET /api/aleo/programs/unknown`)
returns HTTP `404` with a clean error body.

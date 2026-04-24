# CompliLeo Backend MVP

FastAPI backend for **CompliLeo**, a proof-orchestration MVP for private financial verification on Aleo.

This service exposes three proof-evaluation endpoints and a deterministic proof-bundle builder. It is **backend-only**: no database, no auth, no real Aleo integration, no frontend, no AI.

---

## Proof modules

| Module | Logic |
|---|---|
| **TokenProof** | `valid = issuer_approved AND asset_type_supported` |
| **SolvencyProof** | `solvent = reserves >= liabilities` |
| **CompliGuard** | `healthy = anomaly_score_below_threshold AND NOT critical_alert_open` |

---

## API

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness probe |
| POST | `/api/tokenproof/evaluate` | Evaluate token issuance / eligibility |
| POST | `/api/solvencyproof/evaluate` | Evaluate reserve adequacy |
| POST | `/api/compliguard/evaluate` | Evaluate system-health conditions |
| POST | `/api/proof-bundle/create` | Build a deterministic, hash-anchored proof bundle |

### Examples

```bash
curl -X POST http://localhost:8000/api/tokenproof/evaluate \
  -H 'content-type: application/json' \
  -d '{"issuer_approved": true, "asset_type_supported": true}'
# {"valid": true, "reason_codes": ["TOKEN_ELIGIBLE"]}

curl -X POST http://localhost:8000/api/solvencyproof/evaluate \
  -H 'content-type: application/json' \
  -d '{"reserves": 1000, "liabilities": 750}'
# {"solvent": true, "reason_codes": ["RESERVES_SUFFICIENT"]}

curl -X POST http://localhost:8000/api/compliguard/evaluate \
  -H 'content-type: application/json' \
  -d '{"anomaly_score_below_threshold": true, "critical_alert_open": false}'
# {"healthy": true, "reason_codes": ["SYSTEM_HEALTHY"]}

curl -X POST http://localhost:8000/api/proof-bundle/create \
  -H 'content-type: application/json' \
  -d '{"module": "tokenproof", "decision_result": true, "reason_codes": ["TOKEN_ELIGIBLE"]}'
```

---

## Proof bundle

`POST /api/proof-bundle/create` returns a deterministic JSON object:

```json
{
  "module": "tokenproof",
  "decision_result": true,
  "reason_codes": ["TOKEN_ELIGIBLE"],
  "timestamp": "2026-04-24T13:00:00+00:00",
  "input_commitment": "placeholder_input_commitment",
  "aleo_program": "tokenproofx1.aleo",
  "proof_status": "pending",
  "bundle_hash": "<sha256 hex>"
}
```

`bundle_hash` is `SHA-256` over the **canonical JSON** (sorted keys, no whitespace) of every other field, so any two clients producing the same logical bundle will agree on the hash.

The fields `input_commitment`, `aleo_program`, and `proof_status` are **placeholders** until real Aleo integration is added.

---

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# run the API
uvicorn app.main:app --reload

# run the tests
pytest
```

Interactive docs are available at <http://localhost:8000/docs>.

---

## Scope

Out of scope for this MVP:

- Database / persistence
- Authentication / authorization
- Real Aleo program execution or proof submission
- Frontend
- AI / ML components

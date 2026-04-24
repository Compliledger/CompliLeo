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
| GET  | `/api/aleo/programs` | List all registered Aleo programs and metadata |
| GET  | `/api/aleo/programs/{module}` | Get metadata for a single Aleo program |

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

## Aleo program registry

The backend keeps a single source of truth for every Leo program it would
execute on Aleo: [`app/services/aleo_program_registry.py`](app/services/aleo_program_registry.py).

Each registered program records:

| Field | Meaning |
|---|---|
| `module` | Logical CompliLeo module name (`tokenproof`, `solvencyproof`, `compliguard`) |
| `program_name` | Aleo program identifier (matches `program.json` and `program <name>` in `main.leo`) |
| `transition_name` | The Leo `transition` the backend would invoke |
| `local_path` | Repo-relative path to the program's `main.leo` source file |
| `description` | Short summary of what the program proves |

Current registry contents:

| Module | Program | Transition | Local Leo source |
|---|---|---|---|
| `tokenproof` | `tokenproofx1.aleo` | `verify_token` | [`aleo/tokenproofx1/src/main.leo`](../aleo/tokenproofx1/src/main.leo) |
| `solvencyproof` | `solvencypx1.aleo` | `prove_solvency` | [`aleo/solvencypx1/src/main.leo`](../aleo/solvencypx1/src/main.leo) |
| `compliguard` | `compliguardx1.aleo` | `prove_health` | [`aleo/compliguardx1/src/main.leo`](../aleo/compliguardx1/src/main.leo) |

### How the backend references the local Leo programs

The backend does **not** call the Aleo network yet. Instead:

* `aleo_program_registry.py` holds the metadata above. `local_path` values
  point at the actual Leo source files in this repo's top-level `aleo/`
  directory.
* `aleo_adapter.py` reads `PROGRAM_BY_MODULE` directly from the registry,
  so program names and transition names are never hardcoded outside the
  registry.
* The proof-bundle service uses the same registry mapping when stamping
  bundles with the `aleo_program` / `transition_name` that *would* attest
  to a decision.
* `GET /api/aleo/programs` and `GET /api/aleo/programs/{module}` expose
  the registry over HTTP. An unknown module returns `404` with a clean
  error message.

### Example

```bash
curl http://localhost:8000/api/aleo/programs
# [
#   {"module": "tokenproof",    "program_name": "tokenproofx1.aleo",  "transition_name": "verify_token",   "local_path": "../../aleo/tokenproofx1/src/main.leo",  "description": "..."},
#   {"module": "solvencyproof", "program_name": "solvencypx1.aleo",   "transition_name": "prove_solvency", "local_path": "../../aleo/solvencypx1/src/main.leo",   "description": "..."},
#   {"module": "compliguard",   "program_name": "compliguardx1.aleo", "transition_name": "prove_health",   "local_path": "../../aleo/compliguardx1/src/main.leo", "description": "..."}
# ]

curl http://localhost:8000/api/aleo/programs/tokenproof
```

### Next step: real Aleo execution / testnet integration

The registry is the seam where real Aleo integration will plug in. The
next phase will:

1. Use `local_path` to locate and (build / load) each Leo program.
2. Invoke the named `transition` against the Aleo testnet (or a local
   `snarkOS` / `leo` runner) with the typed inputs already prepared by
   `aleo_adapter.prepare_*_input`.
3. Replace the placeholder `proof_status` / `verification_status` /
   `input_commitment` fields with values produced by real proof
   generation and on-chain (or off-chain) verification.

No public surface of `aleo_adapter` or the proof-bundle layout needs to
change for that step — only the bodies of the placeholder functions.

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

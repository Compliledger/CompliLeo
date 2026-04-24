# CompliLeo — Screenshots

> Placeholder file for grant/demo screenshots. Add the captured images
> to `docs/screenshots/` (create the directory when you take the first
> screenshot) and update the placeholders below to point at them.
>
> All screenshots should reflect the **simulated Aleo proof execution**
> shipped in this MVP. Once real Aleo execution / testnet verification
> lands (see [`roadmap.md`](./roadmap.md)), retake the affected shots.

---

## How to Capture

1. Start the backend:

   ```bash
   cd backend
   python -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

2. In a second shell, start the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Capture the screenshots described below at native resolution
   (Retina / 2x where available). Save as `.png`. Crop to the relevant
   panel; avoid OS chrome.

4. Place captured files under `docs/screenshots/` using the suggested
   filenames and replace the `_(placeholder)_` lines below with normal
   markdown image embeds, e.g.:

   ```markdown
   ![Backend Swagger UI](./screenshots/01-backend-swagger.png)
   ```

---

## 1. Backend Swagger UI

**URL:** <http://localhost:8000/docs>

**What to capture:** the FastAPI Swagger UI showing all CompliLeo
endpoints expanded:

- `GET /health`
- `POST /api/tokenproof/evaluate`
- `POST /api/solvencyproof/evaluate`
- `POST /api/compliguard/evaluate`
- `POST /api/proof-bundle/create`
- `GET /api/aleo/programs`
- `GET /api/aleo/programs/{module}`

**Suggested filename:** `01-backend-swagger.png`

_(placeholder — add `docs/screenshots/01-backend-swagger.png` and embed here)_

---

## 2. Frontend Demo Dashboard

**URL:** <http://localhost:5173/demo>

**What to capture:** the React demo wizard mid-flow, ideally on the
TokenProof step with private inputs filled in and the public proof
result visible.

**Suggested filename:** `02-frontend-demo-dashboard.png`

_(placeholder — add `docs/screenshots/02-frontend-demo-dashboard.png` and embed here)_

---

## 3. Aleo Program Registry Response

**URL:** <http://localhost:8000/api/aleo/programs>

**What to capture:** a pretty-printed JSON response showing all three
registered CompliLeo Aleo programs (`tokenproofx1.aleo`,
`solvencypx1.aleo`, `compliguardx1.aleo`), their transitions, local
Leo source paths, and descriptions.

A clean way to capture this is `curl http://localhost:8000/api/aleo/programs | jq` in a terminal screenshot, or the response panel in Swagger UI.

**Suggested filename:** `03-aleo-program-registry.png`

_(placeholder — add `docs/screenshots/03-aleo-program-registry.png` and embed here)_

---

## 4. Proof Bundle Output

**URL:** <http://localhost:5173/results> (frontend) or response of
`POST /api/proof-bundle/create` (backend).

**What to capture:** a deterministic CompliLeo proof bundle showing:

- `module`, `decision_result`, `reason_codes`
- `timestamp`
- `aleo_program`, `transition_name`
- `proof_status: "simulated"`,
  `verification_status: "pending_aleo_execution"`
- `bundle_hash` (SHA-256 hex)

A combined-bundle view (frontend wizard step 4) is preferred because it
shows TokenProof + SolvencyProof + CompliGuard bundles together with
the aggregate hash.

**Suggested filename:** `04-proof-bundle-output.png`

_(placeholder — add `docs/screenshots/04-proof-bundle-output.png` and embed here)_

---

## Notes

- Keep file sizes reasonable (≤ 500 KB per screenshot where possible).
- If the simulated `proof_status` / `verification_status` values change
  in a future phase, retake screenshots 1, 3, and 4.
- Do not include any real customer data, real reserves, or real issuer
  identifiers in screenshots — the demo values shown in
  [`sample-payloads.md`](./sample-payloads.md) are appropriate for all
  capture purposes.

# CompliLeo Frontend

A clean, technical, demo-ready frontend for the CompliLeo MVP.

## Tech stack

- **Vite** — build tool / dev server
- **React 18** + **TypeScript**
- **Tailwind CSS** — styling
- **React Router** — page routing

No wallet integration. No backend dependency: proof evaluation and
deterministic proof-bundle hashing are mirrored client-side from the Python
backend (`backend/app/services/*`) so the demo runs standalone.

## Pages

1. **Home / Overview** (`/`) — what CompliLeo is and the proof modules it ships.
2. **Run Demo** (`/demo`) — 4-step wizard:
   1. **TokenProof** (`tokenproofx1.aleo :: verify_token`)
   2. **SolvencyProof** (`solvencypx1.aleo :: prove_solvency`)
   3. **CompliGuard** (`compliguardx1.aleo :: prove_health`)
   4. **Combined proof bundle** (aggregate hash)
3. **Proof Bundle Results** (`/results`) — per-module bundles + combined
   bundle, each showing private inputs, public result, generated bundle
   hash (SHA-256 over canonical JSON), and an Aleo proof status placeholder.

## Local development

```bash
cd frontend
npm install
npm run dev      # Vite dev server on http://localhost:5173
npm run build    # type-check + production build to dist/
npm run preview  # preview the production build
```

## Layout

```
frontend/
├── index.html
├── src/
│   ├── main.tsx              # React entry
│   ├── App.tsx               # Routes
│   ├── components/           # Layout, ProofBundleCard, AleoStatus, …
│   ├── lib/
│   │   ├── proofs.ts         # Pure evaluators (mirrors backend services)
│   │   ├── bundle.ts         # Deterministic bundle hashing (SHA-256)
│   │   └── demoStore.ts      # In-memory demo state
│   └── pages/
│       ├── Home.tsx
│       ├── RunDemo.tsx
│       └── BundleResults.tsx
├── tailwind.config.js
├── postcss.config.js
└── vite.config.ts
```

## Notes

- The Aleo proof / verification fields are intentionally placeholders
  (`proof_status: "simulated"`, `verification_status: "pending_aleo_execution"`)
  matching the backend `aleo_adapter` so real Aleo execution can be wired in
  later without changing the bundle layout.
- Bundle hashes are computed in the browser via `crypto.subtle.digest`
  using the same canonical-JSON convention as the backend
  (`json.dumps(..., sort_keys=True, separators=(",", ":"))`).

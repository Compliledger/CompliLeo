"""CompliLeo FastAPI application entrypoint.

CompliLeo is a proof-orchestration MVP for private financial verification
on Aleo. This backend exposes three proof evaluators (TokenProof,
SolvencyProof, CompliGuard) and a deterministic proof-bundle builder.
"""
from fastapi import FastAPI

from app.routers import aleo, compliguard, proof_bundle, solvencyproof, tokenproof

app = FastAPI(
    title="CompliLeo MVP",
    version="0.1.0",
    description=(
        "Proof-orchestration MVP for private financial verification on Aleo. "
        "Backend-only: no database, no auth, no blockchain calls, no frontend."
    ),
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    """Liveness probe."""
    return {"status": "ok"}


app.include_router(tokenproof.router)
app.include_router(solvencyproof.router)
app.include_router(compliguard.router)
app.include_router(proof_bundle.router)
app.include_router(aleo.router)

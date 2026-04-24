"""Proof bundle router."""
from fastapi import APIRouter

from app.models import ProofBundle, ProofBundleRequest
from app.services import proof_bundle_service

router = APIRouter(prefix="/api/proof-bundle", tags=["proof-bundle"])


@router.post("/create", response_model=ProofBundle)
def create(req: ProofBundleRequest) -> ProofBundle:
    return proof_bundle_service.create_bundle(req)

"""SolvencyProof router."""
from fastapi import APIRouter

from app.models import SolvencyProofRequest, SolvencyProofResponse
from app.services import solvencyproof_service

router = APIRouter(prefix="/api/solvencyproof", tags=["solvencyproof"])


@router.post("/evaluate", response_model=SolvencyProofResponse)
def evaluate(req: SolvencyProofRequest) -> SolvencyProofResponse:
    solvent, reason_codes = solvencyproof_service.evaluate(req)
    return SolvencyProofResponse(solvent=solvent, reason_codes=reason_codes)

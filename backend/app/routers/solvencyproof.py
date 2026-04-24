"""SolvencyProof router."""
from fastapi import APIRouter

from app.models import AleoExecutionMetadata, SolvencyProofRequest, SolvencyProofResponse
from app.services import aleo_adapter, solvencyproof_service

router = APIRouter(prefix="/api/solvencyproof", tags=["solvencyproof"])


@router.post("/evaluate", response_model=SolvencyProofResponse)
def evaluate(req: SolvencyProofRequest) -> SolvencyProofResponse:
    solvent, reason_codes = solvencyproof_service.evaluate(req)
    aleo_meta = AleoExecutionMetadata(
        **aleo_adapter.build_proof_metadata(
            "solvencyproof", aleo_adapter.prepare_solvencyproof_input(req)
        )
    )
    return SolvencyProofResponse(
        solvent=solvent, reason_codes=reason_codes, aleo=aleo_meta
    )

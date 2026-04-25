"""TokenProof router."""
from fastapi import APIRouter

from app.models import AleoExecutionMetadata, TokenProofRequest, TokenProofResponse
from app.services import aleo_adapter, tokenproof_service

router = APIRouter(prefix="/api/tokenproof", tags=["tokenproof"])


@router.post("/evaluate", response_model=TokenProofResponse)
def evaluate(req: TokenProofRequest) -> TokenProofResponse:
    valid, reason_codes = tokenproof_service.evaluate(req)
    aleo_meta = AleoExecutionMetadata(
        **aleo_adapter.build_proof_metadata(
            "tokenproof", aleo_adapter.prepare_tokenproof_input(req)
        )
    )
    return TokenProofResponse(valid=valid, reason_codes=reason_codes, aleo=aleo_meta)

"""TokenProof router."""
from fastapi import APIRouter

from app.models import TokenProofRequest, TokenProofResponse
from app.services import tokenproof_service

router = APIRouter(prefix="/api/tokenproof", tags=["tokenproof"])


@router.post("/evaluate", response_model=TokenProofResponse)
def evaluate(req: TokenProofRequest) -> TokenProofResponse:
    valid, reason_codes = tokenproof_service.evaluate(req)
    return TokenProofResponse(valid=valid, reason_codes=reason_codes)

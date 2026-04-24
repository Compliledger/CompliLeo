"""CompliGuard router."""
from fastapi import APIRouter

from app.models import AleoExecutionMetadata, CompliGuardRequest, CompliGuardResponse
from app.services import aleo_adapter, compliguard_service

router = APIRouter(prefix="/api/compliguard", tags=["compliguard"])


@router.post("/evaluate", response_model=CompliGuardResponse)
def evaluate(req: CompliGuardRequest) -> CompliGuardResponse:
    healthy, reason_codes = compliguard_service.evaluate(req)
    aleo_meta = AleoExecutionMetadata(
        **aleo_adapter.build_proof_metadata(
            "compliguard", aleo_adapter.prepare_compliguard_input(req)
        )
    )
    return CompliGuardResponse(
        healthy=healthy, reason_codes=reason_codes, aleo=aleo_meta
    )

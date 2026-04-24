"""CompliGuard router."""
from fastapi import APIRouter

from app.models import CompliGuardRequest, CompliGuardResponse
from app.services import compliguard_service

router = APIRouter(prefix="/api/compliguard", tags=["compliguard"])


@router.post("/evaluate", response_model=CompliGuardResponse)
def evaluate(req: CompliGuardRequest) -> CompliGuardResponse:
    healthy, reason_codes = compliguard_service.evaluate(req)
    return CompliGuardResponse(healthy=healthy, reason_codes=reason_codes)

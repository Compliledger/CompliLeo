"""TokenProof service: validates token issuance / eligibility."""
from __future__ import annotations

from typing import List, Tuple

from app.models import TokenProofRequest


def evaluate(req: TokenProofRequest) -> Tuple[bool, List[str]]:
    """Return (valid, reason_codes).

    valid is True only when issuer_approved AND asset_type_supported.
    """
    reason_codes: List[str] = []
    if not req.issuer_approved:
        reason_codes.append("ISSUER_NOT_APPROVED")
    if not req.asset_type_supported:
        reason_codes.append("ASSET_TYPE_UNSUPPORTED")

    valid = req.issuer_approved and req.asset_type_supported
    if valid:
        reason_codes.append("TOKEN_ELIGIBLE")
    return valid, reason_codes

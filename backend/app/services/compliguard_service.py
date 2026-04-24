"""CompliGuard service: validates system health conditions."""
from __future__ import annotations

from typing import List, Tuple

from app.models import CompliGuardRequest


def evaluate(req: CompliGuardRequest) -> Tuple[bool, List[str]]:
    """Return (healthy, reason_codes).

    healthy is True only when anomaly_score_below_threshold AND NOT critical_alert_open.
    """
    reason_codes: List[str] = []
    if not req.anomaly_score_below_threshold:
        reason_codes.append("ANOMALY_SCORE_ABOVE_THRESHOLD")
    if req.critical_alert_open:
        reason_codes.append("CRITICAL_ALERT_OPEN")

    healthy = req.anomaly_score_below_threshold and not req.critical_alert_open
    if healthy:
        reason_codes.append("SYSTEM_HEALTHY")
    return healthy, reason_codes

"""Pydantic models for CompliLeo proof-orchestration MVP."""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Aleo execution metadata (returned alongside every proof evaluation)
# ---------------------------------------------------------------------------
class AleoExecutionMetadata(BaseModel):
    """Aleo-side metadata attached to each proof-evaluation response.

    Shape is stable across both ``simulated`` and ``local_cli`` execution
    modes so frontends can render it uniformly. ``local_execution_result``
    is populated only when ``execution_mode == "local_cli"``.
    """

    execution_mode: str
    program_name: str
    transition_name: str
    proof_status: str
    verification_status: str
    input_commitment: str
    proof_reference: str
    local_execution_result: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# TokenProof
# ---------------------------------------------------------------------------
class TokenProofRequest(BaseModel):
    issuer_approved: bool = Field(
        ..., description="Whether the issuer has been approved by the compliance authority."
    )
    asset_type_supported: bool = Field(
        ..., description="Whether the asset type is supported on the platform."
    )


class TokenProofResponse(BaseModel):
    valid: bool
    reason_codes: List[str]
    aleo: Optional[AleoExecutionMetadata] = None


# ---------------------------------------------------------------------------
# SolvencyProof
# ---------------------------------------------------------------------------
class SolvencyProofRequest(BaseModel):
    reserves: int = Field(..., ge=0, description="Total reserves held (non-negative).")
    liabilities: int = Field(..., ge=0, description="Total outstanding liabilities (non-negative).")


class SolvencyProofResponse(BaseModel):
    solvent: bool
    reason_codes: List[str]
    aleo: Optional[AleoExecutionMetadata] = None


# ---------------------------------------------------------------------------
# CompliGuard
# ---------------------------------------------------------------------------
class CompliGuardRequest(BaseModel):
    anomaly_score_below_threshold: bool = Field(
        ..., description="Whether the anomaly detection score is below the configured threshold."
    )
    critical_alert_open: bool = Field(
        ..., description="Whether a critical compliance alert is currently open."
    )


class CompliGuardResponse(BaseModel):
    healthy: bool
    reason_codes: List[str]
    aleo: Optional[AleoExecutionMetadata] = None


# ---------------------------------------------------------------------------
# Proof Bundle
# ---------------------------------------------------------------------------
ModuleName = Literal["tokenproof", "solvencyproof", "compliguard"]


class ProofBundleRequest(BaseModel):
    module: ModuleName
    decision_result: bool
    reason_codes: List[str] = Field(default_factory=list)


class ProofBundle(BaseModel):
    module: ModuleName
    decision_result: bool
    reason_codes: List[str]
    timestamp: str
    input_commitment: str
    aleo_program: str
    transition_name: str
    proof_status: str
    verification_status: str
    bundle_hash: str

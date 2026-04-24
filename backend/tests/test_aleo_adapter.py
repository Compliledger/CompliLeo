"""Tests for the Aleo adapter abstraction."""
from app.models import (
    CompliGuardRequest,
    SolvencyProofRequest,
    TokenProofRequest,
)
from app.services import aleo_adapter


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------
def test_prepare_tokenproof_input_maps_fields():
    req = TokenProofRequest(issuer_approved=True, asset_type_supported=False)
    assert aleo_adapter.prepare_tokenproof_input(req) == {
        "issuer_approved": True,
        "asset_type_supported": False,
    }


def test_prepare_solvencyproof_input_maps_fields():
    req = SolvencyProofRequest(reserves=1_000, liabilities=750)
    out = aleo_adapter.prepare_solvencyproof_input(req)
    assert out == {"reserves": 1_000, "liabilities": 750}
    assert isinstance(out["reserves"], int)
    assert isinstance(out["liabilities"], int)


def test_prepare_compliguard_input_maps_fields():
    req = CompliGuardRequest(
        anomaly_score_below_threshold=True, critical_alert_open=False
    )
    assert aleo_adapter.prepare_compliguard_input(req) == {
        "anomaly_score_below_threshold": True,
        "critical_alert_open": False,
    }


# ---------------------------------------------------------------------------
# generate_proof_placeholder
# ---------------------------------------------------------------------------
def test_generate_proof_placeholder_tokenproof():
    inputs = {"issuer_approved": True, "asset_type_supported": True}
    proof = aleo_adapter.generate_proof_placeholder("tokenproof", inputs)
    assert proof["program_name"] == "tokenproofx1.aleo"
    assert proof["transition_name"] == "check_token_admission"
    assert proof["proof_status"] == "simulated"
    assert proof["inputs"] == inputs


def test_generate_proof_placeholder_solvencyproof():
    proof = aleo_adapter.generate_proof_placeholder(
        "solvencyproof", {"reserves": 10, "liabilities": 5}
    )
    assert proof["program_name"] == "solvencypx1.aleo"
    assert proof["transition_name"] == "check_solvency"
    assert proof["proof_status"] == "simulated"


def test_generate_proof_placeholder_compliguard():
    proof = aleo_adapter.generate_proof_placeholder(
        "compliguard",
        {"anomaly_score_below_threshold": True, "critical_alert_open": False},
    )
    assert proof["program_name"] == "compliguardx1.aleo"
    assert proof["transition_name"] == "check_system_health"
    assert proof["proof_status"] == "simulated"


def test_generate_proof_placeholder_copies_inputs():
    """Mutating returned inputs must not affect the caller's dict."""
    inputs = {"issuer_approved": True, "asset_type_supported": True}
    proof = aleo_adapter.generate_proof_placeholder("tokenproof", inputs)
    proof["inputs"]["issuer_approved"] = False
    assert inputs["issuer_approved"] is True


# ---------------------------------------------------------------------------
# verify_proof_placeholder
# ---------------------------------------------------------------------------
def test_verify_proof_placeholder_returns_pending_status():
    proof = aleo_adapter.generate_proof_placeholder(
        "tokenproof", {"issuer_approved": True, "asset_type_supported": True}
    )
    verification = aleo_adapter.verify_proof_placeholder(proof)
    assert verification == {
        "program_name": "tokenproofx1.aleo",
        "transition_name": "check_token_admission",
        "verification_status": "pending_aleo_execution",
    }


def test_verify_proof_placeholder_does_not_call_network():
    """The placeholder must not depend on any network state — it always
    returns ``pending_aleo_execution`` regardless of input shape.
    """
    verification = aleo_adapter.verify_proof_placeholder(
        {"program_name": "x.aleo", "transition_name": "t"}
    )
    assert verification["verification_status"] == "pending_aleo_execution"

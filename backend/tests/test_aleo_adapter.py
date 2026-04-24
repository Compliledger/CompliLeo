"""Tests for the Aleo adapter placeholder layer (Backend Phase 2)."""
import hashlib
import json

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
# Module -> program mapping
# ---------------------------------------------------------------------------
def test_program_by_module_covers_all_three_programs():
    assert aleo_adapter.PROGRAM_BY_MODULE["tokenproof"] == {
        "program_name": "tokenproofx1.aleo",
        "transition_name": "verify_token",
    }
    assert aleo_adapter.PROGRAM_BY_MODULE["solvencyproof"] == {
        "program_name": "solvencypx1.aleo",
        "transition_name": "prove_solvency",
    }
    assert aleo_adapter.PROGRAM_BY_MODULE["compliguard"] == {
        "program_name": "compliguardx1.aleo",
        "transition_name": "prove_health",
    }


# ---------------------------------------------------------------------------
# generate_proof_placeholder
# ---------------------------------------------------------------------------
def test_generate_proof_placeholder_returns_expected_shape():
    inputs = {"issuer_approved": True, "asset_type_supported": True}
    proof = aleo_adapter.generate_proof_placeholder(
        "tokenproofx1.aleo", "verify_token", inputs
    )
    assert proof["program_name"] == "tokenproofx1.aleo"
    assert proof["transition_name"] == "verify_token"
    assert proof["proof_status"] == "simulated"
    assert proof["verification_status"] == "pending_aleo_execution"
    # input_commitment is a SHA-256 hex digest (64 hex chars)
    assert isinstance(proof["input_commitment"], str)
    assert len(proof["input_commitment"]) == 64
    int(proof["input_commitment"], 16)  # must be valid hex


def test_generate_proof_placeholder_input_commitment_is_canonical_sha256():
    inputs = {"reserves": 10, "liabilities": 5}
    proof = aleo_adapter.generate_proof_placeholder(
        "solvencypx1.aleo", "prove_solvency", inputs
    )
    expected = hashlib.sha256(
        json.dumps(inputs, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert proof["input_commitment"] == expected


def test_generate_proof_placeholder_is_deterministic_for_same_inputs():
    inputs = {"anomaly_score_below_threshold": True, "critical_alert_open": False}
    a = aleo_adapter.generate_proof_placeholder(
        "compliguardx1.aleo", "prove_health", inputs
    )
    b = aleo_adapter.generate_proof_placeholder(
        "compliguardx1.aleo", "prove_health", dict(inputs),
    )
    assert a == b


def test_generate_proof_placeholder_input_commitment_changes_with_inputs():
    a = aleo_adapter.generate_proof_placeholder(
        "tokenproofx1.aleo", "verify_token",
        {"issuer_approved": True, "asset_type_supported": True},
    )
    b = aleo_adapter.generate_proof_placeholder(
        "tokenproofx1.aleo", "verify_token",
        {"issuer_approved": False, "asset_type_supported": True},
    )
    assert a["input_commitment"] != b["input_commitment"]


def test_generate_proof_placeholder_key_order_independent():
    """Canonical JSON must yield the same commitment regardless of key order."""
    a = aleo_adapter.generate_proof_placeholder(
        "tokenproofx1.aleo", "verify_token",
        {"issuer_approved": True, "asset_type_supported": True},
    )
    b = aleo_adapter.generate_proof_placeholder(
        "tokenproofx1.aleo", "verify_token",
        {"asset_type_supported": True, "issuer_approved": True},
    )
    assert a["input_commitment"] == b["input_commitment"]


# ---------------------------------------------------------------------------
# verify_proof_placeholder
# ---------------------------------------------------------------------------
def test_verify_proof_placeholder_returns_pending_status():
    proof = aleo_adapter.generate_proof_placeholder(
        "tokenproofx1.aleo", "verify_token",
        {"issuer_approved": True, "asset_type_supported": True},
    )
    verification = aleo_adapter.verify_proof_placeholder(proof)
    assert verification == {
        "program_name": "tokenproofx1.aleo",
        "transition_name": "verify_token",
        "input_commitment": proof["input_commitment"],
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

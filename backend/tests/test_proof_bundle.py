import hashlib
import json

from fastapi.testclient import TestClient

from app.main import app
from app.models import ProofBundleRequest
from app.services import proof_bundle_service

client = TestClient(app)


def test_create_bundle_returns_expected_fields():
    r = client.post(
        "/api/proof-bundle/create",
        json={
            "module": "tokenproof",
            "decision_result": True,
            "reason_codes": ["TOKEN_ELIGIBLE"],
        },
    )
    assert r.status_code == 200
    body = r.json()
    for key in (
        "module",
        "decision_result",
        "reason_codes",
        "timestamp",
        "input_commitment",
        "aleo_program",
        "proof_status",
        "bundle_hash",
    ):
        assert key in body, f"missing field: {key}"

    assert body["module"] == "tokenproof"
    assert body["decision_result"] is True
    assert body["reason_codes"] == ["TOKEN_ELIGIBLE"]
    assert body["aleo_program"] == "tokenproofx1.aleo"
    assert body["proof_status"] == "pending"
    assert body["input_commitment"] == "placeholder_input_commitment"
    # SHA-256 hex digest is 64 chars
    assert len(body["bundle_hash"]) == 64
    int(body["bundle_hash"], 16)  # must be valid hex


def test_aleo_program_mapping_per_module():
    cases = {
        "tokenproof": "tokenproofx1.aleo",
        "solvencyproof": "solvencypx1.aleo",
        "compliguard": "compliguardx1.aleo",
    }
    for module, expected_program in cases.items():
        bundle = proof_bundle_service.create_bundle(
            ProofBundleRequest(module=module, decision_result=True, reason_codes=[]),
            timestamp="2026-01-01T00:00:00+00:00",
        )
        assert bundle.aleo_program == expected_program


def test_bundle_hash_is_deterministic_for_same_inputs():
    req = ProofBundleRequest(
        module="solvencyproof",
        decision_result=True,
        reason_codes=["RESERVES_SUFFICIENT"],
    )
    ts = "2026-04-24T13:00:00+00:00"
    b1 = proof_bundle_service.create_bundle(req, timestamp=ts)
    b2 = proof_bundle_service.create_bundle(req, timestamp=ts)
    assert b1.bundle_hash == b2.bundle_hash


def test_bundle_hash_changes_with_inputs():
    ts = "2026-04-24T13:00:00+00:00"
    b1 = proof_bundle_service.create_bundle(
        ProofBundleRequest(module="compliguard", decision_result=True, reason_codes=["SYSTEM_HEALTHY"]),
        timestamp=ts,
    )
    b2 = proof_bundle_service.create_bundle(
        ProofBundleRequest(module="compliguard", decision_result=False, reason_codes=["CRITICAL_ALERT_OPEN"]),
        timestamp=ts,
    )
    assert b1.bundle_hash != b2.bundle_hash


def test_bundle_hash_matches_canonical_sha256_of_body():
    """Hash must be SHA-256 over canonical JSON (sorted keys) of every other field."""
    req = ProofBundleRequest(
        module="tokenproof",
        decision_result=False,
        reason_codes=["ISSUER_NOT_APPROVED", "ASSET_TYPE_UNSUPPORTED"],
    )
    ts = "2026-04-24T13:00:00+00:00"
    bundle = proof_bundle_service.create_bundle(req, timestamp=ts)

    body = bundle.model_dump()
    body.pop("bundle_hash")
    expected = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert bundle.bundle_hash == expected

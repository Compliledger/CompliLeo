from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_tokenproof_valid_when_both_true():
    r = client.post(
        "/api/tokenproof/evaluate",
        json={"issuer_approved": True, "asset_type_supported": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert "TOKEN_ELIGIBLE" in body["reason_codes"]


def test_tokenproof_invalid_when_issuer_not_approved():
    r = client.post(
        "/api/tokenproof/evaluate",
        json={"issuer_approved": False, "asset_type_supported": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert "ISSUER_NOT_APPROVED" in body["reason_codes"]


def test_tokenproof_invalid_when_asset_type_unsupported():
    r = client.post(
        "/api/tokenproof/evaluate",
        json={"issuer_approved": True, "asset_type_supported": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert "ASSET_TYPE_UNSUPPORTED" in body["reason_codes"]


def test_tokenproof_invalid_when_both_false():
    r = client.post(
        "/api/tokenproof/evaluate",
        json={"issuer_approved": False, "asset_type_supported": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert "ISSUER_NOT_APPROVED" in body["reason_codes"]
    assert "ASSET_TYPE_UNSUPPORTED" in body["reason_codes"]

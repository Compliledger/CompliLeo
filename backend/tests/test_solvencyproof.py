from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_solvent_when_reserves_greater_than_liabilities():
    r = client.post(
        "/api/solvencyproof/evaluate",
        json={"reserves": 1000, "liabilities": 500},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["solvent"] is True
    assert "RESERVES_SUFFICIENT" in body["reason_codes"]


def test_solvent_when_reserves_equal_liabilities():
    r = client.post(
        "/api/solvencyproof/evaluate",
        json={"reserves": 750, "liabilities": 750},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["solvent"] is True


def test_insolvent_when_liabilities_exceed_reserves():
    r = client.post(
        "/api/solvencyproof/evaluate",
        json={"reserves": 100, "liabilities": 500},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["solvent"] is False
    assert "RESERVES_INSUFFICIENT" in body["reason_codes"]


def test_negative_inputs_rejected():
    r = client.post(
        "/api/solvencyproof/evaluate",
        json={"reserves": -1, "liabilities": 0},
    )
    assert r.status_code == 422

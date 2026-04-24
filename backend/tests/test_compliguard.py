from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthy_when_anomaly_low_and_no_critical_alert():
    r = client.post(
        "/api/compliguard/evaluate",
        json={"anomaly_score_below_threshold": True, "critical_alert_open": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["healthy"] is True
    assert "SYSTEM_HEALTHY" in body["reason_codes"]


def test_unhealthy_when_critical_alert_open():
    r = client.post(
        "/api/compliguard/evaluate",
        json={"anomaly_score_below_threshold": True, "critical_alert_open": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["healthy"] is False
    assert "CRITICAL_ALERT_OPEN" in body["reason_codes"]


def test_unhealthy_when_anomaly_above_threshold():
    r = client.post(
        "/api/compliguard/evaluate",
        json={"anomaly_score_below_threshold": False, "critical_alert_open": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["healthy"] is False
    assert "ANOMALY_SCORE_ABOVE_THRESHOLD" in body["reason_codes"]


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

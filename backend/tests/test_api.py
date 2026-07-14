from __future__ import annotations

from fastapi.testclient import TestClient


PAYLOAD = {
    "company": "Demo Logistics Ukraine",
    "contact": "operations@example.com",
    "request_text": (
        "Ми отримуємо близько 80 заявок на день через пошту і сайт. "
        "Потрібно класифікувати їх, готувати чернетки відповідей, "
        "створювати завдання та формувати щоденний звіт директору."
    ),
    "source_type": "web_form",
    "data_classification": "internal",
}


def test_health_is_public(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_requires_key(client: TestClient) -> None:
    response = client.get("/api/v1/runs")
    assert response.status_code == 401


def test_full_intake_approval_and_evidence_flow(client: TestClient, headers: dict[str, str]) -> None:
    created = client.post("/api/v1/intake", json=PAYLOAD, headers=headers)
    assert created.status_code == 201, created.text
    run = created.json()
    assert run["evidence_id"].startswith("BADS-")
    assert run["status"] == "awaiting_approval"
    assert run["approval"]["status"] == "pending"
    assert len(run["agent_runs"]) == 5
    assert run["input_hash"] != run["output_hash"]

    summary = client.get("/api/v1/dashboard/summary", headers=headers)
    assert summary.status_code == 200
    assert summary.json()["total_runs"] == 1
    assert summary.json()["awaiting_approval"] == 1

    approval_id = run["approval"]["id"]
    decision = client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        json={"decision": "approved", "reviewer_id": "valentyn", "note": "Pilot draft approved"},
        headers=headers,
    )
    assert decision.status_code == 200, decision.text
    decided = decision.json()
    assert decided["status"] == "approved_draft"
    assert decided["approval"]["status"] == "approved"

    evidence = client.get(f"/api/v1/evidence/{run['evidence_id']}", headers=headers)
    assert evidence.status_code == 200
    package = evidence.json()
    assert package["approval"]["status"] == "approved"
    assert len(package["integrity"]["package_hash"]) == 64


def test_rejects_too_short_request(client: TestClient, headers: dict[str, str]) -> None:
    payload = {**PAYLOAD, "request_text": "Короткий запит"}
    response = client.post("/api/v1/intake", json=payload, headers=headers)
    assert response.status_code == 422

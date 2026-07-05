"""Integration tests for package API endpoints (T150)."""
import time


def _headers(persona: str = "michael-scott") -> dict:
    return {"X-Persona-Id": persona}


def test_list_packages_returns_200(client, package):
    resp = client.get("/packages", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


def test_get_package_returns_detail(client, package):
    resp = client.get(f"/packages/{package.package_id}", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["package_id"] == package.package_id
    assert "line_items" in data


def test_get_package_not_found(client):
    resp = client.get("/packages/PKG-NOTEXIST", headers=_headers())
    assert resp.status_code == 404


def test_advance_status_success(client, package, darryl):
    resp = client.post(
        f"/packages/{package.package_id}/status",
        json={"status": "packaged", "reason": "Packed up"},
        headers=_headers("darryl-philbin"),
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "packaged"


def test_advance_status_invalid_transition(client, package, darryl):
    resp = client.post(
        f"/packages/{package.package_id}/status",
        json={"status": "delivered"},
        headers=_headers("darryl-philbin"),
    )
    assert resp.status_code == 409


def test_advance_status_wrong_persona_rejected(client, package):
    """Sales persona cannot advance lifecycle."""
    resp = client.post(
        f"/packages/{package.package_id}/status",
        json={"status": "packaged"},
        headers=_headers("jim-halpert"),
    )
    assert resp.status_code == 403


def test_get_package_history(client, package):
    resp = client.get(f"/packages/{package.package_id}/history", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert data["package_id"] == package.package_id
    assert isinstance(data["history"], list)


def test_list_packages_response_time_under_2s(client, package):
    """SC-006: package list must load in under 2 seconds."""
    start = time.time()
    resp = client.get("/packages", headers=_headers())
    elapsed = time.time() - start
    assert resp.status_code == 200
    assert elapsed < 2.0, f"Package list took {elapsed:.2f}s — exceeds 2s budget"


def test_at_risk_packages_endpoint(client, package):
    resp = client.get("/packages/at-risk", headers=_headers())
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_delayed_packages_endpoint(client, package):
    resp = client.get("/packages/delayed", headers=_headers())
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_operational_summary(client, package):
    resp = client.get("/operational-summary", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert "total_packages" in data
    assert "open_complaints" in data


def test_operational_summary_includes_extended_fields(client, package):
    """T028: operational-summary includes backorder_count, order_created_count, customer_unhappy_count."""
    resp = client.get("/operational-summary", headers=_headers())
    assert resp.status_code == 200
    data = resp.json()
    assert "backorder_count" in data, "backorder_count missing from operational-summary"
    assert "order_created_count" in data, "order_created_count missing from operational-summary"
    assert "customer_unhappy_count" in data, "customer_unhappy_count missing from operational-summary"
    assert isinstance(data["backorder_count"], int)
    assert isinstance(data["order_created_count"], int)
    assert isinstance(data["customer_unhappy_count"], int)
    assert data["backorder_count"] >= 0
    assert data["order_created_count"] >= 0
    assert data["customer_unhappy_count"] >= 0


def test_no_persona_header_allows_read(client):
    """Anonymous GET is allowed; persona is only required for writes."""
    resp = client.get("/packages")
    assert resp.status_code == 200

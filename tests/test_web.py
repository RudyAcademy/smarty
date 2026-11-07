import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SPARKY_LOCAL_ROOT", str(tmp_path / "local"))
    monkeypatch.setenv("SPARKY_NAS_ROOT", str(tmp_path / "nas"))
    monkeypatch.setenv("SMARTY_WEB_PASSWORD", "testpass123")
    monkeypatch.setenv("SMARTY_SYNC_TOKEN", "synctoken123")
    monkeypatch.setenv("SPARKY_DEVICE_LABEL", "cloud-test")
    monkeypatch.delenv("SPARKY_CONFIG", raising=False)

    # Force a fresh import so module-level app/state don't leak between tests.
    import sys

    for mod in list(sys.modules):
        if mod.startswith("smarty.web"):
            del sys.modules[mod]

    from smarty.web.app import app

    with TestClient(app) as c:
        yield c


def _login(client):
    r = client.post("/login", data={"password": "testpass123", "next": "/"}, follow_redirects=False)
    assert r.status_code == 303


def test_unauthenticated_redirects_to_login(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 303
    assert "/login" in r.headers["location"]


def test_wrong_password_rejected(client):
    r = client.post("/login", data={"password": "wrong", "next": "/"})
    assert r.status_code == 401


def test_correct_password_logs_in_and_shows_tiles(client):
    _login(client)
    r = client.get("/")
    assert r.status_code == 200
    assert "Weekly bots performance" in r.text
    assert "Growth and enrolment" in r.text


def test_tile_page_lists_records(client):
    _login(client)
    r = client.get("/tile/1")  # Growth and enrolment
    assert r.status_code == 200
    assert "Gauss" in r.text


def test_record_detail_shows_summary(client):
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=1")
    assert r.status_code == 200
    assert "Gauss contest preparation" in r.text


def test_notes_save_and_persist(client):
    _login(client)
    r = client.post(
        "/record/sparky-idea-gauss/notes",
        data={"notes": "Check with Lumi", "from_tile": "1"},
        follow_redirects=False,
    )
    assert r.status_code == 303
    r = client.get("/record/sparky-idea-gauss?from_tile=1")
    assert "Check with Lumi" in r.text


def test_reject_requires_two_posts(client):
    _login(client)
    r = client.post(
        "/record/sparky-idea-gauss/status", data={"status": "rejected", "from_tile": "1"}, follow_redirects=True
    )
    assert "Confirm reject" in r.text

    r = client.get("/record/sparky-idea-gauss?from_tile=1")
    assert "status-unreviewed" in r.text or "unreviewed" in r.text.lower()

    r = client.post(
        "/record/sparky-idea-gauss/status",
        data={"status": "rejected", "from_tile": "1", "confirm": "1"},
        follow_redirects=True,
    )
    assert r.status_code == 200


def test_rejected_record_shows_in_rejected_view(client):
    _login(client)
    client.post(
        "/record/sparky-idea-gauss/status",
        data={"status": "rejected", "from_tile": "1", "confirm": "1"},
        follow_redirects=True,
    )
    r = client.get("/tile/9")  # Rejected (recoverable)
    assert "Gauss" in r.text


def test_sync_api_requires_bearer_token(client):
    r = client.get("/api/sync/pull")
    assert r.status_code == 401
    r = client.get("/api/sync/pull", headers={"Authorization": "Bearer wrong"})
    assert r.status_code == 401
    r = client.get("/api/sync/pull", headers={"Authorization": "Bearer synctoken123"})
    assert r.status_code == 200


def test_sync_api_push_merges_and_pull_reflects_it(client):
    _login(client)
    client.post("/record/sparky-idea-gauss/notes", data={"notes": "from web", "from_tile": "1"})

    headers = {"Authorization": "Bearer synctoken123"}
    pulled = client.get("/api/sync/pull", headers=headers).json()["ops"]
    assert len(pulled) == 1

    # simulate a laptop pushing a foreign op for a different record
    from smarty.journal import new_operation

    foreign_op = new_operation(
        device_id="laptop-1",
        device_label="laptop-1",
        content_id="sparky-idea-holiday-gifts",
        field="status",
        base_op_ids=(),
        value="parked",
    )
    r = client.post("/api/sync/push", json={"ops": [foreign_op.to_dict()]}, headers=headers)
    assert r.status_code == 200
    assert r.json()["merged"] == 1

    r = client.get("/record/sparky-idea-holiday-gifts")
    assert "parked" in r.text.lower()

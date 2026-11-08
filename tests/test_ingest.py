import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("SPARKY_LOCAL_ROOT", str(tmp_path / "local"))
    monkeypatch.setenv("SPARKY_NAS_ROOT", str(tmp_path / "nas"))
    monkeypatch.setenv("SMARTY_WEB_PASSWORD", "testpass123")
    monkeypatch.setenv("SMARTY_SYNC_TOKEN", "synctoken123")
    monkeypatch.setenv("SMARTY_INGEST_TOKEN", "ingesttoken123")
    monkeypatch.setenv("SPARKY_DEVICE_LABEL", "cloud-test")
    monkeypatch.delenv("SPARKY_CONFIG", raising=False)

    import sys

    for mod in list(sys.modules):
        if mod.startswith("smarty.web"):
            del sys.modules[mod]

    from smarty.web.app import app

    with TestClient(app) as c:
        yield c


AUTH = {"Authorization": "Bearer ingesttoken123"}


def _new_idea(id="sparky-idea-grokbot-1", title="Grok-bot idea", category="Growth and enrolment"):
    return {
        "id": id,
        "title": title,
        "categories": [category],
        "summary": "A fresh idea from Grok-bot.",
        "implementation_advice": {
            "kind": "bot_suggested_not_original_source_evidence",
            "text": "Try this.",
        },
        "originating_bots": ["Grok-bot"],
    }


def test_schema_endpoint_needs_no_auth(client):
    r = client.get("/api/ingest/schema")
    assert r.status_code == 200
    data = r.json()
    assert data["endpoint"] == "POST /api/ingest"
    assert "Growth and enrolment" in data["valid_categories"]
    assert "Rudy's collection" not in data["valid_categories"]


def test_ingest_requires_token(client):
    r = client.post("/api/ingest", json={"ideas": [_new_idea()]})
    assert r.status_code == 401


def test_ingest_wrong_token_rejected(client):
    r = client.post(
        "/api/ingest", json={"ideas": [_new_idea()]}, headers={"Authorization": "Bearer wrong"}
    )
    assert r.status_code == 401


def test_ingest_adds_new_idea_and_shows_up_in_tile(client):
    r = client.post("/api/ingest", json={"ideas": [_new_idea()]}, headers=AUTH)
    assert r.status_code == 200
    body = r.json()
    assert body["added"] == ["sparky-idea-grokbot-1"]

    _login(client)
    r = client.get("/tile/1")  # Growth and enrolment
    assert "Grok-bot idea" in r.text


def _login(client):
    client.post("/login", data={"password": "testpass123", "next": "/"}, follow_redirects=False)


def test_ingest_rejects_invalid_category(client):
    idea = _new_idea(category="Not A Real Category")
    r = client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)
    assert r.status_code == 422


def test_ingest_rejects_status_view_label_as_category(client):
    idea = _new_idea(category="Rudy's collection")
    r = client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)
    assert r.status_code == 422


def test_ingest_rejects_empty_submission(client):
    r = client.post("/api/ingest", json={"ideas": []}, headers=AUTH)
    assert r.status_code == 400


def test_repeated_submission_of_same_id_does_not_duplicate(client):
    idea = _new_idea()
    r1 = client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)
    assert r1.json()["added"] == ["sparky-idea-grokbot-1"]

    r2 = client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)
    assert r2.json()["added"] == []
    assert r2.json()["no_op"] is True

    _login(client)
    r = client.get("/tile/1")
    assert r.text.count("Grok-bot idea") == 1


def test_ingest_preserves_existing_notes_and_status_on_resubmission(client):
    idea = _new_idea()
    client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)

    _login(client)
    client.post(
        "/record/sparky-idea-grokbot-1/notes", data={"notes": "worth doing", "from_tile": "1"}
    )
    client.post(
        "/record/sparky-idea-grokbot-1/status",
        data={"status": "kept", "from_tile": "1"},
    )

    # Grok-bot resubmits the same idea later (e.g. a revised wording) at a higher revision.
    revised = _new_idea()
    revised["summary"] = "Revised wording from Grok-bot."
    r = client.post(
        "/api/ingest",
        json={"ideas": [revised], "content_revision": 2},
        headers=AUTH,
    )
    assert r.json()["updated"] == ["sparky-idea-grokbot-1"]

    r = client.get("/record/sparky-idea-grokbot-1?from_tile=1")
    assert "Revised wording from Grok-bot." in r.text
    assert "worth doing" in r.text  # notes survived
    assert "kept" in r.text.lower()  # status survived


def test_ingest_cannot_introduce_new_category(client):
    idea = _new_idea()
    r = client.post(
        "/api/ingest",
        json={"ideas": [idea], "categories": [{"id": "category-99", "label": "Sneaky new tile"}]},
        headers=AUTH,
    )
    # categories field is ignored entirely by the ingest endpoint's pydantic
    # model (it doesn't even accept one), so this just succeeds normally
    # without the new category ever being added.
    assert r.status_code == 200
    _login(client)
    r = client.get("/")
    assert "Sneaky new tile" not in r.text

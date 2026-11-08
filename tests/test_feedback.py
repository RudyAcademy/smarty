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


def _login(client):
    client.post("/login", data={"password": "testpass123", "next": "/"}, follow_redirects=False)


def test_feedback_requires_token(client):
    r = client.get("/api/feedback")
    assert r.status_code == 401


def test_feedback_empty_by_default_when_nothing_reviewed(client):
    r = client.get("/api/feedback", headers=AUTH)
    assert r.status_code == 200
    assert r.json()["records"] == []


def test_feedback_includes_all_when_requested(client):
    r = client.get("/api/feedback?include_all=true", headers=AUTH)
    assert r.status_code == 200
    assert len(r.json()["records"]) == 69


def test_feedback_shows_status_and_notes_after_review(client):
    _login(client)
    client.post(
        "/record/sparky-idea-gauss/status", data={"status": "kept", "from_tile": "1"}
    )
    client.post(
        "/record/sparky-idea-gauss/notes",
        data={"notes": "Worth exploring for Grade 6.", "from_tile": "1"},
    )

    r = client.get("/api/feedback", headers=AUTH)
    records = r.json()["records"]
    assert len(records) == 1
    entry = records[0]
    assert entry["id"] == "sparky-idea-gauss"
    assert entry["status"] == "kept"
    assert entry["notes"] == "Worth exploring for Grade 6."
    assert entry["kind"] == "idea"


def test_feedback_notes_only_without_status_change_still_counts(client):
    _login(client)
    client.post(
        "/record/sparky-idea-holiday-gifts/notes",
        data={"notes": "Maybe next year.", "from_tile": "1"},
    )
    r = client.get("/api/feedback", headers=AUTH)
    ids = {e["id"] for e in r.json()["records"]}
    assert "sparky-idea-holiday-gifts" in ids


def test_feedback_filter_by_status(client):
    _login(client)
    client.post("/record/sparky-idea-gauss/status", data={"status": "kept", "from_tile": "1"})
    client.post(
        "/record/sparky-idea-holiday-gifts/status",
        data={"status": "rejected", "from_tile": "1", "confirm": "1"},
    )

    r = client.get("/api/feedback?status=kept", headers=AUTH)
    ids = {e["id"] for e in r.json()["records"]}
    assert ids == {"sparky-idea-gauss"}

    r = client.get("/api/feedback?status=rejected", headers=AUTH)
    ids = {e["id"] for e in r.json()["records"]}
    assert ids == {"sparky-idea-holiday-gifts"}


def test_feedback_rejects_invalid_status_filter(client):
    r = client.get("/api/feedback?status=not-a-real-status", headers=AUTH)
    assert r.status_code == 400


def test_feedback_reflects_ingested_idea_round_trip(client):
    """Full loop: Grok-bot submits an idea, Rudy reviews it on the web,
    Grok-bot reads the feedback back."""
    idea = {
        "id": "sparky-idea-grokbot-roundtrip",
        "title": "Round trip idea",
        "categories": ["Growth and enrolment"],
        "summary": "Testing the full loop.",
        "implementation_advice": {
            "kind": "bot_suggested_not_original_source_evidence",
            "text": "Try it.",
        },
    }
    r = client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)
    assert r.json()["added"] == ["sparky-idea-grokbot-roundtrip"]

    _login(client)
    client.post(
        "/record/sparky-idea-grokbot-roundtrip/status",
        data={"status": "parked", "from_tile": "1"},
    )
    client.post(
        "/record/sparky-idea-grokbot-roundtrip/notes",
        data={"notes": "Revisit after exams.", "from_tile": "1"},
    )

    r = client.get("/api/feedback?status=parked", headers=AUTH)
    records = r.json()["records"]
    assert len(records) == 1
    assert records[0]["id"] == "sparky-idea-grokbot-roundtrip"
    assert records[0]["notes"] == "Revisit after exams."

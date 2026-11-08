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


def test_ingest_with_distinct_summary_and_advice_shows_both_on_page(client):
    idea = _new_idea(id="sparky-idea-distinct-content")
    idea["summary"] = "A genuinely different one-line summary."
    idea["implementation_advice"]["text"] = "A much longer, specific bot suggestion with real detail."
    client.post("/api/ingest", json={"ideas": [idea]}, headers=AUTH)

    _login(client)
    r = client.get("/record/sparky-idea-distinct-content?from_tile=1")
    assert "A genuinely different one-line summary." in r.text
    assert "A much longer, specific bot suggestion with real detail." in r.text


def test_freshly_ingested_idea_shows_new_badge(client):
    client.post("/api/ingest", json={"ideas": [_new_idea()]}, headers=AUTH)
    _login(client)

    r = client.get("/tile/1")
    assert 'class="is-new"' in r.text
    assert "NEW" in r.text

    r = client.get("/record/sparky-idea-grokbot-1?from_tile=1")
    assert "NEW" in r.text


def _link_snippet(html: str, content_id: str) -> str:
    """The <a ...>...</a> block for one record, so assertions don't
    accidentally match some *other* record on the same tile page (several
    real seed ideas are also legitimately "new" in a freshly-bootstrapped
    test cache, since they're all "first seen" at the same moment)."""
    start = html.index(f'href="/record/{content_id}?')
    end = html.index("</a>", start)
    return html[start:end]


def test_reviewing_idea_removes_new_badge(client):
    client.post("/api/ingest", json={"ideas": [_new_idea()]}, headers=AUTH)
    _login(client)
    client.post(
        "/record/sparky-idea-grokbot-1/status", data={"status": "kept", "from_tile": "1"}
    )

    r = client.get("/tile/1")
    snippet = _link_snippet(r.text, "sparky-idea-grokbot-1")
    assert "is-new" not in snippet
    assert "status-kept" in snippet  # the status badge still shows, just not NEW


def test_old_unreviewed_idea_does_not_show_new_badge(client, tmp_path):
    client.post("/api/ingest", json={"ideas": [_new_idea()]}, headers=AUTH)

    # Backdate first_seen_at well past the NEW_IDEA_WINDOW_DAYS window,
    # bypassing the API (there's no legitimate way to fake the clock
    # through it) to prove old-but-unreviewed ideas don't show NEW.
    import json as json_mod
    from datetime import datetime, timedelta, timezone

    cache_path = tmp_path / "local" / "catalog" / "current.json"
    cache = json_mod.loads(cache_path.read_text(encoding="utf-8"))
    old_time = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    cache["records"]["sparky-idea-grokbot-1"]["first_seen_at"] = old_time
    cache_path.write_text(json_mod.dumps(cache), encoding="utf-8")

    _login(client)
    r = client.get("/tile/1")
    snippet = _link_snippet(r.text, "sparky-idea-grokbot-1")
    assert "is-new" not in snippet
    assert "status-unreviewed" in snippet  # still unreviewed, just not flagged NEW anymore

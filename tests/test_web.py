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


def _save(client, content_id, status, notes="", from_tile="2"):
    return client.post(
        f"/record/{content_id}/save",
        data={"status": status, "notes": notes, "from_tile": from_tile},
        follow_redirects=False,
    )


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
    assert "Buffered ideas waiting to be sent to Grok-Bots" in r.text  # first tile


def test_buffer_is_the_first_tile(client):
    _login(client)
    r = client.get("/")
    buffer_pos = r.text.index("Buffered ideas waiting to be sent to Grok-Bots")
    growth_pos = r.text.index("Growth and enrolment")
    assert buffer_pos < growth_pos


def test_tile_page_lists_records(client):
    # index 0 = buffer, 1 = Weekly bots performance, 2 = Growth and enrolment
    _login(client)
    r = client.get("/tile/2")
    assert r.status_code == 200
    assert "Gauss" in r.text


def test_record_detail_shows_summary(client):
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    assert r.status_code == 200
    assert "Gauss contest preparation" in r.text


def test_record_detail_back_to_list_is_in_header_center(client):
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    header, _, rest = r.text.partition("</header>")
    assert "Back to list" in header
    assert "Back to list" not in rest.split("<main>", 1)[0]  # not duplicated outside header


def test_record_detail_has_no_cautions_blurb(client):
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    assert "Proposal only" not in r.text
    assert "class=\"cautions\"" not in r.text or "Status conflict" in r.text


def test_record_detail_source_link_is_clickable_new_tab(client):
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    assert 'target="_blank"' in r.text
    assert "https://cemc.uwaterloo.ca/contests/gauss" in r.text
    assert '<a href="https://cemc.uwaterloo.ca/contests/gauss"' in r.text


def test_record_detail_collapses_redundant_summary_and_advice(client):
    # The real seed data has summary == "{title}: {advice}" for every idea
    # (verified against the raw source file, not assumed) -- the page must
    # not show the title and the advice text twice because of it.
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    advice_text = "Explore an enrichment group; check registration eligibility before promising a contest sitting."
    assert r.text.count(advice_text) == 1
    assert r.text.count("Gauss contest preparation:") == 0  # the redundant "title: advice" sentence


def test_record_detail_has_single_notes_box_with_save_button(client):
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    assert r.text.count("<textarea") == 1
    assert "Save your notes and Send to Grok-bot" in r.text
    assert "Practical steps" not in r.text


def test_record_detail_status_is_one_form_not_instant_submit_buttons(client):
    """The old design had 4 separate <form> elements, one per status
    button, each submitting immediately. The new design has exactly one
    form (status + notes together); status choices are plain buttons the
    page's JS toggles locally."""
    _login(client)
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    assert r.text.count('action="/record/sparky-idea-gauss/save"') == 1
    assert "status-choice" in r.text
    # the two-click reject guard is client-side JS now, not a server round trip
    assert "danger-armed" in r.text
    assert "Confirm reject and save" in r.text


def test_save_sets_status_and_notes_together_and_shows_confirmation(client):
    _login(client)
    r = _save(client, "sparky-idea-gauss", "kept", "Worth exploring for Grade 6.")
    assert r.status_code == 303
    assert "saved=1" in r.headers["location"]

    r = client.get(r.headers["location"])
    assert "Worth exploring for Grade 6." in r.text
    assert 'class="status-choice active" data-status="kept"' in r.text
    assert 'id="status-input" value="kept"' in r.text
    assert "Your note addition was saved in the notes section and added to the transfer buffer." in r.text


def test_save_rejects_notes_with_unreviewed_status_and_preserves_typed_text(client):
    """The single most important bug fix: an invalid save must not lose
    what was typed, and must not silently leave it unreviewed."""
    _login(client)
    r = _save(client, "sparky-idea-gauss", "unreviewed", "A note nobody has acted on yet.")
    assert r.status_code == 422
    assert "A note nobody has acted on yet." in r.text  # typed text preserved, not lost
    assert "Please choose kept, parked, or rejected" in r.text

    # and the save genuinely did not apply
    r = client.get("/record/sparky-idea-gauss?from_tile=2")
    assert "A note nobody has acted on yet." not in r.text


def test_save_with_blank_notes_and_unreviewed_status_is_allowed(client):
    """The new-notes-forces-a-status rule only applies when notes are
    actually present; a bare status click with no notes still works."""
    _login(client)
    r = _save(client, "sparky-idea-gauss", "unreviewed", "")
    assert r.status_code == 303


def test_save_rejected_removes_idea_from_its_category_tile(client):
    _login(client)
    _save(client, "sparky-idea-gauss", "rejected", "Not a fit this year.")
    r = client.get("/tile/2")  # Growth and enrolment
    assert "Gauss" not in r.text

    r = client.get("/tile/9")  # Rejected (recoverable)
    assert "Gauss" in r.text


def test_save_kept_removes_idea_from_category_tile_and_puts_it_in_buffer(client):
    _login(client)
    _save(client, "sparky-idea-gauss", "kept", "Worth it.")
    r = client.get("/tile/2")
    assert "Gauss" not in r.text

    r = client.get("/tile/0")  # buffer
    assert "Gauss" in r.text


def test_save_parked_removes_idea_from_category_tile_and_puts_it_in_parked_view(client):
    _login(client)
    _save(client, "sparky-idea-gauss", "parked", "Revisit later.")
    r = client.get("/tile/2")
    assert "Gauss" not in r.text

    r = client.get("/tile/8")  # parked
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
    _save(client, "sparky-idea-gauss", "parked", "from web")

    headers = {"Authorization": "Bearer synctoken123"}
    pulled = client.get("/api/sync/pull", headers=headers).json()["ops"]
    assert len(pulled) == 2  # notes + status

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

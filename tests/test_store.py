from smarty.paths import SmartyPaths, ensure_local_dirs
from smarty.seed import build_catalog
from smarty.store import Store


def _catalog():
    idea = {
        "id": "sparky-idea-gauss",
        "title": "Gauss contest preparation",
        "categories": ["Growth and enrolment"],
        "summary": "Proposal",
        "implementation_advice": {"kind": "bot_suggested_not_original_source_evidence", "text": "..."},
    }
    categories = [{"id": "category-2", "label": "Growth and enrolment"}]
    return build_catalog([idea], [], categories)


def _paths(tmp_path, nas_tmp_path, label="pc-a"):
    paths = SmartyPaths(
        local_root=tmp_path / "local",
        nas_root=nas_tmp_path,
        device_id=label,
        device_label=label,
    )
    ensure_local_dirs(paths)
    return paths


def test_default_user_state_is_unreviewed_blank_null(tmp_path):
    paths = _paths(tmp_path, tmp_path / "nas")
    store = Store(paths, _catalog())
    us = store.user_state("sparky-idea-gauss")
    assert us.status == "unreviewed"
    assert us.notes == ""
    assert us.practical_steps == ""


def test_set_status_persists_across_reload(tmp_path):
    paths = _paths(tmp_path, tmp_path / "nas")
    store = Store(paths, _catalog())
    store.set_status("sparky-idea-gauss", "kept")
    store.reload_journal()
    us = store.user_state("sparky-idea-gauza" if False else "sparky-idea-gauss")
    assert us.status == "kept"


def test_notes_edit_does_not_change_status(tmp_path):
    paths = _paths(tmp_path, tmp_path / "nas")
    store = Store(paths, _catalog())
    store.set_status("sparky-idea-gauss", "parked")
    store.set_notes("sparky-idea-gauss", "Check with Lumi")
    us = store.user_state("sparky-idea-gauss")
    assert us.status == "parked"
    assert us.notes == "Check with Lumi"


def test_reject_then_restore_keeps_notes(tmp_path):
    paths = _paths(tmp_path, tmp_path / "nas")
    store = Store(paths, _catalog())
    store.set_notes("sparky-idea-gauss", "worth revisiting")
    store.set_status("sparky-idea-gauss", "rejected")
    store.set_status("sparky-idea-gauss", "unreviewed")
    us = store.user_state("sparky-idea-gauss")
    assert us.status == "unreviewed"
    assert us.notes == "worth revisiting"

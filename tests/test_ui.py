import json

from PySide6.QtWidgets import QListWidget

from smarty.paths import SmartyPaths, ensure_local_dirs
from smarty.seed import build_catalog
from smarty.store import Store
from smarty.ui.main_window import MainWindow
from smarty.version import APP_NAME


def _catalog():
    idea = {
        "id": "sparky-idea-gauss",
        "title": "Gauss contest preparation",
        "categories": ["Growth and enrolment"],
        "summary": "A proposal for contest prep sessions.",
        "originating_bots": ["Bunny"],
        "received_date": {"start": "2026-11-01", "end": "2026-11-07"},
        "implementation_advice": {
            "kind": "bot_suggested_not_original_source_evidence",
            "text": "Run a 6-week prep block.",
        },
    }
    categories = [{"id": "category-2", "label": "Growth and enrolment"}]
    return build_catalog([idea], [], categories)


def _window(tmp_path, qtbot):
    paths = SmartyPaths(local_root=tmp_path / "local", nas_root=tmp_path / "nas", device_id="d", device_label="d")
    ensure_local_dirs(paths)
    store = Store(paths, _catalog())
    window = MainWindow(store, paths)
    qtbot.addWidget(window)
    return window, store


def test_window_title_is_smarty(tmp_path, qtbot):
    window, _ = _window(tmp_path, qtbot)
    assert window.windowTitle() == APP_NAME == "Smarty"


def test_layout_order_is_tiles_center_detail_right_list(tmp_path, qtbot):
    window, _ = _window(tmp_path, qtbot)
    splitter = window._main_splitter
    assert splitter.widget(0) is window.tile_list
    assert isinstance(splitter.widget(2), QListWidget)
    assert splitter.widget(2) is window.record_list
    # center is the detail splitter, not another list
    assert not isinstance(splitter.widget(1), QListWidget)


def test_selecting_record_shows_detail(tmp_path, qtbot):
    window, _ = _window(tmp_path, qtbot)
    window.tile_list.setCurrentRow(1)  # growth_and_enrolment is second entry
    assert window.record_list.count() == 1
    assert "Gauss" in window.title_label.text()


def test_notes_autosave_persists_across_reopen(tmp_path, qtbot):
    window, store = _window(tmp_path, qtbot)
    window.tile_list.setCurrentRow(1)
    window.record_list.setCurrentRow(0)
    window.notes_edit.setPlainText("Check with Lumi")
    window._flush_pending_edits()
    assert store.user_state("sparky-idea-gauss").notes == "Check with Lumi"

    store.reload_journal()
    window2 = MainWindow(store, window.paths)
    qtbot.addWidget(window2)
    window2.tile_list.setCurrentRow(1)
    window2.record_list.setCurrentRow(0)
    assert window2.notes_edit.toPlainText() == "Check with Lumi"


def test_reject_needs_two_clicks(tmp_path, qtbot):
    window, store = _window(tmp_path, qtbot)
    window.tile_list.setCurrentRow(1)
    window.record_list.setCurrentRow(0)

    window._on_status_clicked("rejected")
    assert store.user_state("sparky-idea-gauss").status == "unreviewed"
    assert window._reject_armed is True

    window._on_status_clicked("rejected")
    assert store.user_state("sparky-idea-gauss").status == "rejected"


def test_approval_disclaimer_visible(tmp_path, qtbot):
    window, _ = _window(tmp_path, qtbot)
    assert "not approval" in window.privacy_label.text().lower()


def test_device_label_blank_by_default_and_settable(tmp_path, qtbot, monkeypatch):
    paths = SmartyPaths(
        local_root=tmp_path / "local", nas_root=tmp_path / "nas", device_id="dev-x", device_label=""
    )
    ensure_local_dirs(paths)
    store = Store(paths, _catalog())
    window = MainWindow(store, paths)
    qtbot.addWidget(window)
    assert "unlabeled" in window.device_label_button.text().lower()

    monkeypatch.setattr(
        "smarty.ui.main_window.QInputDialog.getText",
        staticmethod(lambda *a, **k: ("Rudy-Laptop", True)),
    )
    monkeypatch.setattr("smarty.ui.main_window.save_device_label", lambda *a, **k: None)
    window._on_set_device_label()
    assert window.paths.device_label == "Rudy-Laptop"
    assert "Rudy-Laptop" in window.device_label_button.text()


def test_import_batch_button_adds_record_without_duplicating_bot_filter(tmp_path, qtbot):
    from smarty.importer import import_file, load_cache, save_cache

    window, store = _window(tmp_path, qtbot)
    initial_bot_count = window.bot_filter.count()  # "All bots" + "Bunny" from the base fixture

    # Mirror what app.py's build_store does: persist the already-loaded
    # catalog as the on-disk cache before importing on top of it.
    cache_path = window.paths.local_catalog_dir / "current.json"
    cache = load_cache(cache_path, window.store.catalog)
    save_cache(cache_path, cache)

    batch_file = tmp_path / "batch.json"
    batch_file.write_text(
        json.dumps(
            {
                "ideas": [
                    {
                        "id": "idea-new",
                        "title": "New idea",
                        "categories": ["Growth and enrolment"],
                        "summary": "fresh",
                        "originating_bots": ["Otto"],
                        "implementation_advice": {
                            "kind": "bot_suggested_not_original_source_evidence",
                            "text": "...",
                        },
                    }
                ],
                "performance_records": [],
                "categories": [{"id": "category-2", "label": "Growth and enrolment"}],
            }
        ),
        encoding="utf-8",
    )

    report, catalog = import_file(cache_path, batch_file)
    assert report.added_ids == ["idea-new"]
    assert {i.id for i in catalog.ideas} == {"sparky-idea-gauss", "idea-new"}

    window.store.catalog = catalog
    window._populate_tiles()
    window._populate_tiles()  # idempotent: must not duplicate bot_filter entries

    assert window.bot_filter.count() == initial_bot_count + 1  # +1 for the new bot "Otto"

from smarty.paths import SmartyPaths, ensure_local_dirs
from smarty.seed import build_catalog
from smarty.store import Store
from smarty.ui.view_model import filter_rows, rows_for_category, rows_for_status_view, sort_rows


def _catalog():
    ideas = [
        {
            "id": "idea-a",
            "title": "B idea",
            "categories": ["Growth and enrolment"],
            "summary": "alpha summary",
            "originating_bots": ["Bunny"],
            "received_date": {"start": "2026-11-01", "end": "2026-11-01"},
            "implementation_advice": {"kind": "bot_suggested_not_original_source_evidence", "text": "..."},
        },
        {
            "id": "idea-b",
            "title": "A idea",
            "categories": ["Growth and enrolment"],
            "summary": "beta summary",
            "originating_bots": ["Otto"],
            "received_date": {"start": "2026-11-05", "end": "2026-11-05"},
            "implementation_advice": {"kind": "bot_suggested_not_original_source_evidence", "text": "..."},
        },
    ]
    performance = [
        {
            "id": "perf-professor",
            "bot": "Professor",
            "categories": ["Weekly bots performance"],
            "summary": "partial recovered review",
            "caveats": ["documented_partial"],
            "verification_status": "documented_partial",
            "period": {"start": "2026-11-02", "end": "2026-11-02"},
        }
    ]
    categories = [
        {"id": "category-1", "label": "Weekly bots performance"},
        {"id": "category-2", "label": "Growth and enrolment"},
    ]
    return build_catalog(ideas, performance, categories)


def _store(tmp_path, catalog):
    paths = SmartyPaths(local_root=tmp_path / "local", nas_root=tmp_path / "nas", device_id="d", device_label="d")
    ensure_local_dirs(paths)
    return Store(paths, catalog)


def test_rows_for_category_excludes_other_categories(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    rows = rows_for_category(catalog, store, "Growth and enrolment")
    assert {r.content_id for r in rows} == {"idea-a", "idea-b"}


def test_performance_records_only_in_weekly_bots_category(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    rows = rows_for_category(catalog, store, "Weekly bots performance")
    assert {r.content_id for r in rows} == {"perf-professor"}


def test_sort_newest_first_default_ties_break_by_title_then_id(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    rows = rows_for_category(catalog, store, "Growth and enrolment")
    sorted_rows = sort_rows(rows, newest_first=True)
    assert [r.content_id for r in sorted_rows] == ["idea-b", "idea-a"]  # 11-05 newer than 11-01


def test_sort_oldest_first_toggle(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    rows = rows_for_category(catalog, store, "Growth and enrolment")
    sorted_rows = sort_rows(rows, newest_first=False)
    assert [r.content_id for r in sorted_rows] == ["idea-a", "idea-b"]


def test_kept_item_shows_in_rudys_collection_view(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    store.set_status("idea-a", "kept")
    rows = rows_for_status_view(catalog, store, "rudys_collection")
    assert [r.content_id for r in rows] == ["idea-a"]


def test_rejected_item_recoverable_in_rejected_view_not_in_default_category_hide(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    store.set_status("idea-a", "rejected")
    rejected_view = rows_for_status_view(catalog, store, "rejected_recoverable")
    assert [r.content_id for r in rejected_view] == ["idea-a"]
    # still findable in its category too -- rejection never deletes the record
    cat_rows = rows_for_category(catalog, store, "Growth and enrolment")
    assert "idea-a" in {r.content_id for r in cat_rows}


def test_search_matches_title_id_summary_bot_notes(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    store.set_notes("idea-b", "ask Lumi about this one")
    rows = rows_for_category(catalog, store, "Growth and enrolment")
    assert {r.content_id for r in filter_rows(rows, search="otto")} == {"idea-b"}
    assert {r.content_id for r in filter_rows(rows, search="alpha summary")} == {"idea-a"}
    assert {r.content_id for r in filter_rows(rows, search="lumi", store=store)} == {"idea-b"}


def test_filter_by_bot_and_status(tmp_path):
    catalog = _catalog()
    store = _store(tmp_path, catalog)
    store.set_status("idea-a", "parked")
    rows = rows_for_category(catalog, store, "Growth and enrolment")
    assert {r.content_id for r in filter_rows(rows, bot="Bunny")} == {"idea-a"}
    assert {r.content_id for r in filter_rows(rows, status="parked")} == {"idea-a"}

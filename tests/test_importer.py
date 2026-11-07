import json

import pytest

from smarty.importer import (
    ImportRejected,
    apply_import_batch,
    cache_to_catalog,
    import_file,
    load_cache,
    validate_manifest_filename,
)
from smarty.seed import empty_catalog


def _base_idea(rev=1, summary="first summary"):
    return {
        "id": "sparky-idea-gauss",
        "kind": "idea",
        "title": "Gauss contest preparation",
        "categories": ["Growth and enrolment"],
        "summary": summary,
        "content_revision": rev,
        "implementation_advice": {"kind": "bot_suggested_not_original_source_evidence", "text": "..."},
    }


def _cache():
    cache = load_cache_for_test()
    return cache


def load_cache_for_test():
    return {
        "records": {},
        "categories": [{"id": "category-2", "label": "Growth and enrolment"}],
        "applied_batches": [],
    }


def test_new_record_is_added():
    cache = _cache()
    batch = {"ideas": [_base_idea()], "performance_records": [], "categories": []}
    report = apply_import_batch(cache, batch)
    assert report.added_ids == ["sparky-idea-gauss"]
    assert "sparky-idea-gauss" in cache["records"]


def test_duplicate_id_within_one_file_rejects_whole_batch():
    cache = _cache()
    batch = {"ideas": [_base_idea(), _base_idea()], "performance_records": [], "categories": []}
    with pytest.raises(ImportRejected):
        apply_import_batch(cache, batch)


def test_unknown_category_label_rejected():
    cache = _cache()
    idea = _base_idea()
    idea["categories"] = ["not_a_real_category"]
    batch = {"ideas": [idea], "performance_records": [], "categories": []}
    with pytest.raises(ImportRejected):
        apply_import_batch(cache, batch)


def test_higher_revision_updates_summary():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=1)], "performance_records": [], "categories": []})
    report = apply_import_batch(
        cache, {"ideas": [_base_idea(rev=2, summary="revised summary")], "performance_records": [], "categories": []}
    )
    assert report.updated_ids == ["sparky-idea-gauss"]
    assert cache["records"]["sparky-idea-gauss"]["data"]["summary"] == "revised summary"


def test_stale_revision_is_skipped_not_applied():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=5)], "performance_records": [], "categories": []})
    report = apply_import_batch(
        cache, {"ideas": [_base_idea(rev=2, summary="old wording")], "performance_records": [], "categories": []}
    )
    assert report.skipped_stale_ids == ["sparky-idea-gauss"]
    assert cache["records"]["sparky-idea-gauss"]["data"]["summary"] == "first summary"


def test_same_revision_conflicting_text_kept_as_alternate_not_overwritten():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=3, summary="A")], "performance_records": [], "categories": []})
    report = apply_import_batch(
        cache, {"ideas": [_base_idea(rev=3, summary="B")], "performance_records": [], "categories": []}
    )
    assert report.kept_alternate_ids == ["sparky-idea-gauss"]
    assert cache["records"]["sparky-idea-gauss"]["data"]["summary"] == "A"
    assert cache["records"]["sparky-idea-gauss"]["alternates"][0]["data"]["summary"] == "B"


def test_repeat_import_of_identical_bytes_is_idempotent_no_op():
    cache = _cache()
    batch = {"ideas": [_base_idea()], "performance_records": [], "categories": []}
    apply_import_batch(cache, batch)
    report = apply_import_batch(cache, dict(batch))
    assert report.no_op is True
    assert len(cache["records"]) == 1


def test_batch_id_replay_is_no_op():
    cache = _cache()
    batch = {"ideas": [_base_idea()], "performance_records": [], "categories": [], "batch_id": "b1"}
    apply_import_batch(cache, batch)
    report = apply_import_batch(cache, dict(batch))
    assert report.no_op is True


def test_cache_to_catalog_round_trips():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea()], "performance_records": [], "categories": []})
    catalog = cache_to_catalog(cache)
    assert len(catalog.ideas) == 1
    assert catalog.ideas[0].id == "sparky-idea-gauss"


def test_load_cache_from_fresh_catalog_preserves_received_date_and_missing_source_note():
    # Regression test: load_cache's fallback path used to serialize via a
    # generic dataclasses.asdict, which writes keys under this class's
    # Python attribute names (received_period) instead of the seed file's
    # own key names (received_date / period), so from_dict silently lost
    # the received window and the missing_source_note on the next read.
    from smarty.seed import build_catalog

    idea = _base_idea()
    idea["received_date"] = {"start": "2026-10-31", "end": "2026-11-07"}
    idea["evidence"] = {
        "verification_status": "unchecked",
        "claim": "relayed only",
        "missing_source_note": "Exact URL unavailable in weekly review; recover original record rather than invent citation.",
    }
    idea["sources"] = []
    catalog = build_catalog([idea], [], [{"id": "category-2", "label": "Growth and enrolment"}])

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as td:
        cache_path = Path(td) / "current.json"
        cache = load_cache(cache_path, catalog)
        round_tripped = cache_to_catalog(cache)

    rt_idea = round_tripped.ideas[0]
    assert rt_idea.received_period.start == "2026-10-31"
    assert rt_idea.received_period.end == "2026-11-07"
    assert rt_idea.missing_source_note == (
        "Exact URL unavailable in weekly review; recover original record rather than invent citation."
    )


def test_manifest_filename_rejects_path_traversal():
    with pytest.raises(ImportRejected):
        validate_manifest_filename("../../evil.json")
    with pytest.raises(ImportRejected):
        validate_manifest_filename("notjson.txt")
    validate_manifest_filename("catalog-2026-11-07.json")


def test_import_file_end_to_end_writes_cache_and_returns_catalog(tmp_path):
    cache_path = tmp_path / "current.json"
    batch_file = tmp_path / "batch.json"
    categories = [{"id": "category-2", "label": "Growth and enrolment"}]
    batch_file.write_text(
        json.dumps({"ideas": [_base_idea()], "performance_records": [], "categories": categories}),
        encoding="utf-8",
    )

    report, catalog = import_file(cache_path, batch_file)
    assert report.added_ids == ["sparky-idea-gauss"]
    assert len(catalog.ideas) == 1
    assert cache_path.exists()
    assert json.loads(cache_path.read_text(encoding="utf-8"))["records"]


def test_import_file_rejects_without_writing_partial_cache(tmp_path):
    cache_path = tmp_path / "current.json"
    batch_file = tmp_path / "batch.json"
    idea = _base_idea()
    idea["categories"] = ["not_a_real_category"]
    batch_file.write_text(
        json.dumps({"ideas": [idea], "performance_records": [], "categories": []}),
        encoding="utf-8",
    )

    with pytest.raises(ImportRejected):
        import_file(cache_path, batch_file)
    assert not cache_path.exists()


def test_import_file_rejects_bad_json(tmp_path):
    cache_path = tmp_path / "current.json"
    batch_file = tmp_path / "batch.json"
    batch_file.write_text("{not valid json", encoding="utf-8")

    with pytest.raises(ImportRejected):
        import_file(cache_path, batch_file)

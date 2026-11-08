import json

import pytest

from smarty.importer import (
    AdviceUpdateNotFound,
    AdviceUpdateStale,
    ImportRejected,
    apply_import_batch,
    cache_to_catalog,
    import_file,
    load_cache,
    record_first_seen_map,
    update_idea_advice_text,
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


def test_new_record_gets_first_seen_at():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea()], "performance_records": [], "categories": []})
    seen = record_first_seen_map(cache)
    assert seen["sparky-idea-gauss"] is not None


def test_update_preserves_original_first_seen_at():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=1)], "performance_records": [], "categories": []})
    original_seen = record_first_seen_map(cache)["sparky-idea-gauss"]

    apply_import_batch(
        cache, {"ideas": [_base_idea(rev=2, summary="revised summary")], "performance_records": [], "categories": []}
    )
    updated_seen = record_first_seen_map(cache)["sparky-idea-gauss"]
    assert updated_seen == original_seen


def test_bootstrap_from_seed_sets_first_seen_at(tmp_path):
    from smarty.seed import build_catalog

    idea = _base_idea()
    catalog = build_catalog([idea], [], [{"id": "category-2", "label": "Growth and enrolment"}])
    cache = load_cache(tmp_path / "does-not-exist.json", catalog)
    seen = record_first_seen_map(cache)
    assert seen["sparky-idea-gauss"] is not None


def test_update_idea_advice_text_bumps_revision_and_preserves_other_fields():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=1)], "performance_records": [], "categories": []})

    updated = update_idea_advice_text(cache, "sparky-idea-gauss", expected_revision=1, text="Expanded advice.")

    assert updated["content_revision"] == 2
    assert updated["data"]["implementation_advice"]["text"] == "Expanded advice."
    # every other field is untouched
    assert updated["data"]["title"] == "Gauss contest preparation"
    assert updated["data"]["categories"] == ["Growth and enrolment"]
    assert updated["data"]["summary"] == "first summary"


def test_update_idea_advice_text_rejects_stale_revision():
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=1)], "performance_records": [], "categories": []})

    with pytest.raises(AdviceUpdateStale) as exc_info:
        update_idea_advice_text(cache, "sparky-idea-gauss", expected_revision=99, text="x")
    assert exc_info.value.current_revision == 1
    # nothing changed
    assert cache["records"]["sparky-idea-gauss"]["content_revision"] == 1


def test_update_idea_advice_text_rejects_unknown_id():
    cache = _cache()
    with pytest.raises(AdviceUpdateNotFound):
        update_idea_advice_text(cache, "does-not-exist", expected_revision=1, text="x")


def test_update_idea_advice_text_rejects_performance_record_id():
    cache = _cache()
    perf = {
        "id": "sparky-performance-x",
        "kind": "performance",
        "bot": "Professor",
        "summary": "s",
        "caveats": [],
        "verification_status": "relayed_unverified",
    }
    apply_import_batch(cache, {"ideas": [], "performance_records": [perf], "categories": []})
    with pytest.raises(AdviceUpdateNotFound):
        update_idea_advice_text(cache, "sparky-performance-x", expected_revision=0, text="x")


def test_update_idea_advice_text_retry_with_same_expected_revision_is_safely_rejected():
    """Simulates a client that timed out and resends the identical request:
    the first call succeeds and bumps the revision, so a second call with
    the SAME expected_revision must fail loudly (stale) rather than
    silently double-applying -- the safe-retry contract documented in the
    schema."""
    cache = _cache()
    apply_import_batch(cache, {"ideas": [_base_idea(rev=1)], "performance_records": [], "categories": []})

    first = update_idea_advice_text(cache, "sparky-idea-gauss", expected_revision=1, text="First attempt.")
    assert first["content_revision"] == 2

    with pytest.raises(AdviceUpdateStale) as exc_info:
        update_idea_advice_text(cache, "sparky-idea-gauss", expected_revision=1, text="First attempt.")
    assert exc_info.value.current_revision == 2
    # the first attempt's write is the one that stuck
    assert cache["records"]["sparky-idea-gauss"]["data"]["implementation_advice"]["text"] == "First attempt."


def test_update_idea_advice_text_never_touches_cache_categories_or_other_records():
    cache = _cache()
    apply_import_batch(
        cache,
        {
            "ideas": [_base_idea(rev=1), {**_base_idea(rev=1), "id": "sparky-idea-other", "title": "Other idea"}],
            "performance_records": [],
            "categories": [],
        },
    )
    categories_before = list(cache["categories"])
    other_before = dict(cache["records"]["sparky-idea-other"])

    update_idea_advice_text(cache, "sparky-idea-gauss", expected_revision=1, text="Expanded advice.")

    assert cache["categories"] == categories_before
    assert cache["records"]["sparky-idea-other"] == other_before

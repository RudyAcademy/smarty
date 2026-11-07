"""Hand-imported content batches and the local evolving catalog cache.

The catalog cache (``current.json``) is strictly separate from user state
(status/notes/practical steps, which live in the journal). That separation
is what makes "imports never reset notes" true by construction: importing
only ever touches editorial fields of the catalog cache.

A batch file may use either this app's own combined shape
(``{"ideas": [...], "performance_records": [...], "categories": [...]}``)
or one of the real per-type seed file shapes (``{"metadata": {...},
"ideas": [...]}`` / ``{"metadata": {...}, "records": [...]}`` /
``{"categories": [...], ...}``) -- both are accepted so the same seed files
can be re-imported by hand later. Categories are matched by their exact
``label`` text, matching how records reference them.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from smarty.models import SeedValidationError
from smarty.seed import Catalog, build_catalog

CACHE_FILENAME = "current.json"


class ImportRejected(ValueError):
    """Raised when an entire batch must be rejected (never partially applied)."""


@dataclass
class ImportReport:
    updated_ids: list[str] = field(default_factory=list)
    skipped_stale_ids: list[str] = field(default_factory=list)
    kept_alternate_ids: list[str] = field(default_factory=list)
    added_ids: list[str] = field(default_factory=list)
    no_op: bool = False
    rejected_reason: str | None = None


def _record_dicts(catalog: Catalog) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for idea in catalog.ideas:
        d = idea.to_cache_dict()
        d["kind"] = "idea"
        out[idea.id] = d
    for rec in catalog.performance_records:
        d = rec.to_cache_dict()
        d["kind"] = "performance"
        out[rec.id] = d
    return out


def load_cache(cache_path: Path, fallback: Catalog) -> dict:
    """Load the raw cache dict (ids -> record dict + alternates), seeding from fallback."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    records = _record_dicts(fallback)
    return {
        "records": {
            cid: {"data": d, "content_revision": d.get("content_revision", 1), "alternates": []}
            for cid, d in records.items()
        },
        "categories": [c.__dict__ for c in fallback.categories],
        "applied_batches": [],
    }


def save_cache(cache_path: Path, cache: dict) -> None:
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = cache_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(cache_path)


def _ideas_list(batch: dict) -> list:
    value = batch.get("ideas", [])
    if not isinstance(value, list):
        raise ImportRejected("batch field 'ideas' must be a list")
    return value


def _performance_list(batch: dict) -> list:
    # This app's own combined shape uses "performance_records"; the real
    # weekly-performance.json seed file uses "records".
    value = batch.get("performance_records", batch.get("records", []))
    if not isinstance(value, list):
        raise ImportRejected("batch field 'performance_records'/'records' must be a list")
    return value


def _categories_list(batch: dict) -> list:
    value = batch.get("categories", [])
    if not isinstance(value, list):
        raise ImportRejected("batch field 'categories' must be a list")
    return value


def _validate_batch_shape(batch: dict) -> None:
    ideas = _ideas_list(batch)
    performance = _performance_list(batch)
    _categories_list(batch)

    ids_seen: set[str] = set()
    for d in ideas + performance:
        rid = d.get("id")
        if not rid or not d.get("title", d.get("bot")):
            raise ImportRejected(f"record missing stable id/title: {d!r}")
        if rid in ids_seen:
            raise ImportRejected(f"duplicate id within one import file: {rid!r}")
        ids_seen.add(rid)

    for d in ideas:
        if "implementation_advice" not in d or "kind" not in d.get("implementation_advice", {}):
            raise ImportRejected(f"idea {d.get('id')!r} missing implementation_advice.kind")

    for d in performance:
        if "bot" not in d or "caveats" not in d or "verification_status" not in d:
            raise ImportRejected(
                f"performance record {d.get('id')!r} missing bot/caveats/verification_status"
            )
        if "score" in d or "grade" in d:
            raise ImportRejected(f"performance record {d.get('id')!r} must not carry a score/grade")


def batch_revision(batch: dict) -> int:
    if "content_revision" in batch:
        return int(batch["content_revision"])
    prepared_on = batch.get("prepared_on") or batch.get("metadata", {}).get("prepared_on")
    if prepared_on:
        try:
            d = date.fromisoformat(prepared_on)
            return int(d.strftime("%Y%m%d"))
        except ValueError:
            pass
    return 0


def apply_import_batch(cache: dict, batch: dict) -> ImportReport:
    """Apply a parsed batch dict to the cache in place. Raises ImportRejected
    for whole-file problems (duplicate ids, unknown categories, bad shape).
    Never partially applies a rejected batch."""
    _validate_batch_shape(batch)

    known_category_labels = {c["label"] for c in cache.get("categories", [])}
    incoming_categories = {c["label"] for c in _categories_list(batch)}
    all_known = known_category_labels | incoming_categories

    report = ImportReport()
    batch_rev = batch_revision(batch)

    batch_id = batch.get("batch_id")
    if batch_id and batch_id in cache.get("applied_batches", []):
        report.no_op = True
        return report

    records = cache.setdefault("records", {})
    all_incoming = [{**d, "kind": "idea"} for d in _ideas_list(batch)] + [
        {**d, "kind": "performance"} for d in _performance_list(batch)
    ]

    for d in all_incoming:
        rid = d["id"]
        cats = d.get("categories", [])
        unknown = [c for c in cats if c not in all_known]
        if unknown:
            raise ImportRejected(f"record {rid!r} uses unknown category label(s): {unknown}")

        # A record may carry its own content_revision (higher-fidelity than
        # the batch envelope's); fall back to the envelope/batch-level revision.
        rev = d.get("content_revision", batch_rev)
        existing = records.get(rid)
        if existing is None:
            records[rid] = {"data": d, "content_revision": rev, "alternates": []}
            report.added_ids.append(rid)
            continue

        existing_rev = existing.get("content_revision", 1)
        if rev > existing_rev:
            if existing["data"] != d:
                records[rid] = {"data": d, "content_revision": rev, "alternates": existing.get("alternates", [])}
                report.updated_ids.append(rid)
            else:
                report.no_op = True
        elif rev == existing_rev:
            if existing["data"] != d:
                alt = existing.setdefault("alternates", [])
                if d not in [a["data"] for a in alt]:
                    alt.append({"data": d, "content_revision": rev})
                    report.kept_alternate_ids.append(rid)
            else:
                report.no_op = True
        else:
            report.skipped_stale_ids.append(rid)

    for c in _categories_list(batch):
        if c["label"] not in known_category_labels:
            cache.setdefault("categories", []).append(c)

    if batch_id:
        cache.setdefault("applied_batches", []).append(batch_id)

    return report


def cache_to_catalog(cache: dict) -> Catalog:
    idea_dicts = [
        {k: v for k, v in r["data"].items() if k != "kind"}
        for r in cache.get("records", {}).values()
        if r["data"].get("kind") == "idea"
    ]
    perf_dicts = [
        {k: v for k, v in r["data"].items() if k != "kind"}
        for r in cache.get("records", {}).values()
        if r["data"].get("kind") == "performance"
    ]
    category_dicts = cache.get("categories", [])
    try:
        return build_catalog(idea_dicts, perf_dicts, category_dicts, source_note="local cache")
    except SeedValidationError:
        # Cache should always be internally consistent; if not, surface as empty
        # rather than crash the app.
        return build_catalog([], [], category_dicts, source_note="local cache (corrupt, ignored)")


def sha256_of_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate_manifest_filename(name: str) -> None:
    if "/" in name or "\\" in name or ".." in name or not name.endswith(".json"):
        raise ImportRejected(f"rejected unsafe manifest filename: {name!r}")


def import_file(cache_path: Path, batch_file: Path) -> tuple[ImportReport, Catalog]:
    """Hand-import one batch JSON file into the on-disk catalog cache.

    Nothing is written to ``cache_path`` unless the whole batch applies
    cleanly -- ``apply_import_batch`` raises before this function reaches
    ``save_cache`` if anything is wrong, so a rejected batch never leaves a
    partial trace on disk.
    """
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        cache = {"records": {}, "categories": [], "applied_batches": []}

    try:
        batch = json.loads(batch_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ImportRejected(f"{batch_file}: invalid JSON ({exc})") from exc

    report = apply_import_batch(cache, batch)
    save_cache(cache_path, cache)
    catalog = cache_to_catalog(cache)
    return report, catalog

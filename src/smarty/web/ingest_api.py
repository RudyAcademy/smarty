"""Authenticated API for an automated submitter (e.g. Grok-bot) to add new
ideas without a human in the loop.

Reuses apply_import_batch -- the exact same validation a hand-import gets
(duplicate ids rejected, unknown categories rejected, no invented scores,
stable-id resubmission merges by revision instead of duplicating). New or
updated catalog records never touch the journal, so existing notes and
kept/parked/rejected choices are untouched by construction, not by any
special-casing here.

Deliberately cannot create new categories: the 7 content tiles + 3 status
views are fixed, so any "categories" the submitter sends is ignored.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from smarty.importer import ImportRejected, apply_import_batch, cache_to_catalog, save_cache
from smarty.version import CATEGORIES_ORDER
from smarty.web.auth import check_ingest_token

router = APIRouter(prefix="/api/ingest")

MAX_RECORDS_PER_SUBMISSION = 200


class IngestBody(BaseModel):
    ideas: list[dict] = []
    performance_records: list[dict] = []
    batch_id: str | None = None
    content_revision: int | None = None
    prepared_on: str | None = None


def _require_token(request: Request) -> None:
    if not check_ingest_token(request):
        raise HTTPException(status_code=401, detail="missing/invalid ingest bearer token")


@router.get("/schema")
def schema(request: Request):
    """Read-only contract description -- no auth needed to read it, since
    it contains no data, only the shape a submitter must produce."""
    return {
        "endpoint": "POST /api/ingest",
        "auth": "Authorization: Bearer <SMARTY_INGEST_TOKEN>",
        "valid_categories": CATEGORIES_ORDER,
        "id_convention": "sparky-idea-<short-stable-slug>, lowercase, hyphenated, unique forever -- "
        "resubmitting the same id merges/updates instead of duplicating; never reuse an id for a "
        "different idea.",
        "body_shape": {
            "ideas": [
                {
                    "id": "sparky-idea-<slug>",
                    "title": "Short title",
                    "categories": ["<one or more of valid_categories, exact text>"],
                    "summary": "One short sentence distinct from implementation_advice.text -- "
                    "do not just repeat '<title>: <advice>'.",
                    "implementation_advice": {
                        "kind": "bot_suggested_not_original_source_evidence",
                        "text": "Longer and specific: what exactly to do, for whom, roughly how, and "
                        "any concrete detail you actually have (numbers, timing, a named tool or "
                        "format) -- several sentences, not a one-liner. Still never invent a detail "
                        "you don't have.",
                    },
                    "originating_bots": ["Grok-bot"],
                    "received_date": {
                        "start": "YYYY-MM-DD",
                        "end": "YYYY-MM-DD",
                        "granularity": "period",
                        "timezone": "America/Toronto",
                        "original_discovery_at": None,
                    },
                    "sources": [{"url": "https://...", "verification_status": "unchecked"}],
                    "cautions": ["Proposal only; not approved or implemented."],
                }
            ],
            "performance_records": [],
            "batch_id": "optional, replaying the same batch_id again is a no-op",
            "content_revision": "optional int, higher wins on id reuse; omit for a brand new idea",
        },
        "response_shape": {
            "added": ["ids newly created"],
            "updated": ["ids whose editorial fields changed because of a higher revision"],
            "skipped_stale": ["ids ignored because their submitted revision was not higher"],
            "kept_alternate": ["ids where same-revision text differed and was kept as an alternate"],
        },
        "guarantees": [
            "Never invents ideas/scores/dates/URLs on this end -- validates exactly what you submit.",
            "Never creates a new category -- every idea's categories must already be in valid_categories.",
            "A rejected submission (bad shape, unknown category, duplicate id within one call) applies "
            "nothing at all -- never partially applied.",
            "Never touches existing notes or kept/parked/rejected status on any id, including one you "
            "resubmit -- those live in a separate journal this endpoint never writes to.",
        ],
        "content_guidance": [
            "summary and implementation_advice.text are shown separately on the page -- make them say "
            "different things. A summary that's just '<title>: <advice text>' is detected and the "
            "duplicate line is hidden, but a real distinct summary is better.",
            "implementation_advice.text is the main thing a reader sees: make it longer and specific "
            "(what, for whom, how, any concrete number/tool/timing you actually have) rather than one "
            "short sentence -- but still never invent a specific you don't have.",
            "To enrich an idea already in the catalog, resubmit the same id with a higher "
            "content_revision -- it updates the editorial fields in place and never touches notes or "
            "status (see guarantees above).",
        ],
        "reverse_channel": {
            "endpoint": "GET /api/feedback",
            "auth": "Authorization: Bearer <same SMARTY_INGEST_TOKEN> (shared with /api/ingest; "
            "revoking it cuts off both directions together, which is correct)",
            "purpose": "Read Rudy's status/notes on ideas -- what got kept, parked, rejected, and why.",
            "query_params": {
                "status": "optional: unreviewed|kept|parked|rejected, filter to one status",
                "include_all": "optional bool, default false: by default only reviewed records "
                "(status set, or notes/practical_steps non-blank) are returned; true returns everything.",
            },
            "response_shape": {
                "records": [
                    {
                        "id": "sparky-idea-<slug>",
                        "kind": "idea | performance",
                        "title": "...",
                        "status": "unreviewed | kept | parked | rejected",
                        "notes": "Rudy's own text, may be blank",
                        "practical_steps": "edited bot-draft text, may be blank",
                        "status_conflict": "present only if two devices set conflicting status and "
                        "neither has been resolved yet",
                    }
                ]
            },
        },
    }


@router.post("")
def ingest(request: Request, body: IngestBody):
    _require_token(request)

    total = len(body.ideas) + len(body.performance_records)
    if total == 0:
        raise HTTPException(status_code=400, detail="submit at least one idea or performance record")
    if total > MAX_RECORDS_PER_SUBMISSION:
        raise HTTPException(
            status_code=400, detail=f"too many records in one submission (max {MAX_RECORDS_PER_SUBMISSION})"
        )

    # apply_import_batch alone would also accept a status-view label (e.g.
    # "Rudy's collection") as a "category", since those share the same
    # categories.json list -- status views aren't something a submitted
    # idea should ever claim, so enforce the narrower content-tile set here.
    valid_categories = set(CATEGORIES_ORDER)
    for record in body.ideas + body.performance_records:
        bad = [c for c in record.get("categories", []) if c not in valid_categories]
        if bad:
            raise HTTPException(
                status_code=422, detail=f"record {record.get('id')!r} uses invalid categories: {bad}"
            )

    paths = request.app.state.paths
    cache_path = paths.local_catalog_dir / "current.json"
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        cache = {"records": {}, "categories": [], "applied_batches": []}

    batch: dict = {
        "ideas": body.ideas,
        "performance_records": body.performance_records,
        "categories": [],  # an automated submitter can never introduce a new category
    }
    if body.batch_id:
        batch["batch_id"] = body.batch_id
    if body.content_revision is not None:
        batch["content_revision"] = body.content_revision
    if body.prepared_on:
        batch["prepared_on"] = body.prepared_on

    try:
        report = apply_import_batch(cache, batch)
    except ImportRejected as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    save_cache(cache_path, cache)
    catalog = cache_to_catalog(cache)
    request.app.state.store.catalog = catalog

    return {
        "added": report.added_ids,
        "updated": report.updated_ids,
        "skipped_stale": report.skipped_stale_ids,
        "kept_alternate": report.kept_alternate_ids,
        "no_op": report.no_op,
    }

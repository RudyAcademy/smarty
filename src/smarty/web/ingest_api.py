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
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from smarty.importer import (
    AdviceUpdateNotFound,
    AdviceUpdateStale,
    ImportRejected,
    apply_import_batch,
    cache_to_catalog,
    save_cache,
    update_idea_advice_text,
)
from smarty.journal import now_iso
from smarty.version import CATEGORIES_ORDER
from smarty.web.auth import check_ingest_token

# rows_for_buffer lives under smarty.ui but has no PySide6/Qt import of its
# own (see smarty/web/app.py's note on this same import) -- safe here too.
from smarty.ui.view_model import rows_for_buffer

router = APIRouter(prefix="/api/ingest")

MAX_RECORDS_PER_SUBMISSION = 200


class IngestBody(BaseModel):
    ideas: list[dict] = []
    performance_records: list[dict] = []
    batch_id: str | None = None
    content_revision: int | None = None
    prepared_on: str | None = None


class AdviceUpdateBody(BaseModel):
    id: str
    expected_revision: int
    text: str


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
            "To enrich many existing ideas' advice text at once without risking any other field "
            "(title, categories, summary, sources, cautions...), use the advice_update_channel below "
            "instead of resubmitting whole ideas through POST /api/ingest -- it's the narrower, "
            "purpose-built tool for exactly that.",
        ],
        "advice_update_channel": {
            "purpose": "Update ONLY implementation_advice.text on an existing idea -- e.g. replacing a "
            "one-liner with Leo's expanded, more specific version -- without touching title, "
            "categories, summary, sources, cautions, originating_bots, received_date, or anything else "
            "about the idea, and without ever touching notes, status, or practical_steps (those live "
            "in a separate journal this channel never writes to, exactly like POST /api/ingest).",
            "read_endpoint": "GET /api/ingest/revisions",
            "read_auth": "Authorization: Bearer <same SMARTY_INGEST_TOKEN>",
            "read_purpose": "Current content_revision per record, nothing else: id, kind, title, "
            "content_revision. Keep review annotations out of this read -- status/notes/"
            "practical_steps are never included here; that's what GET /api/feedback is for. Call "
            "this first to get the expected_revision to send with each advice update.",
            "read_response_shape": {
                "records": [{"id": "...", "kind": "idea | performance", "title": "...", "content_revision": 1}]
            },
            "write_endpoint": "POST /api/ingest/advice",
            "write_auth": "Authorization: Bearer <same SMARTY_INGEST_TOKEN>",
            "write_body": {
                "id": "sparky-idea-<slug> -- must already exist and be an idea, not a performance record",
                "expected_revision": "the content_revision you just read via GET /api/ingest/revisions "
                "for this id -- this is a compare-and-swap, not a blind overwrite",
                "text": "the new implementation_advice.text, longer and specific",
            },
            "write_response_shape": {
                "id": "...",
                "content_revision": "the new revision (expected_revision + 1) -- verify this is what "
                "you expected before moving to the next idea",
                "implementation_advice": {
                    "kind": "bot_suggested_not_original_source_evidence",
                    "text": "exactly what was saved -- compare against what you sent to confirm it "
                    "landed correctly",
                },
            },
            "errors": {
                "401": "missing or invalid token",
                "404": "unknown id, or id belongs to a performance record (no implementation_advice "
                "field exists to edit)",
                "409": "expected_revision does not match the current content_revision -- something "
                "already changed it (another update, or your own earlier attempt). Re-read via GET "
                "/api/ingest/revisions before retrying; do not just resend the same request.",
                "422": "text missing or blank",
            },
            "retry_after_timeout": "If a request times out or the connection drops before you see a "
            "response, do not blindly resend. Call GET /api/ingest/revisions for that id first. If "
            "content_revision is still the value you started from, the write never landed -- resending "
            "the identical request is safe. If it already advanced to expected_revision + 1 and "
            "implementation_advice.text already matches what you sent, your update landed the first "
            "time -- nothing more to do. A 409 on a retry means exactly that: already applied, not a "
            "failure to react to.",
            "guarantees": [
                "Touches only implementation_advice.text. Every other field on the idea is "
                "byte-for-byte unchanged.",
                "Never touches notes, status, or practical_steps.",
                "Never reseeds or resets the catalog -- only edits the already-persisted cache in "
                "place, the same store every other read/write in this app uses.",
                "content_revision only ever moves forward by exactly 1 per successful call; a stale "
                "expected_revision is always rejected (409), never silently applied out of order, so "
                "two concurrent updates to the same id can't clobber each other unnoticed.",
            ],
        },
        "pull_buffer_channel": {
            "purpose": "The actual transfer mechanism. Rudy keeps ideas in the web UI; kept ideas sit "
            "in 'Buffered ideas waiting to be sent to Grok-Bots' until Rudy tells you to come check it "
            "-- Smarty itself never pushes anything out on its own initiative. Call this when Rudy "
            "says to check the buffer.",
            "endpoint": "GET /api/ingest/pull-buffer",
            "auth": "Authorization: Bearer <same SMARTY_INGEST_TOKEN>",
            "side_effect": "Every record returned by this call is archived (moved from the buffer into "
            "'Rudy's collection of actionable ideas') as part of the same call. This is a consuming "
            "read, unlike every other GET in this API -- calling it twice in a row normally returns "
            "data the first time and an empty list the second time, because the first call already "
            "archived everything.",
            "response_shape": {
                "records": [
                    {
                        "id": "sparky-idea-<slug>",
                        "title": "...",
                        "categories": ["..."],
                        "summary": "...",
                        "implementation_advice": {"kind": "...", "text": "..."},
                        "notes": "Rudy's own text explaining why this was kept -- may be blank",
                    }
                ],
                "pulled_at": "ISO timestamp of this pull, same value now stamped on every record "
                "returned",
            },
            "empty_buffer": "An empty buffer is not an error -- returns {\"records\": [], \"pulled_at\": "
            "...} and archives nothing.",
            "safety": "Nothing is ever lost by this call, including on a dropped connection after a "
            "successful pull: an archived record stays fully readable afterward via Rudy's web UI "
            "('Rudy's collection of actionable ideas', grouped by category then chronologically) or by "
            "asking Rudy to check there. If you're ever unsure whether a pull actually reached you, "
            "that's where to look rather than re-pulling blindly -- a second pull will come back empty "
            "for anything already archived, not re-send it.",
        },
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


def _load_cache_or_404(request: Request, content_id: str) -> tuple[dict, Path]:
    paths = request.app.state.paths
    cache_path = paths.local_catalog_dir / "current.json"
    if not cache_path.exists():
        raise HTTPException(status_code=404, detail=f"no idea with id {content_id!r}")
    cache = json.loads(cache_path.read_text(encoding="utf-8"))
    return cache, cache_path


@router.get("/revisions")
def revisions(request: Request):
    """Editorial-only read: id, kind, title, content_revision per record --
    deliberately never status/notes/practical_steps (that's GET
    /api/feedback's job; see 'Keep review annotations out of these
    editorial reads' in the schema's advice_update_channel doc). Reading
    the current revision here before calling POST /api/ingest/advice is
    how a submitter picks the correct expected_revision for the
    compare-and-swap."""
    _require_token(request)
    store = request.app.state.store
    out = []
    for idea in store.catalog.ideas:
        out.append(
            {"id": idea.id, "kind": "idea", "title": idea.title, "content_revision": idea.content_revision}
        )
    for rec in store.catalog.performance_records:
        out.append(
            {
                "id": rec.id,
                "kind": "performance",
                "title": rec.title or rec.bot,
                "content_revision": rec.content_revision,
            }
        )
    return {"records": out}


@router.post("/advice")
def update_advice(request: Request, body: AdviceUpdateBody):
    """Patch ONLY implementation_advice.text for one idea. A
    compare-and-swap on content_revision: reject (409) if expected_revision
    doesn't match current, reject (404) if the id doesn't exist or isn't an
    idea. Never reseeds/resets the catalog -- only edits the already-loaded
    cache. See GET /api/ingest/schema's advice_update_channel for the full
    contract, including safe-retry-after-timeout guidance."""
    _require_token(request)
    if not body.text or not body.text.strip():
        raise HTTPException(status_code=422, detail="text must not be empty")

    cache, cache_path = _load_cache_or_404(request, body.id)

    try:
        updated = update_idea_advice_text(cache, body.id, body.expected_revision, body.text)
    except AdviceUpdateNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except AdviceUpdateStale as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    save_cache(cache_path, cache)
    catalog = cache_to_catalog(cache)
    request.app.state.store.catalog = catalog

    return {
        "id": body.id,
        "content_revision": updated["content_revision"],
        "implementation_advice": updated["data"]["implementation_advice"],
    }


@router.get("/pull-buffer")
def pull_buffer(request: Request):
    """Rudy's "ask Leo to go check the buffer" action, from Leo's side:
    returns every currently-buffered idea (kept, not yet archived) with
    enough context to act on (title, categories, summary, advice, Rudy's
    notes), and archives all of them as a side effect of this call --
    Smarty never pushes anything on its own; this is the only way an idea
    leaves the buffer. Calling this with an empty buffer is a harmless
    no-op (returns an empty list, archives nothing).

    Nothing is lost if the response doesn't make it back to the caller: an
    archived idea stays fully readable afterward (via this same endpoint's
    archive, or the web UI's "Rudy's collection of actionable ideas"), so
    a dropped connection after a successful pull never means the data is
    gone -- just that it already moved from buffer to archive."""
    _require_token(request)
    store = request.app.state.store
    rows = rows_for_buffer(store.catalog, store)

    timestamp = now_iso()
    out = []
    for row in rows:
        idea = row.record
        us = store.user_state(row.content_id)
        out.append(
            {
                "id": idea.id,
                "title": idea.title,
                "categories": list(idea.categories),
                "summary": idea.summary,
                "implementation_advice": dict(idea.implementation_advice),
                "notes": us.notes,
            }
        )
        store.set_transferred_at(row.content_id, timestamp)

    return {"records": out, "pulled_at": timestamp}

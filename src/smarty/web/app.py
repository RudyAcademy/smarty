"""Smarty web app: a mobile-friendly, password-gated view of the same
catalog + journal the desktop app uses. Deliberately imports nothing from
smarty.ui -- no PySide6 in this process.
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER

from smarty.importer import record_first_seen_map
from smarty.models import STATUSES
from smarty.version import (
    APP_NAME,
    CATEGORIES_ORDER,
    NEW_IDEA_WINDOW_DAYS,
    WEB_ARCHIVE_LABEL,
    WEB_BUFFER_LABEL,
    WEB_PARKED_LABEL,
    WEB_REJECTED_LABEL,
)
from smarty.web.auth import require_login, web_password
from smarty.web.feedback_api import router as feedback_router
from smarty.web.ingest_api import router as ingest_router
from smarty.web.sync_api import router as sync_router
from smarty.web.webstore import build_web_store

# view_model.py lives under smarty.ui but has no PySide6/Qt import of its
# own, and importing one submodule never triggers its package siblings
# (smarty/ui/__init__.py is empty) -- so this does not pull Qt into the
# web process. Note: rows_for_category/rows_for_status_view/STATUS_VIEW_*
# are shared with the desktop app and are NOT changed here -- the web-only
# buffer/archive/unreviewed-only-categories behavior is layered on top in
# this file instead, so desktop keeps its existing simpler behavior.
from smarty.ui.view_model import (
    filter_rows,
    rows_for_archive,
    rows_for_buffer,
    rows_for_category,
    rows_for_status_view,
    sort_rows,
)

BASE_DIR = Path(__file__).parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    store, paths = build_web_store()
    app.state.store = store
    app.state.paths = paths
    yield


app = FastAPI(title=APP_NAME, lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=os.environ.get("SMARTY_SESSION_SECRET", os.urandom(32).hex()))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(sync_router)
app.include_router(ingest_router)
app.include_router(feedback_router)

# Web-only tile order: the buffer is the very first button in the menu,
# then the 7 content categories (unreviewed-only here -- once an idea is
# kept/parked/rejected it leaves these lists entirely and lives only in
# its bucket), then Parked and Rejected. The archive ("Rudy's collection
# of actionable ideas") is deliberately NOT one of these indexed tiles --
# it needs grouped-by-category rendering, so it gets its own /archive
# route and template instead.
TILES = (
    [("buffer", WEB_BUFFER_LABEL)]
    + [("category", label) for label in CATEGORIES_ORDER]
    + [("parked", WEB_PARKED_LABEL), ("rejected", WEB_REJECTED_LABEL)]
)


def _tile_label(index: int) -> str:
    return TILES[index][1]


def _rows_for_tile(index: int):
    kind, label = TILES[index]
    store = app.state.store
    catalog = store.catalog
    if kind == "buffer":
        return rows_for_buffer(catalog, store)
    if kind == "category":
        rows = rows_for_category(catalog, store, label)
        return [r for r in rows if r.status == "unreviewed"]
    if kind == "parked":
        return rows_for_status_view(catalog, store, "park_it_for_later")
    return rows_for_status_view(catalog, store, "rejected_recoverable")


def _is_new(content_id: str, status: str, first_seen_map: dict) -> bool:
    """NEW badge rule: still unreviewed, and first added within the
    configured window. Once you act on it (kept/parked/rejected), the
    status badge already says what happened, so NEW adds no value."""
    if status != "unreviewed":
        return False
    first_seen = first_seen_map.get(content_id)
    if not first_seen:
        return False
    try:
        seen_at = datetime.fromisoformat(first_seen)
    except ValueError:
        return False
    return datetime.now(timezone.utc) - seen_at <= timedelta(days=NEW_IDEA_WINDOW_DAYS)


def _back_url(from_tile: str) -> str:
    if from_tile == "archive":
        return "/archive"
    return f"/tile/{from_tile}"


def _status_conflict_text(us) -> str | None:
    if not us.is_conflicted("status"):
        return None
    return ", ".join(f"{v} ({dev})" for v, dev, _ in us.conflicts["status"])


def _first_seen_map() -> dict:
    paths = app.state.paths
    cache_path = paths.local_catalog_dir / "current.json"
    if not cache_path.exists():
        return {}
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return record_first_seen_map(cache)


def _record_view(content_id: str) -> dict | None:
    store = app.state.store
    for idea in store.catalog.ideas:
        if idea.id == content_id:
            advice_text = idea.implementation_advice.get("text")
            # The real seed data has summary == "{title}: {advice}" for every
            # idea, so showing both the summary paragraph and a separate
            # "bot suggestion" box repeats the same sentence (and the title)
            # twice. Once Grok-bot starts submitting a summary genuinely
            # distinct from the advice, this stops matching and both show.
            summary_is_redundant = idea.summary == f"{idea.title}: {advice_text}"
            return {
                "kind": "idea",
                "id": idea.id,
                "title": idea.title,
                "bots": ", ".join(idea.originating_bots),
                "period_start": idea.received_period.start,
                "period_end": idea.received_period.end,
                "summary": idea.summary,
                "advice_text": advice_text,
                "summary_is_redundant": summary_is_redundant,
                "sources": [s.get("url", "") for s in idea.sources],
                "missing_source_note": idea.missing_source_note,
                "cautions": list(idea.cautions),
                "caveats": [],
                "verification_status": idea.verification_status,
            }
    for rec in store.catalog.performance_records:
        if rec.id == content_id:
            return {
                "kind": "performance",
                "id": rec.id,
                "title": rec.title or rec.bot,
                "bots": rec.bot,
                "period_start": rec.received_period.start,
                "period_end": rec.received_period.end,
                "summary": rec.summary,
                "advice_text": None,
                "summary_is_redundant": False,
                "sources": [],
                "missing_source_note": None,
                "cautions": [],
                "caveats": list(rec.caveats),
                "verification_status": rec.verification_status,
            }
    return None


@app.get("/login")
def login_form(request: Request, next: str = "/"):
    return templates.TemplateResponse(
        request, "login.html", {"logged_in": False, "next_url": next, "error": None}
    )


@app.post("/login")
def login_submit(request: Request, password: str = Form(...), next: str = Form("/")):
    if password == web_password():
        request.session["authenticated"] = True
        return RedirectResponse(url=next or "/", status_code=HTTP_303_SEE_OTHER)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"logged_in": False, "next_url": next, "error": "Wrong password."},
        status_code=401,
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=HTTP_303_SEE_OTHER)


@app.get("/")
def index(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    first_seen = _first_seen_map()
    tiles = []
    for i in range(len(TILES)):
        rows = _rows_for_tile(i)
        new_count = sum(1 for r in rows if _is_new(r.content_id, r.status, first_seen))
        tiles.append({"index": i, "label": _tile_label(i), "count": len(rows), "new_count": new_count})
    archive_count = len(rows_for_archive(store.catalog, store))
    return templates.TemplateResponse(
        request,
        "index.html",
        {"logged_in": True, "tiles": tiles, "archive_label": WEB_ARCHIVE_LABEL, "archive_count": archive_count},
    )


@app.get("/tile/{tile_index}")
def tile_view(request: Request, tile_index: int, q: str = ""):
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    rows = _rows_for_tile(tile_index)
    rows = filter_rows(rows, search=q, store=store)
    rows = sort_rows(rows, newest_first=True)
    first_seen = _first_seen_map()
    new_ids = {r.content_id for r in rows if _is_new(r.content_id, r.status, first_seen)}
    return templates.TemplateResponse(
        request,
        "tile.html",
        {
            "logged_in": True,
            "tile_index": tile_index,
            "tile_label": _tile_label(tile_index),
            "query": q,
            "rows": rows,
            "new_ids": new_ids,
        },
    )


@app.get("/archive")
def archive_view(request: Request):
    """Rudy's collection of actionable ideas -- kept ideas already pulled
    by Grok-bot, grouped by category then newest-received-first within
    each category (same tie-break rule as everywhere else: title, then
    id, when the period matches)."""
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    rows = rows_for_archive(store.catalog, store)

    groups: list[dict] = []
    for label in CATEGORIES_ORDER:
        group_rows = [r for r in rows if label in getattr(r.record, "categories", ())]
        if group_rows:
            groups.append({"label": label, "rows": sort_rows(group_rows, newest_first=True)})

    return templates.TemplateResponse(
        request,
        "archive.html",
        {"logged_in": True, "label": WEB_ARCHIVE_LABEL, "groups": groups},
    )


@app.get("/record/{content_id}")
def record_view(
    request: Request, content_id: str, from_tile: str = "0", saved: bool = False, error: str = ""
):
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    record = _record_view(content_id)
    if record is None:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    us = store.user_state(content_id)
    is_new = _is_new(content_id, us.status, _first_seen_map())
    return templates.TemplateResponse(
        request,
        "record.html",
        {
            "logged_in": True,
            "record": record,
            "from_tile": from_tile,
            "back_url": _back_url(from_tile),
            "statuses": STATUSES,
            "current_status": us.status,
            "status_conflict": _status_conflict_text(us),
            "notes": us.notes,
            "transferred_at": us.transferred_at,
            "is_new": is_new,
            "saved": saved,
            "error": error or None,
        },
    )


@app.post("/record/{content_id}/save")
def save_record(
    request: Request,
    content_id: str,
    status: str = Form(...),
    notes: str = Form(""),
    from_tile: str = Form("0"),
):
    """Unified save: status and notes submit together, exactly once, so a
    status click can never discard an unsaved note (the old separate
    /status and /notes endpoints made that possible via an intermediate
    reload -- this replaces both). The two-click reject confirmation now
    happens client-side in record.html's JS before the form ever submits,
    so by the time this runs, "rejected" already means confirmed.

    Validation: notes can't be saved while status is (or would stay)
    "unreviewed" -- re-renders the same page with the typed notes still
    in the box and an error banner, rather than redirecting (a redirect
    would reload from the journal and lose the unsaved text)."""
    redirect = require_login(request)
    if redirect:
        return redirect
    if status not in STATUSES:
        raise HTTPException(status_code=400, detail=f"unknown status: {status!r}")

    store = app.state.store
    record = _record_view(content_id)
    if record is None:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    us = store.user_state(content_id)

    if notes.strip() and status == "unreviewed":
        is_new = _is_new(content_id, us.status, _first_seen_map())
        return templates.TemplateResponse(
            request,
            "record.html",
            {
                "logged_in": True,
                "record": record,
                "from_tile": from_tile,
                "back_url": _back_url(from_tile),
                "statuses": STATUSES,
                "current_status": us.status,
                "status_conflict": _status_conflict_text(us),
                "notes": notes,
                "transferred_at": us.transferred_at,
                "is_new": is_new,
                "saved": False,
                "error": "Please choose kept, parked, or rejected before saving a note.",
            },
            status_code=422,
        )

    if notes != us.notes:
        store.set_notes(content_id, notes)
    # Always go through set_status when the saved state is "kept" -- even
    # if it already was -- because Store.set_status is what clears
    # transferred_at. Editing notes on an already-archived kept idea and
    # saving is a new, worth-reporting decision, so it should re-enter the
    # buffer, not stay silently archived.
    if status != us.status or status == "kept":
        store.set_status(content_id, status)

    return RedirectResponse(
        url=f"/record/{content_id}?from_tile={from_tile}&saved=1", status_code=HTTP_303_SEE_OTHER
    )


@app.post("/record/{content_id}/steps")
def set_steps(request: Request, content_id: str, practical_steps: str = Form(""), from_tile: int = Form(0)):
    redirect = require_login(request)
    if redirect:
        return redirect
    app.state.store.set_practical_steps(content_id, practical_steps)
    return RedirectResponse(url=f"/record/{content_id}?from_tile={from_tile}", status_code=HTTP_303_SEE_OTHER)

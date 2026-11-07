"""Smarty web app: a mobile-friendly, password-gated view of the same
catalog + journal the desktop app uses. Deliberately imports nothing from
smarty.ui -- no PySide6 in this process.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.status import HTTP_303_SEE_OTHER

from smarty.models import STATUSES
from smarty.version import APP_NAME, CATEGORIES_ORDER, STATUS_VIEWS_ORDER
from smarty.web.auth import require_login, web_password
from smarty.web.sync_api import router as sync_router
from smarty.web.webstore import build_web_store

# view_model.py lives under smarty.ui but has no PySide6/Qt import of its
# own, and importing one submodule never triggers its package siblings
# (smarty/ui/__init__.py is empty) -- so this does not pull Qt into the
# web process.
from smarty.ui.view_model import (
    STATUS_VIEW_LABELS,
    filter_rows,
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

TILES = [("category", label) for label in CATEGORIES_ORDER] + [
    ("status_view", key) for key in STATUS_VIEWS_ORDER
]


def _tile_label(index: int) -> str:
    kind, key = TILES[index]
    if kind == "category":
        return key
    return STATUS_VIEW_LABELS[key]


def _rows_for_tile(index: int):
    kind, key = TILES[index]
    store = app.state.store
    catalog = store.catalog
    if kind == "category":
        return rows_for_category(catalog, store, key)
    return rows_for_status_view(catalog, store, key)


def _record_view(content_id: str) -> dict | None:
    store = app.state.store
    for idea in store.catalog.ideas:
        if idea.id == content_id:
            return {
                "kind": "idea",
                "id": idea.id,
                "title": idea.title,
                "bots": ", ".join(idea.originating_bots),
                "period_start": idea.received_period.start,
                "period_end": idea.received_period.end,
                "summary": idea.summary,
                "advice_text": idea.implementation_advice.get("text"),
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
    tiles = []
    for i in range(len(TILES)):
        tiles.append({"index": i, "label": _tile_label(i), "count": len(_rows_for_tile(i))})
    return templates.TemplateResponse(request, "index.html", {"logged_in": True, "tiles": tiles})


@app.get("/tile/{tile_index}")
def tile_view(request: Request, tile_index: int, q: str = ""):
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    rows = _rows_for_tile(tile_index)
    rows = filter_rows(rows, search=q, store=store)
    rows = sort_rows(rows, newest_first=True)
    return templates.TemplateResponse(
        request,
        "tile.html",
        {
            "logged_in": True,
            "tile_index": tile_index,
            "tile_label": _tile_label(tile_index),
            "query": q,
            "rows": rows,
        },
    )


@app.get("/record/{content_id}")
def record_view(request: Request, content_id: str, from_tile: int = 0, reject_armed: bool = False):
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    record = _record_view(content_id)
    if record is None:
        return RedirectResponse(url="/", status_code=HTTP_303_SEE_OTHER)
    us = store.user_state(content_id)
    status_conflict = None
    if us.is_conflicted("status"):
        status_conflict = ", ".join(f"{v} ({dev})" for v, dev, _ in us.conflicts["status"])
    return templates.TemplateResponse(
        request,
        "record.html",
        {
            "logged_in": True,
            "record": record,
            "from_tile": from_tile,
            "statuses": STATUSES,
            "current_status": us.status,
            "status_conflict": status_conflict,
            "notes": us.notes,
            "practical_steps": us.practical_steps,
            "reject_armed": reject_armed,
        },
    )


@app.post("/record/{content_id}/status")
def set_status(
    request: Request,
    content_id: str,
    status: str = Form(...),
    from_tile: int = Form(0),
    confirm: str = Form(""),
):
    redirect = require_login(request)
    if redirect:
        return redirect
    store = app.state.store
    if status == "rejected" and confirm != "1":
        return RedirectResponse(
            url=f"/record/{content_id}?from_tile={from_tile}&reject_armed=1", status_code=HTTP_303_SEE_OTHER
        )
    store.set_status(content_id, status)
    return RedirectResponse(url=f"/record/{content_id}?from_tile={from_tile}", status_code=HTTP_303_SEE_OTHER)


@app.post("/record/{content_id}/notes")
def set_notes(request: Request, content_id: str, notes: str = Form(""), from_tile: int = Form(0)):
    redirect = require_login(request)
    if redirect:
        return redirect
    app.state.store.set_notes(content_id, notes)
    return RedirectResponse(url=f"/record/{content_id}?from_tile={from_tile}", status_code=HTTP_303_SEE_OTHER)


@app.post("/record/{content_id}/steps")
def set_steps(request: Request, content_id: str, practical_steps: str = Form(""), from_tile: int = Form(0)):
    redirect = require_login(request)
    if redirect:
        return redirect
    app.state.store.set_practical_steps(content_id, practical_steps)
    return RedirectResponse(url=f"/record/{content_id}?from_tile={from_tile}", status_code=HTTP_303_SEE_OTHER)

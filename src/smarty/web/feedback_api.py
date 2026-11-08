"""Reverse channel: lets an automated reader (e.g. Grok-bot) pull Rudy's
status/notes feedback on ideas it previously submitted via /api/ingest --
what got kept, parked, rejected, and why.

Read-only: this endpoint never writes anything. It reduces the journal the
same way the UI does (smarty.store.Store.user_state), so it reports
exactly what a person would see on screen, never a raw operation log.

Shares SMARTY_INGEST_TOKEN with /api/ingest on purpose -- both directions
belong to the same automated counterpart (Grok-bot), so one secret covers
reading feedback and submitting new ideas. Revoking that one token cuts
off both directions together, which is the correct blast radius: there's
no scenario where Grok-bot should keep reading feedback after being cut
off from submitting, or vice versa.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from smarty.models import STATUSES
from smarty.web.auth import check_ingest_token

router = APIRouter(prefix="/api/feedback")


def _require_token(request: Request) -> None:
    if not check_ingest_token(request):
        raise HTTPException(status_code=401, detail="missing/invalid ingest bearer token")


def _record_summary(store, content_id: str, title: str, kind: str) -> dict:
    us = store.user_state(content_id)
    entry = {
        "id": content_id,
        "kind": kind,
        "title": title,
        "status": us.status,
        "notes": us.notes,
        "practical_steps": us.practical_steps,
    }
    if us.is_conflicted("status"):
        entry["status_conflict"] = [
            {"value": v, "device": dev, "at": t} for v, dev, t in us.conflicts["status"]
        ]
    return entry


@router.get("")
def feedback(request: Request, status: str | None = None, include_all: bool = False):
    """Returns Rudy's current status/notes per record.

    By default, only records that have actually been reviewed (status is
    not "unreviewed", or notes/practical_steps are non-blank) are
    returned -- an untouched record isn't feedback yet. Pass
    `include_all=true` to get every record including untouched ones, or
    `status=kept` (etc.) to filter to one status.
    """
    _require_token(request)

    if status is not None and status not in STATUSES:
        raise HTTPException(status_code=400, detail=f"status must be one of {STATUSES}")

    store = request.app.state.store
    out = []
    for idea in store.catalog.ideas:
        entry = _record_summary(store, idea.id, idea.title, "idea")
        out.append(entry)
    for rec in store.catalog.performance_records:
        entry = _record_summary(store, rec.id, rec.title or rec.bot, "performance")
        out.append(entry)

    if not include_all:
        out = [e for e in out if e["status"] != "unreviewed" or e["notes"] or e["practical_steps"]]
    if status is not None:
        out = [e for e in out if e["status"] == status]

    return {"records": out}

"""HTTP journal sync: lets the laptop pull/push operations against this
hosted copy, instead of (or in addition to) the LAN-only T:\\ share. Same
union-by-op-id, keep-both-on-conflict rules as the filesystem-based sync --
this just moves the "shared root" onto an HTTPS endpoint.

Authenticated with a bearer token (SMARTY_SYNC_TOKEN), separate from the
browser session password -- a laptop syncing in the background shouldn't
need a human to click through a login page.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from smarty.journal import Operation
from smarty.web.auth import check_sync_token

router = APIRouter(prefix="/api/sync")


class PushBody(BaseModel):
    ops: list[dict]


def _require_token(request: Request) -> None:
    if not check_sync_token(request):
        raise HTTPException(status_code=401, detail="missing/invalid sync bearer token")


@router.get("/pull")
def pull(request: Request):
    _require_token(request)
    store = request.app.state.store
    return {"ops": [op.to_dict() for op in store.all_operations]}


@router.post("/push")
def push(request: Request, body: PushBody):
    _require_token(request)
    store = request.app.state.store
    paths = request.app.state.paths

    incoming = [Operation.from_dict(d) for d in body.ops]
    known_ids = {op.op_id for op in store.all_operations}
    new_ops = [op for op in incoming if op.op_id not in known_ids]

    from smarty.journal import append_operation

    for op in new_ops:
        append_operation(paths.local_journal_path, op)
    store.reload_journal()

    return {"merged": len(new_ops), "ops": [op.to_dict() for op in store.all_operations]}

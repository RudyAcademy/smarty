"""Shared-password gate for the hosted web app.

Not an account system: one password, set via the SMARTY_WEB_PASSWORD env
var, required before any page loads. A session cookie (signed, via
Starlette's SessionMiddleware) remembers that you entered it.

Two other, separate bearer tokens exist, each checked per-request instead
of via a browser session, and each independently revocable:
- SMARTY_SYNC_TOKEN -- the laptop's "Sync to cloud" button (read/write the
  journal).
- SMARTY_INGEST_TOKEN -- an automated submitter (e.g. Grok-bot) adding new
  ideas via /api/ingest. Deliberately a different secret from the sync
  token: revoking a misbehaving automated submitter should never also log
  out the laptop's own sync.
"""

from __future__ import annotations

import os

from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.status import HTTP_303_SEE_OTHER


def web_password() -> str:
    pw = os.environ.get("SMARTY_WEB_PASSWORD")
    if not pw:
        raise RuntimeError("SMARTY_WEB_PASSWORD must be set before the web app will start")
    return pw


def sync_token() -> str | None:
    return os.environ.get("SMARTY_SYNC_TOKEN")


def ingest_token() -> str | None:
    return os.environ.get("SMARTY_INGEST_TOKEN")


def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("authenticated"))


def require_login(request: Request) -> RedirectResponse | None:
    """Call at the top of a route; returns a redirect if not logged in, else None."""
    if not is_logged_in(request):
        return RedirectResponse(url=f"/login?next={request.url.path}", status_code=HTTP_303_SEE_OTHER)
    return None


def _check_bearer(request: Request, expected: str | None) -> bool:
    if not expected:
        return False
    header = request.headers.get("authorization", "")
    return header == f"Bearer {expected}"


def check_sync_token(request: Request) -> bool:
    return _check_bearer(request, sync_token())


def check_ingest_token(request: Request) -> bool:
    return _check_bearer(request, ingest_token())

"""Shared-password gate for the hosted web app.

Not an account system: one password, set via the SMARTY_WEB_PASSWORD env
var, required before any page loads. A session cookie (signed, via
Starlette's SessionMiddleware) remembers that you entered it. The sync API
(laptop <-> cloud) uses a separate bearer token, SMARTY_SYNC_TOKEN, checked
per-request instead of via a browser session.
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


def is_logged_in(request: Request) -> bool:
    return bool(request.session.get("authenticated"))


def require_login(request: Request) -> RedirectResponse | None:
    """Call at the top of a route; returns a redirect if not logged in, else None."""
    if not is_logged_in(request):
        return RedirectResponse(url=f"/login?next={request.url.path}", status_code=HTTP_303_SEE_OTHER)
    return None


def check_sync_token(request: Request) -> bool:
    expected = sync_token()
    if not expected:
        return False
    header = request.headers.get("authorization", "")
    return header == f"Bearer {expected}"

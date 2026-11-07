"""Sync the local journal against the hosted web app over HTTPS, instead
of (or alongside) the LAN-only T:\\ share. Same union-by-op-id merge the
NAS sync uses -- just reached via smarty.web.sync_api's /api/sync/pull and
/api/sync/push instead of a mounted file.

Uses only the standard library (urllib) so the desktop app picks up no
new runtime dependency for this.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass

from smarty.journal import Operation
from smarty.paths import SmartyPaths
from smarty.store import Store

DEFAULT_TIMEOUT = 10.0


@dataclass
class CloudSyncResult:
    outcome: str  # "not_configured" | "ok" | "unauthorized" | "offline" | "error"
    detail: str = ""
    pulled: int = 0
    pushed: int = 0


def _request(url: str, token: str, *, method: str = "GET", body: dict | None = None, timeout: float = DEFAULT_TIMEOUT):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sync_with_cloud(store: Store, paths: SmartyPaths, timeout: float = DEFAULT_TIMEOUT) -> CloudSyncResult:
    if not paths.cloud_sync_url or not paths.cloud_sync_token:
        return CloudSyncResult(outcome="not_configured")

    base = paths.cloud_sync_url.rstrip("/")
    token = paths.cloud_sync_token

    try:
        pull_result = _request(f"{base}/api/sync/pull", token, timeout=timeout)
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return CloudSyncResult(outcome="unauthorized", detail="bad SPARKY_CLOUD_SYNC_TOKEN")
        return CloudSyncResult(outcome="error", detail=f"pull failed: HTTP {exc.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return CloudSyncResult(outcome="offline", detail=f"could not reach cloud: {exc}")

    remote_ops = [Operation.from_dict(d) for d in pull_result.get("ops", [])]
    known_before = {op.op_id for op in store.all_operations}
    store.merge_remote_ops(remote_ops)
    pulled = len({op.op_id for op in remote_ops} - known_before)

    local_ops = [op.to_dict() for op in store.all_operations]
    try:
        push_result = _request(
            f"{base}/api/sync/push", token, method="POST", body={"ops": local_ops}, timeout=timeout
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 401:
            return CloudSyncResult(outcome="unauthorized", detail="bad SPARKY_CLOUD_SYNC_TOKEN", pulled=pulled)
        return CloudSyncResult(outcome="error", detail=f"push failed: HTTP {exc.code}", pulled=pulled)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return CloudSyncResult(outcome="offline", detail=f"could not reach cloud: {exc}", pulled=pulled)

    # The push response includes the server's full, now-merged op set --
    # merge it back in case anything landed there between our pull and push.
    server_ops = [Operation.from_dict(d) for d in push_result.get("ops", [])]
    before_final = {op.op_id for op in store.all_operations}
    store.merge_remote_ops(server_ops)
    pulled += len({op.op_id for op in server_ops} - before_final)

    return CloudSyncResult(outcome="ok", pulled=pulled, pushed=len(local_ops))

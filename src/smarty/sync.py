"""Syncing the user-state journal with the shared NAS root.

Startup must never hang on a dead share: every network-touching step runs
under a bounded timeout and failures degrade to "stay on local state,
report offline/stale" rather than raising.
"""

from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from smarty.journal import Operation, read_journal, union_ops
from smarty.paths import SmartyPaths
from smarty.store import Store

DEFAULT_SHARE_PROBE_TIMEOUT = 5.0
DEFAULT_REFRESH_TIMEOUT = 10.0
DEFAULT_LOCK_WAIT_TIMEOUT = 2.0
DEFAULT_LOCK_LEASE_SECONDS = 30.0
DEFAULT_MAX_AUTO_BACKUPS = 5

_executor = ThreadPoolExecutor(max_workers=4)


@dataclass
class SyncConfig:
    share_probe_timeout: float = DEFAULT_SHARE_PROBE_TIMEOUT
    refresh_timeout: float = DEFAULT_REFRESH_TIMEOUT
    lock_wait_timeout: float = DEFAULT_LOCK_WAIT_TIMEOUT
    lock_lease_seconds: float = DEFAULT_LOCK_LEASE_SECONDS
    max_auto_backups: int = DEFAULT_MAX_AUTO_BACKUPS


@dataclass
class SyncResult:
    outcome: str  # "ok" | "offline" | "no_data_dir" | "locked" | "read_only" | "error"
    detail: str = ""
    new_remote_ops: int = 0
    damaged_lines_seen: int = 0


def _run_with_timeout(fn, timeout: float, default):
    future = _executor.submit(fn)
    try:
        return future.result(timeout=timeout)
    except (FutureTimeoutError, OSError):
        return default


def probe_share(paths: SmartyPaths, timeout: float) -> bool:
    return _run_with_timeout(lambda: paths.nas_root.exists(), timeout, False)


def nas_data_present(paths: SmartyPaths, timeout: float) -> bool:
    """True only if the NAS data dir already exists. Never creates it."""
    return _run_with_timeout(lambda: paths.nas_data_dir.exists(), timeout, False)


class _LockLease:
    """A file-based lock with an expiring lease, so a crash can't block the share forever."""

    def __init__(self, lock_path: Path, device_id: str, lease_seconds: float):
        self.lock_path = lock_path
        self.device_id = device_id
        self.lease_seconds = lease_seconds
        self._held = False

    def acquire(self, wait_timeout: float) -> bool:
        deadline = time.monotonic() + wait_timeout
        while True:
            if self._try_once():
                return True
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.1)

    def _try_once(self) -> bool:
        try:
            fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w") as f:
                f.write(f"{self.device_id}:{time.time()}")
            self._held = True
            return True
        except FileExistsError:
            pass
        except OSError:
            return False

        try:
            stat = self.lock_path.stat()
            age = time.time() - stat.st_mtime
        except OSError:
            return False
        if age > self.lease_seconds:
            try:
                self.lock_path.unlink()
            except OSError:
                return False
            return self._try_once()
        return False

    def release(self) -> None:
        if not self._held:
            return
        try:
            self.lock_path.unlink()
        except OSError:
            pass
        self._held = False


def _backup_shared_journal(paths: SmartyPaths, current_bytes: bytes, max_backups: int) -> None:
    backups_dir = paths.nas_data_dir / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup_path = backups_dir / f"journal-{stamp}.jsonl.bak"
    backup_path.write_bytes(current_bytes)

    auto_backups = sorted(backups_dir.glob("journal-*.jsonl.bak"))
    excess = len(auto_backups) - max_backups
    for old in auto_backups[:max(excess, 0)]:
        try:
            old.unlink()
        except OSError:
            pass


def _atomic_write_journal(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def sync_notes_journal(store: Store, paths: SmartyPaths, config: SyncConfig | None = None) -> SyncResult:
    config = config or SyncConfig()

    if not probe_share(paths, config.share_probe_timeout):
        return SyncResult(outcome="offline", detail="NAS root not reachable within timeout")

    if not nas_data_present(paths, config.share_probe_timeout):
        return SyncResult(outcome="no_data_dir", detail=f"{paths.nas_data_dir} does not exist yet")

    lock = _LockLease(paths.nas_lock_path, paths.device_id, config.lock_lease_seconds)
    if not lock.acquire(config.lock_wait_timeout):
        # Still read-only merge what we can without the lock, but do not publish.
        try:
            remote_ops, damaged = read_journal(paths.nas_journal_path)
        except OSError:
            return SyncResult(outcome="locked", detail="could not read while locked")
        store.merge_remote_ops(remote_ops)
        return SyncResult(
            outcome="locked",
            detail="lock busy; merged remote read-only, did not publish",
            new_remote_ops=len(remote_ops),
            damaged_lines_seen=len(damaged),
        )

    try:
        try:
            remote_ops, damaged = read_journal(paths.nas_journal_path)
            current_bytes = (
                paths.nas_journal_path.read_bytes() if paths.nas_journal_path.exists() else b""
            )
        except OSError as exc:
            return SyncResult(outcome="read_only", detail=f"could not read shared journal: {exc}")

        local_ops, local_damaged = read_journal(paths.local_journal_path)
        merged = union_ops(local_ops, remote_ops)

        try:
            if current_bytes:
                _backup_shared_journal(paths, current_bytes, config.max_auto_backups)
            text = "\n".join(op.to_json_line() for op in merged)
            if text:
                text += "\n"
            for raw in damaged:
                text += raw + "\n"
            _atomic_write_journal(paths.nas_journal_path, text)
        except OSError as exc:
            store.merge_remote_ops(remote_ops)
            return SyncResult(
                outcome="read_only",
                detail=f"share is read-only, merged locally only: {exc}",
                new_remote_ops=len(remote_ops),
                damaged_lines_seen=len(damaged),
            )

        reread_ops, reread_damaged = read_journal(paths.nas_journal_path)
        store.merge_remote_ops(reread_ops)

        return SyncResult(
            outcome="ok",
            new_remote_ops=len(remote_ops),
            damaged_lines_seen=len(damaged) + len(local_damaged) + len(reread_damaged),
        )
    finally:
        lock.release()

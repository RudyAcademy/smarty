"""Self-update: stage a versioned zip, verify its hash, smoke-check it, then
switch the "current version" pointer. The previous version is left in place
until a new build passes its smoke check, so a bad build can't strand the
user, and a downgrade is refused outright.

A checksum here proves integrity (the bytes match what the manifest says),
not a publisher signature -- this module never claims more than that.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path

ZIP_NAME_RE = re.compile(r"^Smarty_v(\d+)\.(\d+)\.(\d+)\.zip$")


class UpdateRejected(ValueError):
    pass


def parse_version(version: str) -> tuple[int, int, int]:
    parts = version.split(".")
    if len(parts) != 3:
        raise UpdateRejected(f"not a semantic version: {version!r}")
    try:
        return tuple(int(p) for p in parts)  # type: ignore[return-value]
    except ValueError as exc:
        raise UpdateRejected(f"not a semantic version: {version!r}") from exc


def validate_zip_filename(name: str) -> str:
    m = ZIP_NAME_RE.match(name)
    if not m:
        raise UpdateRejected(f"rejected update filename (must be Smarty_vX.Y.Z.zip): {name!r}")
    return f"{m.group(1)}.{m.group(2)}.{m.group(3)}"


def sha256_of_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_manifest(manifest: dict) -> None:
    required = ("version", "zip", "sha256")
    missing = [k for k in required if k not in manifest]
    if missing:
        raise UpdateRejected(f"update manifest missing field(s): {missing}")
    validate_zip_filename(manifest["zip"])
    parse_version(manifest["version"])


def is_downgrade(installed_version: str, candidate_version: str) -> bool:
    return parse_version(candidate_version) <= parse_version(installed_version)


@dataclass
class StageResult:
    ok: bool
    version: str | None = None
    detail: str = ""


def stage_update(
    *,
    source_zip: Path,
    manifest: dict,
    installed_version: str,
    versions_dir: Path,
    smoke_check,
) -> StageResult:
    """Copy+verify+extract a zip already staged locally (never run directly
    from a mapped share), then smoke-check it before switching anything."""
    validate_manifest(manifest)
    candidate_version = manifest["version"]

    if is_downgrade(installed_version, candidate_version):
        return StageResult(ok=False, detail=f"refusing downgrade {installed_version} -> {candidate_version}")

    actual_hash = sha256_of_file(source_zip)
    if actual_hash != manifest["sha256"]:
        return StageResult(ok=False, detail="sha256 mismatch; zip not applied")

    version_dir = versions_dir / candidate_version
    if version_dir.exists():
        shutil.rmtree(version_dir)
    version_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(source_zip) as zf:
        zf.extractall(version_dir)

    if not smoke_check(version_dir):
        shutil.rmtree(version_dir, ignore_errors=True)
        return StageResult(ok=False, detail="smoke check failed; previous version left in place")

    return StageResult(ok=True, version=candidate_version)


def switch_current_version(versions_dir: Path, version: str) -> None:
    pointer = versions_dir / "current_version.txt"
    tmp = pointer.with_suffix(".tmp")
    tmp.write_text(version, encoding="utf-8")
    tmp.replace(pointer)


def read_current_version(versions_dir: Path, fallback: str) -> str:
    pointer = versions_dir / "current_version.txt"
    if not pointer.exists():
        return fallback
    return pointer.read_text(encoding="utf-8").strip() or fallback


def default_smoke_check(version_dir: Path) -> bool:
    """Minimal smoke check: the extracted tree has something runnable."""
    exe_candidates = list(version_dir.glob("**/Smarty.exe")) + list(version_dir.glob("**/*.pyz"))
    py_entry = list(version_dir.glob("**/__main__.py")) + list(version_dir.glob("**/smarty/ui/app.py"))
    return bool(exe_candidates or py_entry)


def publish_update_manifest(
    *,
    installers_dir: Path,
    zip_path: Path,
    version: str,
    built_on: str,
    windows_installer: bool,
) -> dict:
    """Publish latest.json only after the zip is already in place and its
    hash verified -- callers must copy/verify the zip into installers_dir
    before calling this."""
    final_zip = installers_dir / zip_path.name
    if not final_zip.exists():
        raise UpdateRejected("zip must already be staged in installers_dir before publishing manifest")

    manifest = {
        "version": version,
        "zip": zip_path.name,
        "sha256": sha256_of_file(final_zip),
        "windows_installer": windows_installer,
        "built_on": built_on,
    }
    validate_manifest(manifest)

    manifest_path = installers_dir / "latest.json"
    tmp = manifest_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(manifest_path)

    # Re-read to confirm what's on disk, as the behavior spec requires.
    reread = json.loads(manifest_path.read_text(encoding="utf-8"))
    if reread != manifest:
        raise UpdateRejected("manifest re-read mismatch after publish")
    return manifest

"""Path and device configuration.

Legacy config file name (``sparky-paths.json``) and legacy environment variable
names (``SPARKY_LOCAL_ROOT``, ``SPARKY_NAS_ROOT``, ``SPARKY_CONFIG``,
``SPARKY_DEVICE_ID``, ``SPARKY_DEVICE_LABEL``) are kept on purpose so that a
future Smarty build stays compatible with files written under the old
"Sparky" internal name. The product name shown to the user is always Smarty.

No path here is ever hardcoded to a specific UNC address. The shared root is
whatever drive letter or path the caller configures (default: ``T:\\TowerHill\\Sparky``,
which is only a drive-letter path, never resolved to a UNC by this code).
"""

from __future__ import annotations

import json
import os
import uuid
from dataclasses import dataclass
from pathlib import Path

DEFAULT_LOCAL_ROOT = Path(r"C:\TowerHill\Grok-Bot-data\business-ideas")
DEFAULT_NAS_ROOT = Path(r"T:\TowerHill\Sparky")
LEGACY_CONFIG_FILENAME = "sparky-paths.json"


@dataclass(frozen=True)
class SmartyPaths:
    local_root: Path
    nas_root: Path
    device_id: str
    device_label: str
    # Optional: syncing against the hosted web app (over HTTPS) instead of
    # or in addition to the LAN-only T:\ share. Both unset by default --
    # nothing changes for anyone who hasn't configured cloud sync.
    cloud_sync_url: str | None = None
    cloud_sync_token: str | None = None

    @property
    def local_catalog_dir(self) -> Path:
        return self.local_root / "catalog"

    @property
    def local_state_dir(self) -> Path:
        return self.local_root / "state"

    @property
    def local_journal_path(self) -> Path:
        return self.local_state_dir / "journal.jsonl"

    @property
    def local_app_manifest_path(self) -> Path:
        return self.local_state_dir / "app-manifest.json"

    @property
    def local_backups_dir(self) -> Path:
        return self.local_state_dir / "backups"

    @property
    def nas_data_dir(self) -> Path:
        return self.nas_root / "Data"

    @property
    def nas_installers_dir(self) -> Path:
        return self.nas_root / "Installers"

    @property
    def nas_journal_path(self) -> Path:
        return self.nas_data_dir / "journal.jsonl"

    @property
    def nas_lock_path(self) -> Path:
        return self.nas_data_dir / "journal.lock"

    @property
    def nas_catalog_manifest_path(self) -> Path:
        return self.nas_data_dir / "catalog-manifest.json"

    @property
    def nas_update_manifest_path(self) -> Path:
        return self.nas_installers_dir / "latest.json"


def _default_device_id() -> str:
    node = uuid.getnode()
    return f"dev-{node:012x}"


def _default_device_label() -> str:
    # Deliberately blank, not the hostname: a device label is something a
    # person types (e.g. "Rudy-Laptop"), never invented by the app. The UI
    # prompts for it once and persists what's typed via save_device_label.
    return ""


def _read_legacy_config(config_path: Path) -> dict:
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def resolve_config_path(env: dict | None = None) -> Path:
    env = os.environ if env is None else env
    return Path(env["SPARKY_CONFIG"]) if env.get("SPARKY_CONFIG") else DEFAULT_LOCAL_ROOT / LEGACY_CONFIG_FILENAME


def _update_legacy_config(updates: dict, env: dict | None = None) -> None:
    config_path = resolve_config_path(env)
    config = _read_legacy_config(config_path)
    config.update(updates)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = config_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(config, indent=2, sort_keys=True), encoding="utf-8")
    tmp.replace(config_path)


def save_device_label(label: str, env: dict | None = None) -> None:
    """Persist a person-typed device label into the legacy config file,
    preserving whatever else is already there."""
    _update_legacy_config({"device_label": label}, env)


def save_cloud_sync_config(url: str, token: str, env: dict | None = None) -> None:
    """Persist the hosted web app's URL + sync token, preserving whatever
    else is already in the legacy config file."""
    _update_legacy_config({"cloud_sync_url": url, "cloud_sync_token": token}, env)


def load_paths(env: dict | None = None) -> SmartyPaths:
    """Resolve Smarty's local/shared paths and device identity.

    Precedence (highest first): environment variables, legacy
    ``sparky-paths.json`` config file, built-in defaults.
    """
    env = os.environ if env is None else env

    local_root = Path(env.get("SPARKY_LOCAL_ROOT", "")) if env.get("SPARKY_LOCAL_ROOT") else None
    nas_root = Path(env.get("SPARKY_NAS_ROOT", "")) if env.get("SPARKY_NAS_ROOT") else None
    config_path = resolve_config_path(env)

    config = _read_legacy_config(config_path)

    if local_root is None:
        local_root = Path(config["local_root"]) if config.get("local_root") else DEFAULT_LOCAL_ROOT
    if nas_root is None:
        nas_root = Path(config["nas_root"]) if config.get("nas_root") else DEFAULT_NAS_ROOT

    device_id = env.get("SPARKY_DEVICE_ID") or config.get("device_id") or _default_device_id()
    device_label = env.get("SPARKY_DEVICE_LABEL") or config.get("device_label") or _default_device_label()
    cloud_sync_url = env.get("SPARKY_CLOUD_SYNC_URL") or config.get("cloud_sync_url")
    cloud_sync_token = env.get("SPARKY_CLOUD_SYNC_TOKEN") or config.get("cloud_sync_token")

    return SmartyPaths(
        local_root=local_root,
        nas_root=nas_root,
        device_id=device_id,
        device_label=device_label,
        cloud_sync_url=cloud_sync_url,
        cloud_sync_token=cloud_sync_token,
    )


def ensure_local_dirs(paths: SmartyPaths) -> None:
    """Create local-only directories. Never touches the shared NAS root."""
    paths.local_root.mkdir(parents=True, exist_ok=True)
    paths.local_catalog_dir.mkdir(parents=True, exist_ok=True)
    paths.local_state_dir.mkdir(parents=True, exist_ok=True)
    paths.local_backups_dir.mkdir(parents=True, exist_ok=True)

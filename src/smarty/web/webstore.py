"""Builds the Store for the hosted web app.

Deliberately imports nothing from smarty.ui (no PySide6 in a web/container
deployment). Uses the same paths/journal/importer/seed modules as the
desktop app, just pointed at a different local root via the existing
SPARKY_LOCAL_ROOT env var -- same persistence model, same conflict rules,
just reachable over HTTPS instead of a desktop window.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from smarty.importer import cache_to_catalog, load_cache, save_cache
from smarty.paths import SmartyPaths, ensure_local_dirs, load_paths
from smarty.seed import empty_catalog, load_seed_from_dir
from smarty.store import Store

BUNDLED_SEED_DIR = Path(__file__).parent / "bundled_seed"


def _ensure_seed_files_present(seed_dir: Path) -> None:
    """Copy the bundled real seed into the configured seed dir if nothing
    is there yet -- so a fresh container (no persistent volume populated)
    still has the real catalog on first boot, exactly like a fresh laptop
    install does from its own local seed folder."""
    seed_dir.mkdir(parents=True, exist_ok=True)
    for name in ("categories.json", "ideas.json", "weekly-performance.json"):
        dest = seed_dir / name
        if not dest.exists():
            src = BUNDLED_SEED_DIR / name
            if src.exists():
                shutil.copy(src, dest)


def build_web_store() -> tuple[Store, SmartyPaths]:
    paths = load_paths()
    ensure_local_dirs(paths)

    seed_dir = paths.local_catalog_dir / "seed"
    cache_path = paths.local_catalog_dir / "current.json"

    if not cache_path.exists():
        _ensure_seed_files_present(seed_dir)

    bundled_seed = load_seed_from_dir(seed_dir)
    cache = load_cache(cache_path, bundled_seed if not bundled_seed.is_empty else empty_catalog())
    save_cache(cache_path, cache)
    catalog = cache_to_catalog(cache)

    store = Store(paths, catalog)
    return store, paths

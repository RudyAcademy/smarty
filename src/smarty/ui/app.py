"""Smarty entry point.

Startup order matters: open the local copy immediately (never block the
window on a dead T: drive), then kick off a bounded-timeout background
refresh.
"""

from __future__ import annotations

import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from smarty.importer import cache_to_catalog, load_cache, save_cache
from smarty.paths import ensure_local_dirs, load_paths
from smarty.seed import empty_catalog, load_seed_from_dir
from smarty.store import Store
from smarty.ui.main_window import MainWindow


def build_store():
    paths = load_paths()
    ensure_local_dirs(paths)

    seed_dir = paths.local_catalog_dir / "seed"
    cache_path = paths.local_catalog_dir / "current.json"

    bundled_seed = load_seed_from_dir(seed_dir)
    cache = load_cache(cache_path, bundled_seed if not bundled_seed.is_empty else empty_catalog())
    save_cache(cache_path, cache)
    catalog = cache_to_catalog(cache)

    store = Store(paths, catalog)
    return store, paths


def main() -> int:
    app = QApplication(sys.argv)
    store, paths = build_store()
    window = MainWindow(store, paths)
    window.resize(1366, 768)
    window.show()
    # Open the local copy immediately; the bounded-timeout share refresh
    # runs right after so a dead T: drive never blocks first paint.
    QTimer.singleShot(50, window.run_sync)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

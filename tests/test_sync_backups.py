from smarty.paths import SmartyPaths, ensure_local_dirs
from smarty.seed import empty_catalog
from smarty.store import Store
from smarty.sync import SyncConfig, sync_notes_journal


def _paths(tmp_path, nas_root, label):
    paths = SmartyPaths(
        local_root=tmp_path / label / "local",
        nas_root=nas_root,
        device_id=label,
        device_label=label,
    )
    ensure_local_dirs(paths)
    return paths


def test_only_five_auto_backups_kept_manual_backup_untouched(tmp_path):
    nas_root = tmp_path / "nas"
    data_dir = nas_root / "Data"
    backups_dir = data_dir / "backups"
    backups_dir.mkdir(parents=True)

    manual_backup = backups_dir / "manual-keep-forever.jsonl.bak"
    manual_backup.write_text("manual", encoding="utf-8")

    paths_a = _paths(tmp_path, nas_root, "pc-a")
    store_a = Store(paths_a, empty_catalog())

    for i in range(8):
        store_a.set_notes("idea-1", f"edit {i}")
        sync_notes_journal(store_a, paths_a, SyncConfig(share_probe_timeout=1))

    auto_backups = sorted(backups_dir.glob("journal-*.jsonl.bak"))
    assert len(auto_backups) <= 5
    assert manual_backup.exists()
    assert manual_backup.read_text(encoding="utf-8") == "manual"

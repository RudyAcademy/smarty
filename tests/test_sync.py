from smarty.journal import new_operation, read_journal
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


def test_offline_when_share_missing(tmp_path):
    paths = _paths(tmp_path, tmp_path / "does-not-exist-share", "pc-a")
    store = Store(paths, empty_catalog())
    result = sync_notes_journal(store, paths, SyncConfig(share_probe_timeout=1))
    assert result.outcome == "offline"


def test_no_data_dir_when_root_exists_but_data_missing(tmp_path):
    nas_root = tmp_path / "nas"
    nas_root.mkdir()
    paths = _paths(tmp_path, nas_root, "pc-a")
    store = Store(paths, empty_catalog())
    result = sync_notes_journal(store, paths, SyncConfig(share_probe_timeout=1))
    assert result.outcome == "no_data_dir"
    assert not (nas_root / "Data").exists()


def test_two_devices_sync_and_both_see_each_others_edit(tmp_path):
    nas_root = tmp_path / "nas"
    (nas_root / "Data").mkdir(parents=True)

    paths_a = _paths(tmp_path, nas_root, "pc-a")
    paths_b = _paths(tmp_path, nas_root, "pc-b")
    store_a = Store(paths_a, empty_catalog())
    store_b = Store(paths_b, empty_catalog())

    store_a.set_status("idea-1", "kept")
    store_b.set_notes("idea-1", "Check with Lumi")

    r1 = sync_notes_journal(store_a, paths_a, SyncConfig(share_probe_timeout=1))
    assert r1.outcome == "ok"
    r2 = sync_notes_journal(store_b, paths_b, SyncConfig(share_probe_timeout=1))
    assert r2.outcome == "ok"
    r3 = sync_notes_journal(store_a, paths_a, SyncConfig(share_probe_timeout=1))
    assert r3.outcome == "ok"

    assert store_a.user_state("idea-1").status == "kept"
    assert store_a.user_state("idea-1").notes == "Check with Lumi"
    assert store_b.user_state("idea-1").status == "kept"
    assert store_b.user_state("idea-1").notes == "Check with Lumi"


def test_stale_pc_does_not_resurrect_rejected_item(tmp_path):
    nas_root = tmp_path / "nas"
    (nas_root / "Data").mkdir(parents=True)
    paths_a = _paths(tmp_path, nas_root, "pc-a")
    paths_b = _paths(tmp_path, nas_root, "pc-b")
    store_a = Store(paths_a, empty_catalog())
    store_b = Store(paths_b, empty_catalog())

    store_a.set_status("idea-1", "rejected")
    sync_notes_journal(store_a, paths_a, SyncConfig(share_probe_timeout=1))

    # pc-b never wrote a competing op; it just syncs and should pick up the rejection.
    sync_notes_journal(store_b, paths_b, SyncConfig(share_probe_timeout=1))
    assert store_b.user_state("idea-1").status == "rejected"


def test_damaged_line_in_shared_journal_is_preserved_not_discarded(tmp_path):
    nas_root = tmp_path / "nas"
    data_dir = nas_root / "Data"
    data_dir.mkdir(parents=True)
    journal_path = data_dir / "journal.jsonl"
    journal_path.write_text("{this is not valid json}\n", encoding="utf-8")

    paths_a = _paths(tmp_path, nas_root, "pc-a")
    store_a = Store(paths_a, empty_catalog())
    store_a.set_status("idea-1", "kept")

    result = sync_notes_journal(store_a, paths_a, SyncConfig(share_probe_timeout=1))
    assert result.outcome == "ok"
    assert result.damaged_lines_seen >= 1

    text = journal_path.read_text(encoding="utf-8")
    assert "{this is not valid json}" in text


def test_lock_held_by_other_device_skips_publish_but_still_merges(tmp_path):
    nas_root = tmp_path / "nas"
    data_dir = nas_root / "Data"
    data_dir.mkdir(parents=True)
    lock_path = data_dir / "journal.lock"
    lock_path.write_text("someone-else:999999999999", encoding="utf-8")
    import os
    import time

    os.utime(lock_path, (time.time(), time.time()))  # fresh lock, not expired

    paths_a = _paths(tmp_path, nas_root, "pc-a")
    store_a = Store(paths_a, empty_catalog())
    store_a.set_status("idea-1", "kept")

    result = sync_notes_journal(store_a, paths_a, SyncConfig(share_probe_timeout=1, lock_wait_timeout=0.3))
    assert result.outcome == "locked"
    assert lock_path.exists()


def test_expired_lock_is_stolen(tmp_path):
    nas_root = tmp_path / "nas"
    data_dir = nas_root / "Data"
    data_dir.mkdir(parents=True)
    lock_path = data_dir / "journal.lock"
    lock_path.write_text("someone-else:1", encoding="utf-8")
    import os

    old_time = 0
    os.utime(lock_path, (old_time, old_time))

    paths_a = _paths(tmp_path, nas_root, "pc-a")
    store_a = Store(paths_a, empty_catalog())
    store_a.set_status("idea-1", "kept")

    result = sync_notes_journal(
        store_a, paths_a, SyncConfig(share_probe_timeout=1, lock_wait_timeout=0.5, lock_lease_seconds=1)
    )
    assert result.outcome == "ok"

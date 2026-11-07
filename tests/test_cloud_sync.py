"""Integration tests: a real smarty.web.app instance running in a
background thread, and cloud_sync.sync_with_cloud actually talking to it
over real HTTP (not mocked) -- proving the laptop-side client and the
server's /api/sync endpoints genuinely agree on the wire format.
"""

import threading
import time

import pytest
import uvicorn

from smarty.cloud_sync import sync_with_cloud
from smarty.paths import SmartyPaths, ensure_local_dirs
from smarty.seed import empty_catalog
from smarty.store import Store


@pytest.fixture()
def live_cloud_server(tmp_path, monkeypatch):
    monkeypatch.setenv("SPARKY_LOCAL_ROOT", str(tmp_path / "cloud-data"))
    monkeypatch.setenv("SPARKY_NAS_ROOT", str(tmp_path / "cloud-nas"))
    monkeypatch.setenv("SMARTY_WEB_PASSWORD", "pw")
    monkeypatch.setenv("SMARTY_SYNC_TOKEN", "tok123")
    monkeypatch.setenv("SPARKY_DEVICE_LABEL", "cloud")
    monkeypatch.delenv("SPARKY_CONFIG", raising=False)

    import sys

    for mod in list(sys.modules):
        if mod.startswith("smarty.web"):
            del sys.modules[mod]

    from smarty.web.app import app

    config = uvicorn.Config(app, host="127.0.0.1", port=8799, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    deadline = time.monotonic() + 5
    while not server.started and time.monotonic() < deadline:
        time.sleep(0.05)
    assert server.started, "cloud server did not start in time"

    yield "http://127.0.0.1:8799", "tok123"

    server.should_exit = True
    thread.join(timeout=5)


def _laptop_paths(tmp_path, label, cloud_url, cloud_token):
    paths = SmartyPaths(
        local_root=tmp_path / label / "local",
        nas_root=tmp_path / "unused-nas",
        device_id=label,
        device_label=label,
        cloud_sync_url=cloud_url,
        cloud_sync_token=cloud_token,
    )
    ensure_local_dirs(paths)
    return paths


def test_not_configured_when_no_cloud_url(tmp_path):
    paths = SmartyPaths(local_root=tmp_path / "local", nas_root=tmp_path / "nas", device_id="d", device_label="d")
    ensure_local_dirs(paths)
    store = Store(paths, empty_catalog())
    result = sync_with_cloud(store, paths)
    assert result.outcome == "not_configured"


def test_wrong_token_is_unauthorized(tmp_path, live_cloud_server):
    url, _token = live_cloud_server
    paths = _laptop_paths(tmp_path, "laptop", url, "wrong-token")
    store = Store(paths, empty_catalog())
    result = sync_with_cloud(store, paths, timeout=5)
    assert result.outcome == "unauthorized"


def test_push_then_pull_round_trip_over_real_http(tmp_path, live_cloud_server):
    url, token = live_cloud_server

    laptop_paths = _laptop_paths(tmp_path, "laptop", url, token)
    laptop_store = Store(laptop_paths, empty_catalog())
    laptop_store.set_status("sparky-idea-gauss", "kept")
    laptop_store.set_notes("sparky-idea-gauss", "from laptop")

    result = sync_with_cloud(laptop_store, laptop_paths, timeout=5)
    assert result.outcome == "ok"
    assert result.pushed == 2

    # A second laptop pulls and should see the first laptop's edits.
    laptop2_paths = _laptop_paths(tmp_path, "laptop2", url, token)
    laptop2_store = Store(laptop2_paths, empty_catalog())
    result2 = sync_with_cloud(laptop2_store, laptop2_paths, timeout=5)
    assert result2.outcome == "ok"
    assert result2.pulled >= 2

    us = laptop2_store.user_state("sparky-idea-gauss")
    assert us.status == "kept"
    assert us.notes == "from laptop"


def test_ipad_web_edit_reaches_laptop_via_cloud(tmp_path, live_cloud_server):
    """The web UI writes directly into the cloud server's own store (that's
    how a browser/iPad session edits); a laptop syncing afterwards must see it."""
    import httpx

    url, token = live_cloud_server

    with httpx.Client(base_url=url) as client:
        client.post("/login", data={"password": "pw", "next": "/"})
        r = client.post(
            "/record/sparky-idea-gauss/status",
            data={"status": "parked", "from_tile": "1"},
        )
        assert r.status_code == 303

    laptop_paths = _laptop_paths(tmp_path, "laptop", url, token)
    laptop_store = Store(laptop_paths, empty_catalog())
    result = sync_with_cloud(laptop_store, laptop_paths, timeout=5)
    assert result.outcome == "ok"
    assert laptop_store.user_state("sparky-idea-gauss").status == "parked"

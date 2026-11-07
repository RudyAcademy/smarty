import zipfile

import pytest

from smarty.updater import (
    UpdateRejected,
    publish_update_manifest,
    read_current_version,
    stage_update,
    switch_current_version,
    validate_zip_filename,
)


def _make_zip(path, with_entry=True):
    with zipfile.ZipFile(path, "w") as zf:
        if with_entry:
            zf.writestr("smarty/ui/app.py", "# entry point\n")
        else:
            zf.writestr("readme.txt", "nothing runnable\n")


def test_rejects_bad_zip_filename():
    with pytest.raises(UpdateRejected):
        validate_zip_filename("Sparky_v0.2.0.zip")
    with pytest.raises(UpdateRejected):
        validate_zip_filename("Smarty_v0.2.zip")
    assert validate_zip_filename("Smarty_v0.2.0.zip") == "0.2.0"


def test_refuses_downgrade(tmp_path):
    zip_path = tmp_path / "Smarty_v0.1.0.zip"
    _make_zip(zip_path)
    import hashlib

    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    manifest = {"version": "0.1.0", "zip": "Smarty_v0.1.0.zip", "sha256": sha}

    result = stage_update(
        source_zip=zip_path,
        manifest=manifest,
        installed_version="0.2.0",
        versions_dir=tmp_path / "versions",
        smoke_check=lambda d: True,
    )
    assert result.ok is False
    assert "downgrade" in result.detail


def test_hash_mismatch_rejected(tmp_path):
    zip_path = tmp_path / "Smarty_v0.2.0.zip"
    _make_zip(zip_path)
    manifest = {"version": "0.2.0", "zip": "Smarty_v0.2.0.zip", "sha256": "0" * 64}

    result = stage_update(
        source_zip=zip_path,
        manifest=manifest,
        installed_version="0.1.0",
        versions_dir=tmp_path / "versions",
        smoke_check=lambda d: True,
    )
    assert result.ok is False
    assert "sha256" in result.detail


def test_smoke_check_failure_leaves_previous_version(tmp_path):
    zip_path = tmp_path / "Smarty_v0.2.0.zip"
    _make_zip(zip_path, with_entry=False)
    import hashlib

    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    manifest = {"version": "0.2.0", "zip": "Smarty_v0.2.0.zip", "sha256": sha}
    versions_dir = tmp_path / "versions"
    versions_dir.mkdir()
    switch_current_version(versions_dir, "0.1.0")

    result = stage_update(
        source_zip=zip_path,
        manifest=manifest,
        installed_version="0.1.0",
        versions_dir=versions_dir,
        smoke_check=lambda d: False,
    )
    assert result.ok is False
    assert not (versions_dir / "0.2.0").exists()
    assert read_current_version(versions_dir, "fallback") == "0.1.0"


def test_successful_stage_then_switch(tmp_path):
    zip_path = tmp_path / "Smarty_v0.2.0.zip"
    _make_zip(zip_path)
    import hashlib

    sha = hashlib.sha256(zip_path.read_bytes()).hexdigest()
    manifest = {"version": "0.2.0", "zip": "Smarty_v0.2.0.zip", "sha256": sha}
    versions_dir = tmp_path / "versions"
    versions_dir.mkdir()
    switch_current_version(versions_dir, "0.1.0")

    result = stage_update(
        source_zip=zip_path,
        manifest=manifest,
        installed_version="0.1.0",
        versions_dir=versions_dir,
        smoke_check=lambda d: True,
    )
    assert result.ok is True
    switch_current_version(versions_dir, result.version)
    assert read_current_version(versions_dir, "fallback") == "0.2.0"


def test_publish_manifest_only_after_zip_staged(tmp_path):
    installers_dir = tmp_path / "Installers"
    installers_dir.mkdir()
    zip_path = tmp_path / "Smarty_v0.2.0.zip"
    _make_zip(zip_path)

    with pytest.raises(UpdateRejected):
        publish_update_manifest(
            installers_dir=installers_dir,
            zip_path=zip_path,
            version="0.2.0",
            built_on="linux",
            windows_installer=False,
        )

    staged = installers_dir / zip_path.name
    staged.write_bytes(zip_path.read_bytes())
    manifest = publish_update_manifest(
        installers_dir=installers_dir,
        zip_path=zip_path,
        version="0.2.0",
        built_on="linux",
        windows_installer=False,
    )
    assert manifest["windows_installer"] is False
    assert (installers_dir / "latest.json").exists()

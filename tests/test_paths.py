from smarty.paths import load_paths, save_device_label


def test_device_label_blank_by_default(tmp_path):
    env = {"SPARKY_LOCAL_ROOT": str(tmp_path / "local"), "SPARKY_NAS_ROOT": str(tmp_path / "nas")}
    paths = load_paths(env)
    assert paths.device_label == ""


def test_save_device_label_persists_and_preserves_other_fields(tmp_path):
    config_path = tmp_path / "sparky-paths.json"
    env = {
        "SPARKY_LOCAL_ROOT": str(tmp_path / "local"),
        "SPARKY_NAS_ROOT": str(tmp_path / "nas"),
        "SPARKY_CONFIG": str(config_path),
    }
    save_device_label("Rudy-Laptop", env)
    paths = load_paths(env)
    assert paths.device_label == "Rudy-Laptop"

    # saving again must not clobber local_root/nas_root already resolved via env
    save_device_label("Rudy-Laptop-renamed", env)
    paths2 = load_paths(env)
    assert paths2.device_label == "Rudy-Laptop-renamed"
    assert paths2.local_root == tmp_path / "local"

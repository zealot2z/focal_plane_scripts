from focal_plane_refactor.config import load_config


def test_default_method_is_sep():
    cfg = load_config(None)
    assert cfg["process_raw"]["method"] == "sep"

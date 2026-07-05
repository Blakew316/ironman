"""Tests for path/config resolution."""

from pathlib import Path

from jarvis import config


def test_paths_are_pathlib_paths():
    assert isinstance(config.ASSET_PATH, Path)
    assert isinstance(config.SOUNDS_PATH, Path)
    assert isinstance(config.MUSIC_PATH, Path)


def test_asset_subpaths_are_under_asset_path():
    for sub in (config.SOUNDS_PATH, config.MUSIC_PATH, config.NOTES_PATH, config.SCREENSHOTS_PATH):
        assert config.ASSET_PATH in sub.parents


def test_no_hardcoded_windows_paths():
    # regression guard: the old code hard-coded C:\Users\skili\...
    assert "skili" not in str(config.ASSET_PATH)
    assert not str(config.ASSET_PATH).startswith("C:\\")


def test_ensure_asset_dirs_creates_writable_dirs(tmp_path, monkeypatch):
    notes = tmp_path / "notes"
    shots = tmp_path / "screenshots"
    monkeypatch.setattr(config, "NOTES_PATH", notes)
    monkeypatch.setattr(config, "SCREENSHOTS_PATH", shots)
    config.ensure_asset_dirs()
    assert notes.is_dir()
    assert shots.is_dir()

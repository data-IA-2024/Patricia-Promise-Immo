from scripts.unzip_to_csv import root_dir
from pathlib import Path

def test_should_root_dir_is_path():
    base = root_dir()
    out_expected = "D:/ProjectFolderDevAI_2025-2026/Immo_project"
    assert base == Path(out_expected)

def test_should_ensure_create_dirs():
    pass
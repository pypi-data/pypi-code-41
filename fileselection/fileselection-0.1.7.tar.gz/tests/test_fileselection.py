#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fileselection` package."""
from pathlib import Path

import pytest
from fileselection.fileselection import (
    FileSelectionFile,
    NotRelativeToRootException,
    FileSelectionFolder,
    FileSelectionLoadError,
)
from tests import RESOURCE_PATH


def test_fileselection_file():
    """Very basic tests"""

    # initialise basic
    _ = FileSelectionFile(data_file_path=RESOURCE_PATH)

    # initialise with description and file list
    selection = FileSelectionFile(
        data_file_path=RESOURCE_PATH,
        description="a test selection",
        selected_paths=["selected_paths/file1", "selected_paths/file2"],
    )
    assert len(selection.selected_paths) == 2


def test_absolute_vs_relative_paths():

    # initialising with absolute selected_paths should work
    root_path = Path("/fileselection_root_path/test1")
    path1 = root_path / "file1"
    path2 = root_path / "file2"
    assert path1.is_absolute()
    selection = FileSelectionFile(
        data_file_path=root_path, selected_paths=[path1, path2]
    )

    # but selected_paths should have been stored as relative
    assert len(selection.selected_paths) == 2
    assert not selection.selected_paths[0].is_absolute()


def test_absolute_vs_relative_path_exception():
    """Adding a path outside root path should not be possible"""

    # initialising with absolute selected_paths should work
    root_path = Path("/fileselection_root_path/test1")
    path1 = root_path / "file1"
    path2 = Path("/some_other_absolute_path/file2")
    assert path2.is_absolute()
    with pytest.raises(NotRelativeToRootException):
        _ = FileSelectionFile(data_file_path=root_path, selected_paths=[path1, path2])


def test_persisting_to_disk(tmpdir):
    """Load and save a FileSelectionFile """
    datafile = tmpdir / ".fileselection"
    selection = FileSelectionFile(
        data_file_path=datafile,
        description="a test selection",
        selected_paths=["selected_paths/file1", "selected_paths/file2"],
    )
    with open(datafile, "w") as f:
        selection.save(f)

    with open(datafile, "r") as f:
        loaded = FileSelectionFile.load(f, datafile=datafile)
    assert len(loaded.selected_paths) == 2
    assert loaded.description == "a test selection"
    assert loaded.root_path == tmpdir


def test_persisting_to_disk_tricky_values(tmpdir):
    """Load and save a FileSelectionFile with accolades, newlines and cyrillic """
    datafile = tmpdir / ".fileselection"
    selection = FileSelectionFile(
        data_file_path=datafile,
        description='a test: #)%*(I#JF Very nasty {is this escaped?} "" \nselection',
        selected_paths=["selected_paths/file1", "selected_paths/Ба́бушка.txt"],
    )
    with open(datafile, "w") as f:
        selection.save(f)

    with open(datafile, "r") as f:
        loaded = FileSelectionFile.load(f, datafile=datafile)
    assert len(loaded.selected_paths) == 2
    assert loaded.selected_paths[1] == Path("selected_paths/Ба́бушка.txt")
    assert (
        loaded.description
        == 'a test: #)%*(I#JF Very nasty {is this escaped?} "" \nselection'
    )
    assert loaded.root_path == tmpdir


def test_file_selection(tmpdir):
    paths = [tmpdir / "test1", tmpdir / "test2"]
    description = "Some description"
    selection_folder = FileSelectionFolder(path=tmpdir)
    assert selection_folder.has_file_selection() is False

    fileselection = FileSelectionFile(
        data_file_path=Path(tmpdir) / "fileselection",
        description=description,
        selected_paths=paths,
    )

    selection_folder.save_file_selection(fileselection)
    assert fileselection.id is not None
    assert selection_folder.has_file_selection()

    loaded = selection_folder.load_file_selection()
    assert loaded.selected_paths_absolute == paths
    assert loaded.description == description
    assert loaded.id == fileselection.id


def test_file_selection_non_existant(tmpdir):
    """Try to load a FileSelectionFolder from a folder where there is none"""

    with pytest.raises(FileNotFoundError):
        FileSelectionFolder(tmpdir).load_file_selection()

    # and try loading from a non-existant folder
    with pytest.raises(FileNotFoundError):
        FileSelectionFolder("/non_existant_folder").load_file_selection()


def test_file_selection_barely_valid_format():
    """Fileselection files can be edited. And of course edited badly. Check whether users are getting proper
    feedback """

    datafile_path = RESOURCE_PATH / "fileselections" / "should_work.txt"
    with open(datafile_path, "r") as f:
        loaded = FileSelectionFile.load(f, datafile_path)

    assert len(loaded.selected_paths) == 33

    # empty file paths should just be ignored
    datafile_path = RESOURCE_PATH / "fileselections" / "empty_filename.txt"
    with open(datafile_path, "r") as f:
        loaded = FileSelectionFile.load(f, datafile_path)
    assert len(loaded.selected_paths) == 2


@pytest.mark.parametrize(
    "input_file, expected_exception",
    [
        ("missing_fields.txt", FileSelectionLoadError),
        ("invalid_newlines.txt", FileSelectionLoadError),
        ("forgot_dash.txt", FileSelectionLoadError),
        ("not_relative_path.txt", NotRelativeToRootException),
    ],
)
def test_file_selection_invalid_format(input_file, expected_exception):
    """FileSelectionFolder files can be edited. And of course edited badly. Check whether users are getting proper
    feedback """

    datafile_path = RESOURCE_PATH / "fileselections" / input_file
    with pytest.raises(expected_exception) as e:
        with open(datafile_path, "r") as f:
            FileSelectionFile.load(f, datafile_path)
    test = 1

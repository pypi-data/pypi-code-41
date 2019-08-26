import os
import re

from click.testing import CliRunner

from psed import __main__

SAMPLE_FILE_1 = (
    "[ERROR] Some error\n"
    "[INFO] Some info\n"
    "[WARNING] Some warning\n"
    "[ERROR] Other error\n"
    "[ERROR] There's a lot of errors\n"
    "[DEBUG] And one debug\n"
)

SAMPLE_FILE_1_REPLACED = (
    f"{{ERROR}} Some error{os.linesep}"
    f"{{INFO}} Some info{os.linesep}"
    f"{{WARNING}} Some warning{os.linesep}"
    f"{{ERROR}} Other error{os.linesep}"
    f"{{ERROR}} There's a lot of errors{os.linesep}"
    f"{{DEBUG}} And one debug{os.linesep}"
)

SAMPLE_FILE_2 = (
    "[ERROR] First error\n"
    "[ERROR] Second error\n"
    "[INFO] Info message\n"
    "[WARNING] There were 2 errors\n"
)

SAMPLE_FILE_2_REPLACED = (
    f"{{ERROR}} First error{os.linesep}"
    f"{{ERROR}} Second error{os.linesep}"
    f"{{INFO}} Info message{os.linesep}"
    f"{{WARNING}} There were 2 errors{os.linesep}"
)


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(__main__.main)
    assert result.exit_code == 2
    assert 'Missing option "-i" / "--input"' in result.output
    help_result = runner.invoke(__main__.main, ["--help"])
    assert help_result.exit_code == 0
    assert re.search(r"--help\s+Show this message and exit", help_result.output)


def test_find_full(fs):
    fs.create_file("first_file", contents=SAMPLE_FILE_1)
    fs.create_file("second_file", contents=SAMPLE_FILE_2)

    runner = CliRunner()
    result = runner.invoke(
        __main__.main,
        ["--input", "*_file", "--find", r"\[ERROR\]", "--find", r"\[WARNING\]", "-vv"],
    )

    assert result.exit_code == 0
    assert result.output == (
        "Find patterns:\n"
        "	- \\[ERROR\\]\n"
        "	- \\[WARNING\\]\n"
        "Glob has matched following files:\n"
        "	- first_file\n"
        "	- second_file\n"
        "first_file: 4 matches:\n"
        "	(0, 7): [ERROR]\n"
        "	(59, 66): [ERROR]\n"
        "	(79, 86): [ERROR]\n"
        "	(36, 45): [WARNING]\n"
        "second_file: 3 matches:\n"
        "	(0, 7): [ERROR]\n"
        "	(20, 27): [ERROR]\n"
        "	(61, 70): [WARNING]\n"
    )


def test_find_full_no_results(fs):
    fs.create_file("first_file", contents=SAMPLE_FILE_1)
    fs.create_file("second_file", contents=SAMPLE_FILE_2)

    runner = CliRunner()
    result = runner.invoke(
        __main__.main, ["--input", "*_file", "--find", r"\[CRITICAL\]", "-vv"]
    )

    assert result.exit_code == 0
    assert result.output == (
        "Find patterns:\n"
        "	- \\[CRITICAL\\]\n"
        "Glob has matched following files:\n"
        "	- first_file\n"
        "	- second_file\n"
        "No matches.\n"
    )


def test_find_replace(fs):
    fs.create_file("first_file", contents=SAMPLE_FILE_1)
    first_replaced = fs.create_file("first_file_psed")
    fs.create_file("second_file", contents=SAMPLE_FILE_2)
    second_replaced = fs.create_file("second_file_psed")

    runner = CliRunner()
    result = runner.invoke(
        __main__.main,
        ["--input", "*_file", "--find", r"\[(\w+)\]", "--replace", r"{\1}", "-vv"],
    )

    assert result.exit_code == 0
    assert result.output == (
        "Find patterns:\n"
        "	- \\[(\\w+)\\]\n"
        "Replace pattern: {\\1}\n"
        "Glob has matched following files:\n"
        "	- first_file\n"
        "	- second_file\n"
        "Saved file after changes: first_file_psed\n"
        "Saved file after changes: second_file_psed\n"
    )

    assert first_replaced.contents == SAMPLE_FILE_1_REPLACED
    assert second_replaced.contents == SAMPLE_FILE_2_REPLACED


def test_find_replace_inplace(fs):
    first_file = fs.create_file("first_file", contents=SAMPLE_FILE_1)
    second_file = fs.create_file("second_file", contents=SAMPLE_FILE_2)

    runner = CliRunner()
    result = runner.invoke(
        __main__.main,
        [
            "--input",
            "*_file",
            "--find",
            r"\[(\w+)\]",
            "--replace",
            r"{\1}",
            "--inplace",
            "-vv",
        ],
    )

    assert result.exit_code == 0
    assert result.output == (
        "Find patterns:\n"
        "	- \\[(\\w+)\\]\n"
        "Replace pattern: {\\1}\n"
        "Glob has matched following files:\n"
        "	- first_file\n"
        "	- second_file\n"
        "Modified file: first_file\n"
        "Modified file: second_file\n"
    )

    assert first_file.contents == SAMPLE_FILE_1_REPLACED
    assert second_file.contents == SAMPLE_FILE_2_REPLACED

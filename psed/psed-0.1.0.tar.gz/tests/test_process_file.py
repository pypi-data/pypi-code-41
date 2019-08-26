from psed.psed import Psed

LOG_FILE_CONTENT = (
    "[ERROR] Some error\n"
    "[INFO] Some info\n"
    "[WARNING] Some warning\n"
    "[ERROR] Other error\n"
    "[ERROR] There's a lot of errors\n"
    "[DEBUG] And one debug\n"
)


def test_find_simple(fs, capsys):
    fs.create_file("input_file", contents="the haystack with a needle somewhere")

    psed = Psed(find=["needle"])
    matches = psed.process_file("input_file")

    assert len(matches) == 1

    output = capsys.readouterr().out
    assert output == ("input_file: 1 match:\n	(20, 26): needle\n")


def test_not_found(fs,):
    fs.create_file("input_file", contents="the haystack")

    psed = Psed(find=["needle"])
    matches = psed.process_file("input_file")

    assert not matches


def test_find_multiple_matches(fs, capsys):
    fs.create_file("input_file", contents=LOG_FILE_CONTENT)

    psed = Psed(find=["ERROR"])
    matches = psed.process_file("input_file")

    assert len(matches) == 3

    output = capsys.readouterr().out
    assert output == (
        "input_file: 3 matches:\n"
        "\t(1, 6): ERROR\n"
        "\t(60, 65): ERROR\n"
        "\t(80, 85): ERROR\n"
    )


def test_find_regex(fs, capsys):
    fs.create_file("input_file", contents=LOG_FILE_CONTENT)

    psed = Psed(find=[r"\[\w+\]"])
    matches = psed.process_file("input_file")

    assert len(matches) == 6

    output = capsys.readouterr().out
    assert output == (
        "input_file: 6 matches:\n"
        "\t(0, 7): [ERROR]\n"
        "\t(19, 25): [INFO]\n"
        "\t(36, 45): [WARNING]\n"
        "\t(59, 66): [ERROR]\n"
        "\t(79, 86): [ERROR]\n"
        "\t(111, 118): [DEBUG]\n"
    )


def test_find_multiple_inputs(fs, capsys):
    fs.create_file("input_file", contents=LOG_FILE_CONTENT)

    psed = Psed(find=[r"\[ERROR\]", r"\[INFO\]", r"\[WARNING\]", r"\[DEBUG\]"])
    matches = psed.process_file("input_file")

    assert len(matches) == 6

    output = capsys.readouterr().out
    assert output == (
        "input_file: 6 matches:\n"
        "\t(0, 7): [ERROR]\n"
        "\t(59, 66): [ERROR]\n"
        "\t(79, 86): [ERROR]\n"
        "\t(19, 25): [INFO]\n"
        "\t(36, 45): [WARNING]\n"
        "\t(111, 118): [DEBUG]\n"
    )


def test_replace_simple(fs):
    fs.create_file("input_file", contents="the haystack with a needle somewhere")
    out_file = fs.create_file("input_file_psed")

    assert out_file.contents == ""

    psed = Psed(find=["needle"], replace="nail")
    match = psed.process_file("input_file")

    assert match
    assert out_file.contents == "the haystack with a nail somewhere"


def test_replace_simple_inplace(fs):
    in_file = fs.create_file(
        "input_file", contents="the haystack with a needle somewhere"
    )

    assert in_file.contents == "the haystack with a needle somewhere"

    psed = Psed(find=["needle"], replace="nail", inplace=True)
    match = psed.process_file("input_file")

    assert match
    assert in_file.contents == "the haystack with a nail somewhere"


def test_replace_regex(fs):
    fs.create_file("input_file", contents="[ERROR] and [WARNING]")
    out_file = fs.create_file("input_file_psed")

    assert out_file.contents == ""

    psed = Psed(find=[r"\[(\w+)\]"], replace=r"[SOME_\1]")
    match = psed.process_file("input_file")

    assert match

    assert out_file.contents == "[SOME_ERROR] and [SOME_WARNING]"


def test_replace_no_matches(fs):
    in_file = fs.create_file("input_file", contents="a big haystack")

    assert in_file.contents == "a big haystack"

    psed = Psed(find=["needle"], replace="nail", inplace=True)
    match = psed.process_file("input_file")

    assert not match
    assert in_file.contents == "a big haystack"

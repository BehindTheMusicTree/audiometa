import subprocess

import pytest
from select_test_matrix import changed_regular_files, main, select_mode

UNIT_TEST = "audiometa/test/tests/unit/metadata_field/test_values.py"
HELPER = "audiometa/utils/disc_number_read.py"
DOC = "docs/TESTING.md"


@pytest.mark.unit
@pytest.mark.parametrize(
    ("paths", "mode"),
    [
        ([DOC, "SUPPORT.md"], "docs"),
        ([UNIT_TEST, DOC, HELPER], "reduced"),
        ([DOC, "README.md"], "full"),
        ([UNIT_TEST, "pyproject.toml"], "full"),
        ([HELPER, "scripts/install-system-dependencies-macos.sh"], "full"),
        ([HELPER, ".github/workflows/lint-and-test.yml"], "full"),
        ([HELPER, "audiometa/test/tests/unit/conftest.py"], "full"),
        ([DOC, "docs/demos/tape.md"], "full"),
        ([DOC, "CHANGELOG.md"], "full"),
        ([UNIT_TEST, "CHANGELOG.md"], "full"),
        ([], "full"),
    ],
)
def test_select_mode(paths, mode):
    assert select_mode(paths) == mode


@pytest.mark.unit
@pytest.mark.parametrize(
    ("header", "paths"),
    [
        (b":100644 100644 old new M", [DOC]),
        (b":100644 100755 old old M", []),
        (b":100644 000000 old 000 D", []),
        (b":000000 100644 000 new A", []),
        (b":120000 120000 old new M", []),
    ],
)
def test_regular_file_edits(header, paths):
    assert changed_regular_files(header + b"\0" + DOC.encode() + b"\0") == paths


@pytest.mark.unit
def test_git_failure_uses_full_matrix(monkeypatch, capsys):
    def unavailable_git(*args):
        raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr("select_test_matrix.git", unavailable_git)
    main()
    assert capsys.readouterr().out == "full\n"

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import tests.test_utils as utils
from hook.file_processing.pre_commit_runner import PreCommitRunner


class PreCommitRunnerScenariosTest(unittest.TestCase):
    """Verify pre-commit runner behavior across file-processing scenarios.

    These tests check that the runner reads and sorts Python files, rewrites files
    only when their sorted source differs, returns the correct pre-commit exit
    code, and ignores non-Python files without passing them to the source sorter.
    """

    def setUp(self) -> None:
        self.source_sorter = utils.FakeSourceSorter()
        self.python_file_repository = utils.FakePythonFileRepository()
        self.pre_commit_runner = PreCommitRunner(
            self.source_sorter,
            self.python_file_repository,
        )

    def test_returns_zero_when_no_python_file_changes(self) -> None:
        python_file_path = Path("example.py")
        self.python_file_repository.source_by_file_path[python_file_path] = "same"

        exit_code = self.pre_commit_runner.run([python_file_path])

        self.assertEqual(
            0,
            exit_code,
            msg="Expected exit code 0 when no Python file is changed.",
        )
        self.assertEqual(
            [],
            self.python_file_repository.written_file_paths,
            msg="Expected unchanged Python file not to be written.",
        )

    def test_returns_one_when_python_file_changes(self) -> None:
        python_file_path = Path("example.py")
        self.python_file_repository.source_by_file_path[python_file_path] = "original"
        self.source_sorter.sorted_source_by_original_source["original"] = "sorted"

        exit_code = self.pre_commit_runner.run([python_file_path])

        self.assertEqual(
            1,
            exit_code,
            msg="Expected exit code 1 when a Python file is rewritten.",
        )
        self.assertEqual(
            "sorted",
            self.python_file_repository.written_source_by_file_path[python_file_path],
            msg="Expected changed Python file to be written with sorted source.",
        )

    def test_ignores_non_python_files(self) -> None:
        python_file_path = Path("example.py")
        text_file_path = Path("notes.txt")
        markdown_file_path = Path("README.md")
        self.python_file_repository.source_by_file_path[python_file_path] = "same"

        exit_code = self.pre_commit_runner.run([text_file_path, python_file_path, markdown_file_path])

        self.assertEqual(
            0,
            exit_code,
            msg="Expected exit code 0 when no Python file changes.",
        )
        self.assertEqual(
            [python_file_path],
            self.python_file_repository.read_file_paths,
            msg="Expected only .py files to be read.",
        )

    def test_returns_one_when_any_python_file_changes(self) -> None:
        changed_file_path = Path("changed.py")
        unchanged_file_path = Path("unchanged.py")
        self.python_file_repository.source_by_file_path[changed_file_path] = "original"
        self.python_file_repository.source_by_file_path[unchanged_file_path] = "same"
        self.source_sorter.sorted_source_by_original_source["original"] = "sorted"

        exit_code = self.pre_commit_runner.run([changed_file_path, unchanged_file_path])

        self.assertEqual(
            1,
            exit_code,
            msg=("Expected exit code 1 when at least one Python file is changed, " "even if other Python files are unchanged."),
        )
        self.assertEqual(
            [changed_file_path],
            self.python_file_repository.written_file_paths,
            msg="Expected only changed Python files to be written.",
        )

    def test_passes_sort_decorated_methods_option_to_source_sorter(self) -> None:
        python_file_path = Path("example.py")
        self.python_file_repository.source_by_file_path[python_file_path] = "same"

        self.pre_commit_runner.run(
            [python_file_path],
            sort_decorated_methods=True,
        )

        self.assertEqual(
            [True],
            self.source_sorter.received_sort_decorated_methods,
            msg="Expected sort_decorated_methods option to be passed to SourceSorter.",
        )

    def test_passes_sort_within_groups_option_to_source_sorter(self) -> None:
        python_file_path = Path("example.py")
        self.python_file_repository.source_by_file_path[python_file_path] = "same"

        self.pre_commit_runner.run(
            [python_file_path],
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            ["alphabetical"],
            self.source_sorter.received_sort_within_groups,
            msg="Expected sort_within_groups option to be passed to SourceSorter.",
        )

    def test_real_file_repository_reads_and_writes_utf_8_python_file(self) -> None:
        from hook.file_processing.python_file_repository import PythonFileRepository

        with TemporaryDirectory() as temporary_directory:
            python_file_path = Path(temporary_directory) / "example.py"
            python_file_path.write_text("original ü", encoding="utf-8")

            python_file_repository = PythonFileRepository()
            source = python_file_repository.read_source(python_file_path)
            python_file_repository.write_source(python_file_path, "sorted ü")

            self.assertEqual(
                "original ü",
                source,
                msg="Expected PythonFileRepository to read source as UTF-8.",
            )
            self.assertEqual(
                "sorted ü",
                python_file_path.read_text(encoding="utf-8"),
                msg="Expected PythonFileRepository to write source as UTF-8.",
            )

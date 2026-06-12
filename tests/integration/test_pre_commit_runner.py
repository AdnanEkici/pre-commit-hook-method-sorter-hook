from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import tests.test_utils as utils
from hook.file_processing.pre_commit_runner import PreCommitRunner
from hook.file_processing.python_file_repository import PythonFileRepository


class PreCommitRunnerTest(unittest.TestCase):
    """Verify pre-commit runner file handling and exit-code behavior.

    These tests check that unchanged Python files leave the hook successful,
    changed Python files are rewritten and produce a failing pre-commit exit code,
    and non-Python files are ignored without being passed to the source sorter.
    """

    def test_returns_zero_when_file_does_not_change(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text("value = 1\n", encoding="utf-8")
            source_sorter = utils.SourceSorterDouble("value = 1\n")
            pre_commit_runner = PreCommitRunner(source_sorter, PythonFileRepository())
            exit_code = pre_commit_runner.run([file_path])
            self.assertEqual(0, exit_code, msg="Expected returns zero when file does not change; assertEqual failed.")
            self.assertEqual(
                "value = 1\n", file_path.read_text(encoding="utf-8"), msg="Expected returns zero when file does not change; assertEqual failed."
            )

    def test_returns_one_and_rewrites_file_when_file_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text("value = 1\n", encoding="utf-8")
            source_sorter = utils.SourceSorterDouble("value = 2\n")
            pre_commit_runner = PreCommitRunner(source_sorter, PythonFileRepository())
            exit_code = pre_commit_runner.run([file_path])
            self.assertEqual(1, exit_code, msg="Expected returns one and rewrites file when file changes; assertEqual failed.")
            self.assertEqual(
                "value = 2\n",
                file_path.read_text(encoding="utf-8"),
                msg="Expected returns one and rewrites file when file changes; assertEqual failed.",
            )

    def test_skips_non_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.txt"
            file_path.write_text("value = 1\n", encoding="utf-8")
            source_sorter = utils.SourceSorterDouble("value = 2\n")
            pre_commit_runner = PreCommitRunner(source_sorter, PythonFileRepository())
            exit_code = pre_commit_runner.run([file_path])
            self.assertEqual(0, exit_code, msg="Expected skips non python files; assertEqual failed.")
            self.assertEqual([], source_sorter.received_sources, msg="Expected skips non python files; assertEqual failed.")

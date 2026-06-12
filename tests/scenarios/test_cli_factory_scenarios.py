from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import tests.test_utils as utils
from hook.command_line import main
from hook.factory import create_pre_commit_runner
from hook.file_processing.pre_commit_runner import PreCommitRunner


class CommandLineAndFactoryScenariosTest(unittest.TestCase):
    """Verify command-line integration and dependency factory wiring scenarios.

    These tests check that command-line options are parsed and passed to the
    pre-commit runner correctly, and that the factory creates a fully wired
    runner with the expected sorting, source-processing, and file-processing
    dependencies.
    """

    def test_factory_creates_pre_commit_runner_without_error(self) -> None:
        pre_commit_runner = create_pre_commit_runner()

        self.assertIsInstance(
            pre_commit_runner,
            PreCommitRunner,
            msg="Expected factory to create a PreCommitRunner instance.",
        )

    def test_main_passes_file_paths_to_pre_commit_runner(self) -> None:
        fake_pre_commit_runner = utils.FakePreCommitRunner(exit_code=0)

        with patch(
            "hook.command_line.create_pre_commit_runner",
            return_value=fake_pre_commit_runner,
        ):
            exit_code = main(["first.py", "second.py"])

        self.assertEqual(
            0,
            exit_code,
            msg="Expected main to return the exit code from PreCommitRunner.",
        )
        self.assertEqual(
            [Path("first.py"), Path("second.py")],
            fake_pre_commit_runner.received_file_paths,
            msg="Expected main to pass parsed file paths to PreCommitRunner.",
        )

    def test_main_passes_sort_decorated_methods_flag(self) -> None:
        fake_pre_commit_runner = utils.FakePreCommitRunner(exit_code=0)

        with patch(
            "hook.command_line.create_pre_commit_runner",
            return_value=fake_pre_commit_runner,
        ):
            main(["--sort-decorated-methods", "example.py"])

        self.assertEqual(
            True,
            fake_pre_commit_runner.received_sort_decorated_methods,
            msg="Expected CLI flag --sort-decorated-methods to be passed as True.",
        )

    def test_main_uses_preserve_as_default_sort_within_groups(self) -> None:
        fake_pre_commit_runner = utils.FakePreCommitRunner(exit_code=0)

        with patch(
            "hook.command_line.create_pre_commit_runner",
            return_value=fake_pre_commit_runner,
        ):
            main(["example.py"])

        self.assertEqual(
            "preserve",
            fake_pre_commit_runner.received_sort_within_groups,
            msg="Expected CLI to use preserve as default sort_within_groups option.",
        )

    def test_main_passes_alphabetical_sort_within_groups_option(self) -> None:
        fake_pre_commit_runner = utils.FakePreCommitRunner(exit_code=0)

        with patch(
            "hook.command_line.create_pre_commit_runner",
            return_value=fake_pre_commit_runner,
        ):
            main(["--sort-within-groups", "alphabetical", "example.py"])

        self.assertEqual(
            "alphabetical",
            fake_pre_commit_runner.received_sort_within_groups,
            msg=("Expected CLI option --sort-within-groups alphabetical to be passed " "to PreCommitRunner."),
        )

    def test_main_returns_runner_exit_code_one(self) -> None:
        fake_pre_commit_runner = utils.FakePreCommitRunner(exit_code=1)

        with patch(
            "hook.command_line.create_pre_commit_runner",
            return_value=fake_pre_commit_runner,
        ):
            exit_code = main(["example.py"])

        self.assertEqual(
            1,
            exit_code,
            msg="Expected main to return exit code 1 from PreCommitRunner.",
        )

    def test_main_accepts_no_files(self) -> None:
        fake_pre_commit_runner = utils.FakePreCommitRunner(exit_code=0)

        with patch(
            "hook.command_line.create_pre_commit_runner",
            return_value=fake_pre_commit_runner,
        ):
            exit_code = main([])

        self.assertEqual(
            0,
            exit_code,
            msg="Expected main to support being called with no file paths.",
        )
        self.assertEqual(
            [],
            fake_pre_commit_runner.received_file_paths,
            msg="Expected main to pass an empty file path list when no files are given.",
        )

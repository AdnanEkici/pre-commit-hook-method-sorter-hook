from __future__ import annotations

import unittest
from unittest.mock import patch

import tests.test_utils as utils
from hook import command_line


class CommandLineTest(unittest.TestCase):
    """Verify command-line argument parsing and runner invocation.

    This test ensures that the command-line entry point creates a runner, passes
    parsed file paths and sorting options to it, and returns the runner's exit code.
    """

    def test_main_passes_arguments_to_runner(self) -> None:
        pre_commit_runner = utils.PreCommitRunnerDouble()
        with patch("hook.command_line.create_pre_commit_runner", return_value=pre_commit_runner):
            exit_code = command_line.main(["--sort-decorated-methods", "--sort-within-groups", "alphabetical", "example.py"])
        self.assertEqual(7, exit_code, msg="Expected main passes arguments to runner; assertEqual failed.")
        self.assertEqual("example.py", str(pre_commit_runner.received_files[0]), msg="Expected main passes arguments to runner; assertEqual failed.")
        self.assertTrue(pre_commit_runner.received_sort_decorated_methods, msg="Expected main passes arguments to runner; assertTrue failed.")
        self.assertEqual(
            "alphabetical", pre_commit_runner.received_sort_within_groups, msg="Expected main passes arguments to runner; assertEqual failed."
        )

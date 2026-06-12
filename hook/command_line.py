from __future__ import annotations

import argparse
from pathlib import Path

from hook.configuration.sorting_options import SortWithinGroups
from hook.factory import create_pre_commit_runner


def main(command_arguments: list[str] | None = None) -> int:
    """Run the method-sorter pre-commit hook command.

    Args:
        command_arguments: Command-line arguments to parse. When None, arguments
            are read from the current process command line.

    Returns:
        Exit code returned by the pre-commit runner.
    """
    argument_parser = argparse.ArgumentParser(prog="method-sorter-hook")
    argument_parser.add_argument(
        "files",
        nargs="*",
        type=Path,
    )
    argument_parser.add_argument(
        "--sort-decorated-methods",
        action="store_true",
    )
    argument_parser.add_argument(
        "--sort-within-groups",
        choices=("preserve", "alphabetical"),
        default="preserve",
    )
    parsed_arguments = argument_parser.parse_args(command_arguments)
    sort_within_groups: SortWithinGroups = parsed_arguments.sort_within_groups
    pre_commit_runner = create_pre_commit_runner()
    exit_code = pre_commit_runner.run(
        parsed_arguments.files,
        sort_decorated_methods=parsed_arguments.sort_decorated_methods,
        sort_within_groups=sort_within_groups,
    )
    return exit_code

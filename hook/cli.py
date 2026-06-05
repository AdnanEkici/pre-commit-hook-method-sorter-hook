from __future__ import annotations

import argparse
import sys
from pathlib import Path

from hook.sorter import SortWithinGroups, sort_python_source


def parse_arguments(command_line_arguments: list[str]) -> argparse.Namespace:
    argument_parser = argparse.ArgumentParser(
        prog="method-sorter-hook",
        description="Sort Python class methods according to configurable method groups.",
    )

    argument_parser.add_argument(
        "files",
        nargs="*",
        help="Python files passed by pre-commit.",
    )

    argument_parser.add_argument(
        "--check",
        action="store_true",
        help="Do not rewrite files. Return non-zero if changes are needed.",
    )

    argument_parser.add_argument(
        "--sort-decorated-methods",
        action="store_true",
        help="Allow decorated methods to be sorted. Disabled by default.",
    )

    argument_parser.add_argument(
        "--sort-within-groups",
        choices=["preserve", "alphabetical"],
        default="preserve",
        help="How to sort methods inside each group.",
    )

    return argument_parser.parse_args(command_line_arguments)


def process_file(
    file_path: Path,
    *,
    check: bool,
    sort_decorated_methods: bool,
    sort_within_groups: SortWithinGroups,
) -> bool:
    original_source = file_path.read_text(encoding="utf-8")

    updated_source = sort_python_source(
        original_source,
        sort_decorated_methods=sort_decorated_methods,
        sort_within_groups=sort_within_groups,
    )

    if updated_source == original_source:
        return False

    if check:
        print(f"{file_path}: methods are not sorted")
        return True

    file_path.write_text(updated_source, encoding="utf-8")
    print(f"{file_path}: sorted methods")
    return True


def main(command_line_arguments: list[str] | None = None) -> int:
    parsed_arguments = parse_arguments(
        sys.argv[1:] if command_line_arguments is None else command_line_arguments
    )

    changed = False
    failed = False

    for file_name in parsed_arguments.files:
        file_path = Path(file_name)

        if file_path.suffix != ".py":
            continue

        if not file_path.exists():
            continue

        try:
            file_changed = process_file(
                file_path,
                check=parsed_arguments.check,
                sort_decorated_methods=parsed_arguments.sort_decorated_methods,
                sort_within_groups=parsed_arguments.sort_within_groups,
            )
            changed = changed or file_changed
        except Exception as exception:
            failed = True
            print(f"{file_path}: error: {exception}", file=sys.stderr)

    if failed:
        return 1

    if parsed_arguments.check and changed:
        return 1

    return 0
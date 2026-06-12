from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from hook.configuration.sorting_options import SortWithinGroups


class PythonFileRepositoryProtocol(Protocol):
    """File-access behavior required by the pre-commit runner."""

    def read_source(self, file_path: Path) -> str:
        """Read Python source code from a file.

        Args:
            file_path: Path to the Python source file.

        Returns:
            Source code read from the file.
        """
        ...

    def write_source(self, file_path: Path, source: str) -> None:
        """Write Python source code to a file.

        Args:
            file_path: Path to the Python source file.
            source: Source code to write.
        """
        ...


class SourceSorterProtocol(Protocol):
    """Source-sorting behavior required by the pre-commit runner."""

    def sort_python_source(
        self,
        source: str,
        *,
        sort_decorated_methods: bool = False,
        sort_within_groups: SortWithinGroups = "preserve",
    ) -> str:
        """Sort method definitions in Python source code.

        Args:
            source: Python source code to sort.
            sort_decorated_methods: Whether decorated methods should be included
                in sorting.
            sort_within_groups: Strategy for ordering methods within the same
                method group.

        Returns:
            Python source code after method sorting.
        """
        ...


class PreCommitRunner:
    """Run method-sorting checks and rewrites for Python files in a pre-commit hook."""

    def __init__(
        self,
        source_sorter: SourceSorterProtocol,
        python_file_repository: PythonFileRepositoryProtocol,
    ) -> None:
        """Initialize the runner with source-sorting and file-access dependencies.

        Args:
            source_sorter: Service used to sort methods in Python source code.
            python_file_repository: Repository used to read and write Python source files.
        """
        self.source_sorter = source_sorter
        self.python_file_repository = python_file_repository

    def run(
        self,
        file_paths: Sequence[Path],
        *,
        sort_decorated_methods: bool = False,
        sort_within_groups: SortWithinGroups = "preserve",
    ) -> int:
        """Sort methods in the provided Python files and report whether files changed.

        Non-Python files are ignored. Python files whose sorted source differs from
        the original source are overwritten and reported to stdout.

        Args:
            file_paths: Paths to files selected by the pre-commit hook.
            sort_decorated_methods: Whether decorated methods should be included in sorting.
            sort_within_groups: Strategy for ordering methods within sorting groups.

        Returns:
            Exit code for the pre-commit hook. Returns 1 when at least one file was
            changed, otherwise returns 0.
        """
        changed_file_paths: list[Path] = []

        for file_path in file_paths:
            original_source = self.python_file_repository.read_source(file_path)
            sorted_source = self.source_sorter.sort_python_source(
                original_source,
                sort_decorated_methods=sort_decorated_methods,
                sort_within_groups=sort_within_groups,
            )

            if sorted_source != original_source:
                self.python_file_repository.write_source(file_path, sorted_source)
                changed_file_paths.append(file_path)

        if changed_file_paths:
            print("Sorted methods in:")
            for changed_file_path in changed_file_paths:
                print(f"  {changed_file_path}")
            return 1

        return 0


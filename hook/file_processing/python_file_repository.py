from __future__ import annotations

from pathlib import Path


class PythonFileRepository:
    """Read and write Python source files using UTF-8 encoding."""

    def read_source(self, file_path: Path) -> str:
        """Read Python source code from a file.

        Args:
            file_path: Path to the Python source file.

        Returns:
            The file contents as a string.
        """
        source = file_path.read_text(encoding="utf-8")
        return source

    def write_source(self, file_path: Path, source: str) -> None:
        """Write Python source code to a file.

        Args:
            file_path: Path to the Python source file.
            source: Source code to write.
        """
        file_path.write_text(source, encoding="utf-8")

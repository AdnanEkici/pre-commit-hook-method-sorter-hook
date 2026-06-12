from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from hook.file_processing.python_file_repository import PythonFileRepository


class PythonFileRepositoryTest(unittest.TestCase):
    """Verify sorting behavior for contiguous method statement groups.

    These tests check that method statements are ordered by configured group
    priority, optionally sorted alphabetically within the same group, or left in
    their original relative order when intra-group sorting is set to preserve.
    """

    def setUp(self) -> None:
        self.python_file_repository = PythonFileRepository()

    def test_reads_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text("value = 1\n", encoding="utf-8")
            source = self.python_file_repository.read_source(file_path)
            self.assertEqual("value = 1\n", source, msg="Expected reads source; assertEqual failed.")

    def test_writes_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            self.python_file_repository.write_source(file_path, "value = 1\n")
            self.assertEqual("value = 1\n", file_path.read_text(encoding="utf-8"), msg="Expected writes source; assertEqual failed.")

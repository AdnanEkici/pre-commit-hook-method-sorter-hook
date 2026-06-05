import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from hook.cli import main, parse_arguments, process_file


class TestCommandLineArguments(unittest.TestCase):
    def test_parse_arguments_defaults(self) -> None:
        parsed_arguments = parse_arguments(["example.py"])

        self.assertEqual(parsed_arguments.files, ["example.py"])
        self.assertFalse(parsed_arguments.check)
        self.assertFalse(parsed_arguments.sort_decorated_methods)
        self.assertEqual(parsed_arguments.sort_within_groups, "preserve")

    def test_parse_arguments_with_options(self) -> None:
        parsed_arguments = parse_arguments(
            [
                "--check",
                "--sort-decorated-methods",
                "--sort-within-groups=alphabetical",
                "example.py",
            ]
        )

        self.assertEqual(parsed_arguments.files, ["example.py"])
        self.assertTrue(parsed_arguments.check)
        self.assertTrue(parsed_arguments.sort_decorated_methods)
        self.assertEqual(parsed_arguments.sort_within_groups, "alphabetical")


class TestProcessFile(unittest.TestCase):
    def test_process_file_rewrites_unsorted_file(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        pass
'''

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(source, encoding="utf-8")

            changed = process_file(
                file_path,
                check=False,
                sort_decorated_methods=False,
                sort_within_groups="preserve",
            )

            self.assertTrue(changed)
            self.assertEqual(file_path.read_text(encoding="utf-8"), expected)

    def test_process_file_check_does_not_rewrite_file(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    def __init__(self):
        pass
'''

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(source, encoding="utf-8")

            changed = process_file(
                file_path,
                check=True,
                sort_decorated_methods=False,
                sort_within_groups="preserve",
            )

            self.assertTrue(changed)
            self.assertEqual(file_path.read_text(encoding="utf-8"), source)

    def test_process_file_returns_false_when_no_change_needed(self) -> None:
        source = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        pass
'''

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(source, encoding="utf-8")

            changed = process_file(
                file_path,
                check=False,
                sort_decorated_methods=False,
                sort_within_groups="preserve",
            )

            self.assertFalse(changed)
            self.assertEqual(file_path.read_text(encoding="utf-8"), source)


class TestMain(unittest.TestCase):
    def test_main_returns_zero_for_sorted_file(self) -> None:
        source = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        pass
'''

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(source, encoding="utf-8")

            exit_code = main([str(file_path)])

            self.assertEqual(exit_code, 0)

    def test_main_returns_zero_after_rewriting_unsorted_file(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    def __init__(self):
        pass
'''

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(source, encoding="utf-8")

            exit_code = main([str(file_path)])

            self.assertEqual(exit_code, 0)

    def test_main_returns_one_in_check_mode_when_change_needed(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    def __init__(self):
        pass
'''

        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(source, encoding="utf-8")

            exit_code = main(["--check", str(file_path)])

            self.assertEqual(exit_code, 1)

    def test_main_skips_non_python_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.txt"
            file_path.write_text("not python", encoding="utf-8")

            exit_code = main([str(file_path)])

            self.assertEqual(exit_code, 0)

    def test_main_returns_one_when_processing_raises_exception(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text("class", encoding="utf-8")

            exit_code = main([str(file_path)])

            self.assertEqual(exit_code, 1)

    def test_main_uses_sys_arguments_when_no_arguments_are_provided(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            file_path = Path(temporary_directory) / "example.py"
            file_path.write_text(
                '''\
class Example:
    def __init__(self):
        pass
''',
                encoding="utf-8",
            )

            with patch("sys.argv", ["method-sorter-hook", str(file_path)]):
                exit_code = main()

            self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
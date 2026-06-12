from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class TopLevelFunctionScenariosTest(unittest.TestCase):
    """Verify that top-level functions are not affected by class method sorting.

    These tests check that module-level function definitions remain in their
    original order and are not classified, grouped, or reordered by the method
    sorter, which only targets methods inside class bodies.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_does_not_sort_public_protected_and_private_top_level_functions(self) -> None:
        source = """\
def __private_function():
    pass

def _protected_function():
    pass

def public_function():
    pass
"""

        expected_source = """\
def __private_function():
    pass

def _protected_function():
    pass

def public_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected top-level public, protected, and private functions to " "remain unchanged because only methods inside classes are sorted."
            ),
        )

    def test_does_not_sort_top_level_functions_alphabetically_when_requested(self) -> None:
        source = """\
def zebra_function():
    pass

def alpha_function():
    pass

def build_function():
    pass
"""

        expected_source = """\
def zebra_function():
    pass

def alpha_function():
    pass

def build_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level functions to remain unchanged even when " "alphabetical sorting is requested."),
        )

    def test_does_not_sort_dunder_top_level_functions(self) -> None:
        source = """\
def __str__():
    return "example"

def __init__():
    pass

def __repr__():
    return "Example()"
"""

        expected_source = """\
def __str__():
    return "example"

def __init__():
    pass

def __repr__():
    return "Example()"
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected dunder-style top-level functions to remain unchanged " "because dunder grouping applies only to class methods."),
        )

    def test_does_not_sort_decorated_top_level_functions_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
@decorator
def decorated_function():
    pass

def regular_function():
    pass

@another_decorator
def another_decorated_function():
    pass
"""

        expected_source = """\
@decorator
def decorated_function():
    pass

def regular_function():
    pass

@another_decorator
def another_decorated_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected decorated top-level functions to remain unchanged when "
                "decorated method sorting is disabled because top-level functions "
                "are outside class bodies."
            ),
        )

    def test_does_not_sort_decorated_top_level_functions_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
@decorator
def zebra_function():
    pass

@decorator
def alpha_function():
    pass

def build_function():
    pass
"""

        expected_source = """\
@decorator
def zebra_function():
    pass

@decorator
def alpha_function():
    pass

def build_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected decorated top-level functions to remain unchanged even " "when decorated sorting and alphabetical sorting are enabled."),
        )

    def test_does_not_sort_abstract_top_level_functions(self) -> None:
        source = """\
@abc.abstractmethod
def abstract_function():
    pass

def public_function():
    pass
"""

        expected_source = """\
@abc.abstractmethod
def abstract_function():
    pass

def public_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            sort_decorated_methods=True,
            source=source,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected abstract-style top-level functions to remain unchanged "
                "because abstract method classification applies only inside class "
                "method sorting."
            ),
        )

    def test_preserves_top_level_function_comments(self) -> None:
        source = """\
# Zebra comment
def zebra_function():
    pass

# Alpha comment
def alpha_function():
    pass
"""

        expected_source = """\
# Zebra comment
def zebra_function():
    pass

# Alpha comment
def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected comments attached to top-level functions to remain in "
                "their original positions because top-level functions are not sorted."
            ),
        )

    def test_preserves_multiple_top_level_function_comment_lines(self) -> None:
        source = """\
# Zebra comment line one
# Zebra comment line two
def zebra_function():
    pass

# Alpha comment line one
# Alpha comment line two
def alpha_function():
    pass
"""

        expected_source = """\
# Zebra comment line one
# Zebra comment line two
def zebra_function():
    pass

# Alpha comment line one
# Alpha comment line two
def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected multiple comment lines attached to top-level functions " "to remain unchanged because top-level functions are not sorted."
            ),
        )

    def test_preserves_top_level_function_docstrings(self) -> None:
        source = '''\
def zebra_function():
    """Return zebra result."""
    return "zebra"

def alpha_function():
    """Return alpha result."""
    return "alpha"
'''

        expected_source = '''\
def zebra_function():
    """Return zebra result."""
    return "zebra"

def alpha_function():
    """Return alpha result."""
    return "alpha"
'''

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level function docstrings to remain unchanged because " "top-level functions are not sorted."),
        )

    def test_preserves_top_level_function_type_annotations(self) -> None:
        source = """\
def zebra_function(value: int) -> str:
    return str(value)

def alpha_function(value: str) -> int:
    return len(value)
"""

        expected_source = """\
def zebra_function(value: int) -> str:
    return str(value)

def alpha_function(value: str) -> int:
    return len(value)
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level function annotations to remain unchanged because " "top-level functions are not sorted."),
        )

    def test_preserves_inline_top_level_function_bodies(self) -> None:
        source = """\
def zebra_function(): return "zebra"

def alpha_function(): return "alpha"
"""

        expected_source = """\
def zebra_function(): return "zebra"

def alpha_function(): return "alpha"
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected inline top-level function bodies to remain unchanged " "because top-level functions are not sorted."),
        )

    def test_does_not_move_top_level_functions_across_module_variable(self) -> None:
        source = """\
def zebra_function():
    pass

VALUE = create_value()

def alpha_function():
    pass
"""

        expected_source = """\
def zebra_function():
    pass

VALUE = create_value()

def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level functions not to move across module variables " "because module-level statements are not sorted."),
        )

    def test_does_not_move_top_level_functions_across_imports(self) -> None:
        source = """\
def zebra_function():
    pass

import os

def alpha_function():
    pass
"""

        expected_source = """\
def zebra_function():
    pass

import os

def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level functions not to move across imports because " "module-level statements are not sorted."),
        )

    def test_does_not_move_top_level_functions_across_if_statement(self) -> None:
        source = """\
def zebra_function():
    pass

if CONDITION:
    VALUE = 1

def alpha_function():
    pass
"""

        expected_source = """\
def zebra_function():
    pass

if CONDITION:
    VALUE = 1

def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level functions not to move across module-level " "if statements because module-level statements are not sorted."),
        )

    def test_does_not_sort_functions_inside_top_level_if_statement(self) -> None:
        source = """\
if CONDITION:
    def zebra_function():
        pass

    def alpha_function():
        pass
"""

        expected_source = """\
if CONDITION:
    def zebra_function():
        pass

    def alpha_function():
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected functions nested inside module-level if statements to " "remain unchanged because only class bodies are sorted."),
        )

    def test_does_not_sort_functions_inside_top_level_function(self) -> None:
        source = """\
def outer_function():
    def zebra_function():
        pass

    def alpha_function():
        pass

    return alpha_function()
"""

        expected_source = """\
def outer_function():
    def zebra_function():
        pass

    def alpha_function():
        pass

    return alpha_function()
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected nested functions inside a top-level function to remain " "unchanged because only class bodies are sorted."),
        )

    def test_sorts_methods_inside_class_but_not_surrounding_top_level_functions(self) -> None:
        source = """\
def module_before():
    pass

class Example:
    def __private(self):
        pass

    def public(self):
        pass

def module_after():
    pass
"""

        expected_source = """\
def module_before():
    pass

class Example:
    def public(self):
        pass

    def __private(self):
        pass

def module_after():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected class methods to be sorted while top-level functions " "before and after the class remain unchanged."),
        )

    def test_does_not_sort_functions_inside_class_method_body(self) -> None:
        source = """\
class Example:
    def method(self):
        def zebra_function():
            pass

        def alpha_function():
            pass

        return alpha_function()
"""

        expected_source = """\
class Example:
    def method(self):
        def zebra_function():
            pass

        def alpha_function():
            pass

        return alpha_function()
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected local functions inside a method body to remain unchanged " "because only direct class-body methods are sorted."),
        )

    def test_does_not_sort_functions_inside_nested_function_inside_method(self) -> None:
        source = """\
class Example:
    def method(self):
        def outer_function():
            def zebra_function():
                pass

            def alpha_function():
                pass

            return alpha_function()

        return outer_function()
"""

        expected_source = """\
class Example:
    def method(self):
        def outer_function():
            def zebra_function():
                pass

            def alpha_function():
                pass

            return alpha_function()

        return outer_function()
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected deeply nested local functions inside a method body to " "remain unchanged because local function bodies are not sorted."),
        )

    def test_preserves_async_top_level_function_order(self) -> None:
        source = """\
async def zebra_function():
    pass

async def alpha_function():
    pass

async def build_function():
    pass
"""

        expected_source = """\
async def zebra_function():
    pass

async def alpha_function():
    pass

async def build_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected async top-level functions to remain unchanged because " "only methods inside classes are sorted."),
        )

    def test_preserves_mixed_sync_and_async_top_level_function_order(self) -> None:
        source = """\
async def zebra_function():
    pass

def alpha_function():
    pass

async def build_function():
    pass
"""

        expected_source = """\
async def zebra_function():
    pass

def alpha_function():
    pass

async def build_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected mixed sync and async top-level functions to remain " "unchanged because only methods inside classes are sorted."),
        )

    def test_preserves_top_level_function_order_with_overload_decorators(self) -> None:
        source = """\
@typing.overload
def load(value: str) -> str:
    ...

@typing.overload
def load(value: int) -> int:
    ...

def load(value):
    return value

def build():
    pass
"""

        expected_source = """\
@typing.overload
def load(value: str) -> str:
    ...

@typing.overload
def load(value: int) -> int:
    ...

def load(value):
    return value

def build():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level overload functions to remain unchanged because " "overload grouping applies only to class-body method sorting."),
        )

    def test_preserves_top_level_property_like_function_order(self) -> None:
        source = """\
@property
def zebra_function():
    pass

@property
def alpha_function():
    pass
"""

        expected_source = """\
@property
def zebra_function():
    pass

@property
def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level property-like functions to remain unchanged " "because property grouping applies only inside class bodies."),
        )

    def test_top_level_constant_class_and_top_level_functions_remain_in_module_order(self) -> None:
        source = """\
class TerminalColors:
    RED = "\\033[91m"
    END = "\\033[0m"

def zebra_function():
    pass

def alpha_function():
    pass
"""

        expected_source = """\
class TerminalColors:
    RED = "\\033[91m"
    END = "\\033[0m"

def zebra_function():
    pass

def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level constant-only class and top-level functions " "to remain in module order."),
        )

    def test_top_level_utility_functions_and_generator_functions_remain_unchanged(self) -> None:
        source = """\
def natural_keys(text):
    return [
        atoi(character)
        for character in re.split(r"(\\d+)", text)
    ]

def atoi(text):
    return int(text) if text.isdigit() else text

def iterate_values(values):
    for value in values:
        yield value
"""

        expected_source = """\
def natural_keys(text):
    return [
        atoi(character)
        for character in re.split(r"(\\d+)", text)
    ]

def atoi(text):
    return int(text) if text.isdigit() else text

def iterate_values(values):
    for value in values:
        yield value
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level utility and generator functions to remain " "unchanged because only class bodies are sorted."),
        )

    def test_imports_constants_functions_and_classes_keep_module_level_order(self) -> None:
        source = """\
import os
import re

PROJECT_NAME = "example"

def zebra_function():
    pass

class Example:
    def __private(self):
        pass

    def public(self):
        pass

def alpha_function():
    pass
"""

        expected_source = """\
import os
import re

PROJECT_NAME = "example"

def zebra_function():
    pass

class Example:
    def public(self):
        pass

    def __private(self):
        pass

def alpha_function():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected module-level imports, constants, and functions to keep " "their order while class bodies are sorted."),
        )

    def test_does_not_sort_multiple_local_functions_inside_private_method(self) -> None:
        source = """\
class DatasetManager:
    def __export_custom_dataset(self):
        def zebra_writer():
            pass

        def alpha_writer():
            pass

        return alpha_writer()
"""

        expected_source = """\
class DatasetManager:
    def __export_custom_dataset(self):
        def zebra_writer():
            pass

        def alpha_writer():
            pass

        return alpha_writer()
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected local functions inside a private method to remain " "unchanged because only direct class-body methods are sorted."),
        )

    def test_does_not_sort_local_functions_inside_staticmethod(self) -> None:
        source = """\
class DatasetManager:
    @staticmethod
    def duplicate_finder(values):
        def zebra_comparator(first_value, second_value):
            return first_value == second_value

        def alpha_comparator(first_value, second_value):
            return first_value.lower() == second_value.lower()

        return values
"""

        expected_source = """\
class DatasetManager:
    @staticmethod
    def duplicate_finder(values):
        def zebra_comparator(first_value, second_value):
            return first_value == second_value

        def alpha_comparator(first_value, second_value):
            return first_value.lower() == second_value.lower()

        return values
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected local functions inside staticmethod bodies to remain "
                "unchanged because sorting applies only to direct class-body methods."
            ),
        )

    def test_does_not_sort_branch_specific_local_functions_inside_method(self) -> None:
        source = """\
class DatasetManager:
    def chunker(self, mode):
        if mode == "copy":
            def zebra_move_file(source_path, target_path):
                pass

            def alpha_move_file(source_path, target_path):
                pass

        elif mode == "move":
            def gamma_move_file(source_path, target_path):
                pass

            def beta_move_file(source_path, target_path):
                pass

        else:
            def fallback_move_file(source_path, target_path):
                pass

        return mode
"""

        expected_source = """\
class DatasetManager:
    def chunker(self, mode):
        if mode == "copy":
            def zebra_move_file(source_path, target_path):
                pass

            def alpha_move_file(source_path, target_path):
                pass

        elif mode == "move":
            def gamma_move_file(source_path, target_path):
                pass

            def beta_move_file(source_path, target_path):
                pass

        else:
            def fallback_move_file(source_path, target_path):
                pass

        return mode
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected branch-specific local functions inside method bodies to " "remain unchanged because local scopes are not sorted."),
        )

    def test_does_not_move_top_level_functions_across_module_level_function_call(self) -> None:
        source = """\
def create_logger(**keyword_arguments):
    return keyword_arguments

create_logger(kwargs={})

def get_logger():
    return logging.getLogger()
"""

        expected_source = """\
def create_logger(**keyword_arguments):
    return keyword_arguments

create_logger(kwargs={})

def get_logger():
    return logging.getLogger()
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level functions not to move across module-level " "function calls because module-level statements are not sorted."),
        )

    def test_preserves_local_helper_function_inside_top_level_function(self) -> None:
        source = """\
def fix_image_path(image_path):
    def case_sensitive_path_search(path):
        return path

    fixed_path = case_sensitive_path_search(image_path)
    return fixed_path
"""

        expected_source = """\
def fix_image_path(image_path):
    def case_sensitive_path_search(path):
        return path

    fixed_path = case_sensitive_path_search(image_path)
    return fixed_path
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected local helper function inside a top-level function to " "remain unchanged because only class bodies are sorted."),
        )

    def test_preserves_top_level_function_default_call_expression(self) -> None:
        source = """\
def create_video_from_frames(
    output_path,
    four_character_code=cv2.VideoWriter_fourcc(*"MPEG"),
):
    return output_path
"""

        expected_source = """\
def create_video_from_frames(
    output_path,
    four_character_code=cv2.VideoWriter_fourcc(*"MPEG"),
):
    return output_path
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level function default call expression to remain " "unchanged because top-level functions are not sorted."),
        )

from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class DunderMethodScenariosTest(unittest.TestCase):
    """Verify sorting behavior for Python dunder methods.

    These tests check that special double-underscore methods are recognized as
    their own method group and are ordered before regular public, protected, and
    private methods according to the configured method sorting rules.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_keeps_dunder_methods_before_public_methods(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    def __init__(self):
        self.value = 1

    def build(self):
        pass
"""

        expected = """\
class Example:
    def __init__(self):
        self.value = 1

    def run(self):
        pass

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to be sorted before public methods " "according to method group order."),
        )

    def test_preserves_dunder_method_order_when_preserving_group_order(self) -> None:
        source = """\
class Example:
    def __str__(self):
        return "example"

    def __init__(self):
        self.value = 1

    def __repr__(self):
        return "Example()"
"""

        expected = """\
class Example:
    def __str__(self):
        return "example"

    def __init__(self):
        self.value = 1

    def __repr__(self):
        return "Example()"
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to keep their original order when " "sort_within_groups is preserve."),
        )

    def test_sorts_dunder_methods_alphabetically_when_requested(self) -> None:
        source = """\
class Example:
    def __str__(self):
        return "example"

    def __init__(self):
        self.value = 1

    def __repr__(self):
        return "Example()"
"""

        expected = """\
class Example:
    def __init__(self):
        self.value = 1

    def __repr__(self):
        return "Example()"

    def __str__(self):
        return "example"
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to be sorted alphabetically by method " "name when sort_within_groups is alphabetical."),
        )

    def test_keeps_dunder_methods_before_property_methods(self) -> None:
        source = """\
class Example:
    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to be sorted before property methods " "according to method group order."),
        )

    def test_keeps_dunder_methods_before_decorated_methods_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class Example:
    @staticmethod
    def create():
        return Example()

    def __init__(self):
        self.value = 1
"""

        expected = """\
class Example:
    def __init__(self):
        self.value = 1

    @staticmethod
    def create():
        return Example()
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to be sorted before decorated methods " "when decorated method sorting is enabled."),
        )

    def test_does_not_sort_dunder_method_across_decorated_method_boundary_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
class Example:
    @staticmethod
    def create():
        return Example()

    def __init__(self):
        self.value = 1
"""

        expected = """\
class Example:
    @staticmethod
    def create():
        return Example()

    def __init__(self):
        self.value = 1
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected decorated methods to create a sorting boundary when "
                "decorated method sorting is disabled, so __init__ is not moved "
                "across the staticmethod."
            ),
        )

    def test_keeps_dunder_methods_before_protected_and_private_methods(self) -> None:
        source = """\
class Example:
    def _protected(self):
        pass

    def __private(self):
        pass

    def __len__(self):
        return 1
"""

        expected = """\
class Example:
    def __len__(self):
        return 1

    def _protected(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to be sorted before protected and " "private methods according to method group order."),
        )

    def test_preserves_dunder_method_comments(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    # Constructor comment
    def __init__(self):
        self.value = 1
"""

        expected = """\
class Example:
    # Constructor comment
    def __init__(self):
        self.value = 1

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected comments attached to dunder methods to move with the " "dunder method during sorting."),
        )

    def test_preserves_multiple_dunder_method_comment_lines(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    # Constructor comment line one
    # Constructor comment line two
    def __init__(self):
        self.value = 1
"""

        expected = """\
class Example:
    # Constructor comment line one
    # Constructor comment line two
    def __init__(self):
        self.value = 1

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected multiple comment lines attached to a dunder method to " "move with that method during sorting."),
        )

    def test_preserves_dunder_method_docstring(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    def __repr__(self):
        """Return a developer representation."""
        return "Example()"
'''

        expected = '''\
class Example:
    def __repr__(self):
        """Return a developer representation."""
        return "Example()"

    def run(self):
        pass
'''

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder method docstring to remain inside the method body " "when the dunder method is moved."),
        )

    def test_preserves_dunder_method_type_annotations(self) -> None:
        source = """\
class Example:
    def run(self) -> None:
        pass

    def __len__(self) -> int:
        return 1
"""

        expected = """\
class Example:
    def __len__(self) -> int:
        return 1

    def run(self) -> None:
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder method return annotations to be preserved when " "dunder methods are sorted."),
        )

    def test_preserves_inline_dunder_method_body(self) -> None:
        source = """\
class Example:
    def run(self): pass

    def __len__(self): return 1
"""

        expected = """\
class Example:
    def __len__(self): return 1

    def run(self): pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected inline dunder method bodies to be preserved when dunder " "methods are sorted."),
        )

    def test_does_not_move_dunder_method_across_class_attribute(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    value = create_value()

    def __init__(self):
        self.value = value
"""

        expected = """\
class Example:
    def run(self):
        pass

    value = create_value()

    def __init__(self):
        self.value = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to sort only inside their contiguous " "method group and not move across class attributes."),
        )

    def test_does_not_move_dunder_method_across_nested_class(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    class Nested:
        pass

    def __init__(self):
        self.value = 1
"""

        expected = """\
class Example:
    def run(self):
        pass

    class Nested:
        pass

    def __init__(self):
        self.value = 1
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to sort only inside their contiguous " "method group and not move across nested class definitions."),
        )

    def test_sorts_dunder_methods_inside_nested_class(self) -> None:
        source = """\
class Outer:
    class Inner:
        def run(self):
            pass

        def __init__(self):
            self.value = 1
"""

        expected = """\
class Outer:
    class Inner:
        def __init__(self):
            self.value = 1

        def run(self):
            pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods inside nested classes to be sorted because " "nested class definitions are visited."),
        )

    def test_keeps_common_object_dunder_methods_together(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    def __str__(self):
        return "example"

    def __repr__(self):
        return "Example()"

    def __bool__(self):
        return True
"""

        expected = """\
class Example:
    def __str__(self):
        return "example"

    def __repr__(self):
        return "Example()"

    def __bool__(self):
        return True

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected common object dunder methods to stay in the dunder " "group and remain before public methods."),
        )

    def test_sorts_common_object_dunder_methods_alphabetically_when_requested(self) -> None:
        source = """\
class Example:
    def __str__(self):
        return "example"

    def __repr__(self):
        return "Example()"

    def __bool__(self):
        return True
"""

        expected = """\
class Example:
    def __bool__(self):
        return True

    def __repr__(self):
        return "Example()"

    def __str__(self):
        return "example"
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected common object dunder methods to sort alphabetically when " "sort_within_groups is alphabetical."),
        )

    def test_keeps_numeric_dunder_methods_in_dunder_group(self) -> None:
        source = """\
class Example:
    def add_value(self):
        pass

    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __mul__(self, other):
        return self
"""

        expected = """\
class Example:
    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __mul__(self, other):
        return self

    def add_value(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected numeric dunder methods to be classified as dunder " "methods and sorted before public methods."),
        )

    def test_keeps_container_dunder_methods_in_dunder_group(self) -> None:
        source = """\
class Example:
    def items(self):
        return []

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0

    def __contains__(self, item):
        return False
"""

        expected = """\
class Example:
    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0

    def __contains__(self, item):
        return False

    def items(self):
        return []
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected container dunder methods to be classified as dunder " "methods and sorted before public methods."),
        )

    def test_keeps_context_manager_dunder_methods_in_dunder_group(self) -> None:
        source = """\
class Example:
    def open(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        return False
"""

        expected = """\
class Example:
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        return False

    def open(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected context manager dunder methods to be classified as " "dunder methods and sorted before public methods."),
        )

    def test_keeps_async_context_manager_dunder_methods_in_dunder_group(self) -> None:
        source = """\
class Example:
    async def open(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        return False
"""

        expected = """\
class Example:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        return False

    async def open(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected async context manager dunder methods to be classified " "as dunder methods and sorted before public async methods."),
        )

    def test_keeps_del_dunder_method_in_dunder_group(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    def __del__(self):
        self.close()

    def _protected(self):
        pass
"""

        expected_source = """\
class Example:
    def __del__(self):
        self.close()

    def public(self):
        pass

    def _protected(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected __del__ to be classified as a dunder method and sorted " "before public and protected methods."),
        )

    def test_preserves_inherited_class_with_only_iter_dunder_method(self) -> None:
        source = """\
class RandomSplitKeepDefaults(RandomSplit):
    def __iter__(self):
        for split in super().__iter__():
            yield split
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected inherited class with only __iter__ dunder method to " "remain unchanged."),
        )

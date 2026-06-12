from __future__ import annotations

import unittest

from hook.source_processing.source_sorter import SourceSorter
from tests.test_utils import create_source_sorter


class SourceSorterTest(unittest.TestCase):
    """Verify full-source method sorting behavior and preservation rules.

    These tests check that SourceSorter parses and rewrites Python source text
    correctly, supports configured intra-group and decorated-method sorting,
    keeps related property and overload method blocks together, handles nested
    classes recursively, preserves class-attribute boundaries, and leaves already
    sorted or non-sortable class bodies unchanged.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_sorts_python_source(self) -> None:
        source = "class Example:\n    def public(self):\n        pass\n\n    def __init__(self):\n        pass\n"
        sorted_source = self.source_sorter.sort_python_source(source)
        self.assertLess(
            sorted_source.index("def __init__"), sorted_source.index("def public"), msg="Expected sorts python source; assertLess failed."
        )

    def test_sorts_alphabetically_within_groups(self) -> None:
        source = "class Example:\n    def zebra(self):\n        pass\n\n    def alpha(self):\n        pass\n"
        sorted_source = self.source_sorter.sort_python_source(source, sort_within_groups="alphabetical")
        self.assertLess(
            sorted_source.index("def alpha"), sorted_source.index("def zebra"), msg="Expected sorts alphabetically within groups; assertLess failed."
        )

    def test_keeps_injected_class_body_sorter(self) -> None:
        class_body_sorter = self.source_sorter.class_body_sorter
        source_sorter = SourceSorter(class_body_sorter)
        self.assertIs(class_body_sorter, source_sorter.class_body_sorter, msg="Expected keeps injected class body sorter; assertIs failed.")

    def test_sorting_is_idempotent(self) -> None:
        source_sorter = create_source_sorter()
        source = "class Example:\n" "    def public(self):\n" "        pass\n\n" "    def __init__(self):\n" "        pass\n"

        first_sorted_source = source_sorter.sort_python_source(source)
        second_sorted_source = source_sorter.sort_python_source(first_sorted_source)

        self.assertEqual(
            first_sorted_source,
            second_sorted_source,
            msg=("Expected sorting to be idempotent so running the sorter twice " "does not keep modifying the source."),
        )

    def test_keeps_property_family_together(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class Example:\n"
            "    @property\n"
            "    def beta(self):\n"
            "        pass\n\n"
            "    @beta.setter\n"
            "    def beta(self, value):\n"
            "        pass\n\n"
            "    @property\n"
            "    def alpha(self):\n"
            "        pass\n\n"
            "    @alpha.setter\n"
            "    def alpha(self, value):\n"
            "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected each property getter and setter family to remain grouped " "instead of separating all getters from all setters."),
        )

    def test_sorts_property_families_alphabetically_without_splitting_accessors(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class Example:\n"
            "    @property\n"
            "    def beta(self):\n"
            "        pass\n\n"
            "    @beta.setter\n"
            "    def beta(self, value):\n"
            "        pass\n\n"
            "    @property\n"
            "    def alpha(self):\n"
            "        pass\n\n"
            "    @alpha.setter\n"
            "    def alpha(self, value):\n"
            "        pass\n"
        )
        expected_source = (
            "class Example:\n"
            "    @property\n"
            "    def alpha(self):\n"
            "        pass\n\n"
            "    @alpha.setter\n"
            "    def alpha(self, value):\n"
            "        pass\n\n"
            "    @property\n"
            "    def beta(self):\n"
            "        pass\n\n"
            "    @beta.setter\n"
            "    def beta(self, value):\n"
            "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected property families to sort alphabetically by property name " "while keeping each getter and setter together."),
        )

    def test_does_not_sort_across_decorated_method_when_decorated_sorting_is_disabled(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class Example:\n"
            "    def public(self):\n"
            "        pass\n\n"
            "    @staticmethod\n"
            "    def helper():\n"
            "        pass\n\n"
            "    def __init__(self):\n"
            "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(
            source,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected decorated method to split sortable method groups when " "decorated method sorting is disabled."),
        )

    def test_sorts_decorated_method_when_decorated_sorting_is_enabled(self) -> None:
        source_sorter = create_source_sorter()
        source = "class Example:\n" "    @staticmethod\n" "    def helper():\n" "        pass\n\n" "    def __init__(self):\n" "        pass\n"
        expected_source = (
            "class Example:\n" "    def __init__(self):\n" "        pass\n\n" "    @staticmethod\n" "    def helper():\n" "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected decorated method to participate in method sorting when " "decorated method sorting is enabled."),
        )

    def test_sorts_nested_class_methods(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class Outer:\n"
            "    class Inner:\n"
            "        def public(self):\n"
            "            pass\n\n"
            "        def __init__(self):\n"
            "            pass\n"
        )
        expected_source = (
            "class Outer:\n"
            "    class Inner:\n"
            "        def __init__(self):\n"
            "            pass\n\n"
            "        def public(self):\n"
            "            pass\n"
        )

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected nested class methods to be sorted because LibCST visits " "nested class definitions recursively."),
        )

    def test_class_attribute_boundary_is_preserved(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class Example:\n"
            "    def public(self):\n"
            "        pass\n\n"
            "    value = create_value()\n\n"
            "    def __init__(self):\n"
            "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected methods not to move across class attributes because " "class-body assignments can have runtime side effects."),
        )

    def test_overload_group_is_preserved_in_full_source(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class Example:\n"
            "    def public(self):\n"
            "        pass\n\n"
            "    @overload\n"
            "    def value(self, item: int) -> int:\n"
            "        ...\n\n"
            "    @overload\n"
            "    def value(self, item: str) -> str:\n"
            "        ...\n\n"
            "    def value(self, item):\n"
            "        pass\n\n"
            "    def __init__(self):\n"
            "        pass\n"
        )
        expected_source = (
            "class Example:\n"
            "    def __init__(self):\n"
            "        pass\n\n"
            "    @overload\n"
            "    def value(self, item: int) -> int:\n"
            "        ...\n\n"
            "    @overload\n"
            "    def value(self, item: str) -> str:\n"
            "        ...\n\n"
            "    def value(self, item):\n"
            "        pass\n\n"
            "    def public(self):\n"
            "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected overload definitions and their implementation to move " "as one method block during full-source sorting."),
        )

    def test_already_sorted_source_returns_same_text(self) -> None:
        source_sorter = create_source_sorter()
        source = "class Example:\n" "    def __init__(self):\n" "        pass\n\n" "    def public(self):\n" "        pass\n"

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg="Expected already sorted source to remain byte-for-byte unchanged.",
        )

    def test_empty_class_returns_same_text(self) -> None:
        source_sorter = create_source_sorter()
        source = "class Example:\n    pass\n"

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg="Expected empty class body with pass statement to remain unchanged.",
        )

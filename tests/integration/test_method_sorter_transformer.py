from __future__ import annotations

import unittest

from hook.source_processing.method_sorter_transformer import MethodSorterTransformer
from tests.test_utils import create_source_sorter
from tests.test_utils import parse_first_class


class MethodSorterTransformerTest(unittest.TestCase):
    """Verify CST transformation behavior for sorting methods inside class definitions.

    These tests check that source-level sorting updates class bodies through the
    transformer, respects method-sorter skip comments in module and class-leading
    positions, and safely returns unchanged class definitions when their bodies
    are not indented blocks.
    """

    def test_sorts_class_definition_body(self) -> None:
        source_sorter = create_source_sorter()
        source = "class Example:\n    def public(self):\n        pass\n\n    def __init__(self):\n        pass\n"
        sorted_source = source_sorter.sort_python_source(source)
        self.assertLess(
            sorted_source.index("def __init__"), sorted_source.index("def public"), msg="Expected sorts class definition body; assertLess failed."
        )

    def test_respects_skip_comment(self) -> None:
        source_sorter = create_source_sorter()
        source = "# method-sorter: skip\nclass Example:\n    def public(self):\n        pass\n\n    def __init__(self):\n        pass\n"
        sorted_source = source_sorter.sort_python_source(source)
        self.assertEqual(source, sorted_source, msg="Expected respects skip comment; assertEqual failed.")

    def test_returns_updated_node_when_body_is_not_indented_block(self) -> None:
        class_definition = parse_first_class("class Example: ...\n")
        class_body_sorter = create_source_sorter().class_body_sorter
        method_sorter_transformer = MethodSorterTransformer(class_body_sorter, sort_decorated_methods=False, sort_within_groups="preserve")
        updated_class_definition = method_sorter_transformer.leave_ClassDef(class_definition, class_definition)
        self.assertIs(
            class_definition, updated_class_definition, msg="Expected returns updated node when body is not indented block; assertIs failed."
        )

    def test_respects_skip_comment_in_module_header_for_first_class(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "# method-sorter: skip\n" "class Example:\n" "    def public(self):\n" "        pass\n\n" "    def __init__(self):\n" "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected first class to remain unchanged when the skip comment " "appears at the top of the file before the class definition."),
        )

    def test_respects_skip_comment_before_later_class(self) -> None:
        source_sorter = create_source_sorter()
        source = (
            "class First:\n"
            "    def public(self):\n"
            "        pass\n\n"
            "# method-sorter: skip\n"
            "class Second:\n"
            "    def public(self):\n"
            "        pass\n\n"
            "    def __init__(self):\n"
            "        pass\n"
        )

        sorted_source = source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected later class to remain unchanged when the skip comment " "appears directly before that class definition."),
        )

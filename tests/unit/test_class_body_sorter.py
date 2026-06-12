from __future__ import annotations

import unittest

from hook.method_ordering.method_group_spacing_normalizer import MethodGroupSpacingNormalizer
from hook.method_ordering.method_statement_sorter import MethodStatementSorter
from hook.source_processing.class_body_sorter import ClassBodySorter
from tests.test_utils import create_method_block_builder
from tests.test_utils import create_method_classifier
from tests.test_utils import parse_first_class


class ClassBodySorterTest(unittest.TestCase):
    """Verify that class body sorting only reorders contiguous sortable method groups.

    These tests check that methods within the same uninterrupted method block are
    sorted according to method ordering rules, while non-method statements act as
    boundaries that prevent methods from being moved across them.
    """

    def setUp(self) -> None:
        method_classifier = create_method_classifier()
        method_block_builder = create_method_block_builder()
        method_group_spacing_normalizer = MethodGroupSpacingNormalizer()
        method_statement_sorter = MethodStatementSorter(method_block_builder, method_group_spacing_normalizer)
        self.class_body_sorter = ClassBodySorter(method_classifier, method_statement_sorter)

    def test_sorts_contiguous_method_group(self) -> None:
        class_definition = parse_first_class("class Example:\n    def public(self):\n        pass\n\n    def __init__(self):\n        pass\n")
        class_body_statements = list(class_definition.body.body)
        sorted_class_body_statements = self.class_body_sorter.sort_class_body_statements(
            class_body_statements, sort_decorated_methods=False, sort_within_groups="preserve"
        )
        self.assertEqual("__init__", sorted_class_body_statements[0].name.value, msg="Expected sorts contiguous method group; assertEqual failed.")
        self.assertEqual("public", sorted_class_body_statements[1].name.value, msg="Expected sorts contiguous method group; assertEqual failed.")

    def test_does_not_move_methods_across_non_method_statement(self) -> None:
        class_definition = parse_first_class(
            "class Example:\n    def public(self):\n        pass\n\n    value = 1\n\n    def __init__(self):\n        pass\n"
        )
        class_body_statements = list(class_definition.body.body)
        sorted_class_body_statements = self.class_body_sorter.sort_class_body_statements(
            class_body_statements, sort_decorated_methods=False, sort_within_groups="preserve"
        )
        self.assertEqual(
            "public",
            sorted_class_body_statements[0].name.value,
            msg="Expected does not move methods across non method statement; assertEqual failed.",
        )
        self.assertFalse(
            hasattr(sorted_class_body_statements[1], "name"), msg="Expected does not move methods across non method statement; assertFalse failed."
        )
        self.assertEqual(
            "__init__",
            sorted_class_body_statements[2].name.value,
            msg="Expected does not move methods across non method statement; assertEqual failed.",
        )

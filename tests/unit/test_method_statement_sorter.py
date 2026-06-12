from __future__ import annotations

import unittest

from hook.method_ordering.method_group_spacing_normalizer import MethodGroupSpacingNormalizer
from hook.method_ordering.method_statement_sorter import MethodStatementSorter
from tests.test_utils import create_method_block_builder
from tests.test_utils import parse_first_class


class MethodStatementSorterTest(unittest.TestCase):
    """Verify sorting behavior for contiguous method statement groups.

    These tests check that method statements are ordered by configured group
    priority, optionally sorted alphabetically within the same group, or left in
    their original relative order when intra-group sorting is set to preserve.
    """

    def setUp(self) -> None:
        method_block_builder = create_method_block_builder()
        method_group_spacing_normalizer = MethodGroupSpacingNormalizer()
        self.method_statement_sorter = MethodStatementSorter(method_block_builder, method_group_spacing_normalizer)

    def test_sorts_methods_by_group_order(self) -> None:
        class_definition = parse_first_class("class Example:\n    def public(self):\n        pass\n\n    def __init__(self):\n        pass\n")
        method_statements = list(class_definition.body.body)
        sorted_statements = self.method_statement_sorter.sort_method_statement_group(
            method_statements, sort_decorated_methods=False, sort_within_groups="preserve", is_first_class_body_group=True
        )
        self.assertEqual("__init__", sorted_statements[0].name.value, msg="Expected sorts methods by group order; assertEqual failed.")
        self.assertEqual("public", sorted_statements[1].name.value, msg="Expected sorts methods by group order; assertEqual failed.")

    def test_sorts_alphabetically_within_group(self) -> None:
        class_definition = parse_first_class("class Example:\n    def zebra(self):\n        pass\n\n    def alpha(self):\n        pass\n")
        method_statements = list(class_definition.body.body)
        sorted_statements = self.method_statement_sorter.sort_method_statement_group(
            method_statements, sort_decorated_methods=False, sort_within_groups="alphabetical", is_first_class_body_group=True
        )
        self.assertEqual("alpha", sorted_statements[0].name.value, msg="Expected sorts alphabetically within group; assertEqual failed.")
        self.assertEqual("zebra", sorted_statements[1].name.value, msg="Expected sorts alphabetically within group; assertEqual failed.")

    def test_preserves_order_within_group(self) -> None:
        class_definition = parse_first_class("class Example:\n    def zebra(self):\n        pass\n\n    def alpha(self):\n        pass\n")
        method_statements = list(class_definition.body.body)
        sorted_statements = self.method_statement_sorter.sort_method_statement_group(
            method_statements, sort_decorated_methods=False, sort_within_groups="preserve", is_first_class_body_group=True
        )
        self.assertEqual("zebra", sorted_statements[0].name.value, msg="Expected preserves order within group; assertEqual failed.")
        self.assertEqual("alpha", sorted_statements[1].name.value, msg="Expected preserves order within group; assertEqual failed.")

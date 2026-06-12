from __future__ import annotations

import unittest

from hook.method_ordering.method_group_spacing_normalizer import MethodGroupSpacingNormalizer
from tests.test_utils import parse_first_class


class MethodGroupSpacingNormalizerTest(unittest.TestCase):
    """Verify spacing normalization for sorted method groups.

    These tests check that the first method group in a class body starts without
    extra leading blank lines, later method groups receive one leading blank line,
    and leading comments attached to method definitions are preserved.
    """

    def setUp(self) -> None:
        self.method_group_spacing_normalizer = MethodGroupSpacingNormalizer()

    def test_removes_leading_empty_lines_for_first_group_method(self) -> None:
        class_definition = parse_first_class("class Example:\n\n    def build(self):\n        pass\n")
        method_statement = class_definition.body.body[0]
        normalized_statements = self.method_group_spacing_normalizer.normalize([method_statement], is_first_class_body_group=True)
        self.assertEqual(
            [], normalized_statements[0].leading_lines, msg="Expected removes leading empty lines for first group method; assertEqual failed."
        )

    def test_adds_one_empty_line_for_later_group_method(self) -> None:
        class_definition = parse_first_class("class Example:\n    def build(self):\n        pass\n")
        method_statement = class_definition.body.body[0]
        normalized_statements = self.method_group_spacing_normalizer.normalize([method_statement], is_first_class_body_group=False)
        self.assertEqual(
            1, len(normalized_statements[0].leading_lines), msg="Expected adds one empty line for later group method; assertEqual failed."
        )

    def test_preserves_comment_leading_lines(self) -> None:
        class_definition = parse_first_class("class Example:\n    # kept\n    def build(self):\n        pass\n")
        method_statement = class_definition.body.body[0]
        normalized_statement = self.method_group_spacing_normalizer.set_leading_empty_lines(method_statement, [])
        self.assertEqual(1, len(normalized_statement.leading_lines), msg="Expected preserves comment leading lines; assertEqual failed.")
        self.assertIsNotNone(normalized_statement.leading_lines[0].comment, msg="Expected preserves comment leading lines; assertIsNotNone failed.")

from __future__ import annotations

import unittest

from hook.method_analysis.method_information import MethodInformation
from hook.method_ordering.method_block import MethodBlock
from tests.test_utils import parse_first_function


class MethodBlockTest(unittest.TestCase):
    """Verify that method blocks preserve grouped statements and metadata.

    These tests check that a MethodBlock stores its associated CST statements and
    method classification information correctly, and that the frozen dataclass
    prevents reassignment of its fields after creation.
    """

    def test_keeps_statements_and_method_information(self) -> None:
        function_definition = parse_first_function("def build_value():\n    pass\n")
        method_information = MethodInformation(name="build_value", group="public", original_index=0)
        method_block = MethodBlock(statements=[function_definition], method_information=method_information)
        self.assertEqual([function_definition], method_block.statements, msg="Expected keeps statements and method information; assertEqual failed.")
        self.assertEqual(
            method_information, method_block.method_information, msg="Expected keeps statements and method information; assertEqual failed."
        )

    def test_is_immutable(self) -> None:
        function_definition = parse_first_function("def build_value():\n    pass\n")
        method_information = MethodInformation(name="build_value", group="public", original_index=0)
        method_block = MethodBlock(statements=[function_definition], method_information=method_information)
        with self.assertRaises(Exception, msg="Expected immutable method block to reject attribute mutation."):
            method_block.method_information = method_information  # type: ignore[misc]

from __future__ import annotations

import unittest

from tests.test_utils import create_method_block_builder
from tests.test_utils import parse_first_class


class MethodBlockBuilderTest(unittest.TestCase):
    """Verify construction of sortable method blocks from method statements.

    These tests check that regular methods, property accessor families, overload
    groups, and unknown statements are converted into MethodBlock instances with
    the correct grouped statements and method metadata for later sorting.
    """

    def setUp(self) -> None:
        self.method_block_builder = create_method_block_builder()

    def test_builds_regular_method_block(self) -> None:
        class_definition = parse_first_class("class Example:\n    def build(self):\n        pass\n")
        method_statements = list(class_definition.body.body)
        method_blocks = self.method_block_builder.build_method_blocks(method_statements, sort_decorated_methods=False)
        self.assertEqual(1, len(method_blocks), msg="Expected builds regular method block; assertEqual failed.")
        self.assertEqual("build", method_blocks[0].method_information.name, msg="Expected builds regular method block; assertEqual failed.")
        self.assertEqual("public", method_blocks[0].method_information.group, msg="Expected builds regular method block; assertEqual failed.")

    def test_groups_property_getter_and_setter_as_one_method_block(self) -> None:
        class_definition = parse_first_class(
            "class Example:\n"
            "    @property\n"
            "    def value(self):\n"
            "        return self._value\n\n"
            "    @value.setter\n"
            "    def value(self, value):\n"
            "        self._value = value\n"
        )
        method_statements = list(class_definition.body.body)

        method_blocks = self.method_block_builder.build_method_blocks(
            method_statements,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            1,
            len(method_blocks),
            msg="Expected property getter and setter to be grouped into one method block.",
        )
        self.assertEqual(
            2,
            len(method_blocks[0].statements),
            msg="Expected property method block to contain both getter and setter statements.",
        )
        self.assertEqual(
            "value",
            method_blocks[0].method_information.name,
            msg="Expected property method block name to use the property name.",
        )
        self.assertEqual(
            "property",
            method_blocks[0].method_information.group,
            msg="Expected property method block to remain in the property group.",
        )
        self.assertEqual(
            0,
            method_blocks[0].method_information.original_index,
            msg="Expected property method block original index to use getter position.",
        )

    def test_does_not_group_different_property_families(self) -> None:
        class_definition = parse_first_class(
            "class Example:\n"
            "    @property\n"
            "    def beta(self):\n"
            "        return self._beta\n\n"
            "    @beta.setter\n"
            "    def beta(self, value):\n"
            "        self._beta = value\n\n"
            "    @property\n"
            "    def alpha(self):\n"
            "        return self._alpha\n\n"
            "    @alpha.setter\n"
            "    def alpha(self, value):\n"
            "        self._alpha = value\n"
        )
        method_statements = list(class_definition.body.body)

        method_blocks = self.method_block_builder.build_method_blocks(
            method_statements,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            2,
            len(method_blocks),
            msg="Expected each property family to become a separate method block.",
        )
        self.assertEqual(
            "beta",
            method_blocks[0].method_information.name,
            msg="Expected first property block to represent beta family.",
        )
        self.assertEqual(
            2,
            len(method_blocks[0].statements),
            msg="Expected beta property block to contain getter and setter.",
        )
        self.assertEqual(
            "alpha",
            method_blocks[1].method_information.name,
            msg="Expected second property block to represent alpha family.",
        )
        self.assertEqual(
            2,
            len(method_blocks[1].statements),
            msg="Expected alpha property block to contain getter and setter.",
        )

    def test_groups_overload_methods_with_implementation(self) -> None:
        class_definition = parse_first_class(
            "class Example:\n"
            "    @overload\n"
            "    def build(self, value: int) -> int:\n"
            "        ...\n"
            "\n"
            "    @overload\n"
            "    def build(self, value: str) -> str:\n"
            "        ...\n"
            "\n"
            "    def build(self, value):\n"
            "        return value\n"
        )
        method_statements = list(class_definition.body.body)
        method_blocks = self.method_block_builder.build_method_blocks(method_statements, sort_decorated_methods=False)
        self.assertEqual(1, len(method_blocks), msg="Expected groups overload methods with implementation; assertEqual failed.")
        self.assertEqual(3, len(method_blocks[0].statements), msg="Expected groups overload methods with implementation; assertEqual failed.")
        self.assertEqual(
            "decorated_public",
            method_blocks[0].method_information.group,
            msg="Expected groups overload methods with implementation; assertEqual failed.",
        )

    def test_stops_overload_group_at_different_name(self) -> None:
        class_definition = parse_first_class(
            "class Example:\n    @overload\n    def build(self, value: int) -> int:\n        ...\n\n    def other(self):\n        pass\n"
        )
        method_statements = list(class_definition.body.body)
        method_blocks = self.method_block_builder.build_method_blocks(method_statements, sort_decorated_methods=False)
        self.assertEqual(2, len(method_blocks), msg="Expected stops overload group at different name; assertEqual failed.")
        self.assertEqual(1, len(method_blocks[0].statements), msg="Expected stops overload group at different name; assertEqual failed.")

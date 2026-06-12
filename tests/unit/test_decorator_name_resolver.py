from __future__ import annotations

import unittest

import libcst as concrete_syntax_tree

from hook.method_analysis.decorator_name_resolver import DecoratorNameResolver


class DecoratorNameResolverTest(unittest.TestCase):
    """Verify that decorator expressions are resolved to usable string names.

    These tests cover simple decorator names, dotted attribute decorators, and
    called decorators, while also confirming that unsupported expression types
    safely resolve to an empty string.
    """

    def setUp(self) -> None:
        self.decorator_name_resolver = DecoratorNameResolver()

    def test_resolves_simple_name(self) -> None:
        expression = concrete_syntax_tree.Name("property")
        decorator_name = self.decorator_name_resolver.resolve(expression)
        self.assertEqual("property", decorator_name, msg="Expected resolves simple name; assertEqual failed.")

    def test_resolves_attribute_name(self) -> None:
        expression = concrete_syntax_tree.parse_expression("typing.overload")
        decorator_name = self.decorator_name_resolver.resolve(expression)
        self.assertEqual("typing.overload", decorator_name, msg="Expected resolves attribute name; assertEqual failed.")

    def test_resolves_called_decorator_name(self) -> None:
        expression = concrete_syntax_tree.parse_expression("validator()")
        decorator_name = self.decorator_name_resolver.resolve(expression)
        self.assertEqual("validator", decorator_name, msg="Expected resolves called decorator name; assertEqual failed.")

    def test_returns_empty_name_for_unknown_expression(self) -> None:
        expression = concrete_syntax_tree.parse_expression("1")
        decorator_name = self.decorator_name_resolver.resolve(expression)
        self.assertEqual("", decorator_name, msg="Expected returns empty name for unknown expression; assertEqual failed.")

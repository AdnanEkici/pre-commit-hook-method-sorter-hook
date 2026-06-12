from __future__ import annotations

import unittest

import libcst as concrete_syntax_tree

from tests.test_utils import create_method_classifier
from tests.test_utils import parse_first_class
from tests.test_utils import parse_first_function


class MethodClassifierTest(unittest.TestCase):
    """Verify method classification rules used by the method sorter.

    These tests cover how CST statements are recognized as methods, how methods
    are grouped by special cases such as dunder, property, abstract, and decorated
    methods, and how visibility conventions affect classification and sortability.
    """

    def setUp(self) -> None:
        self.method_classifier = create_method_classifier()

    def test_get_function_definition_returns_function_definition(self) -> None:
        function_definition = parse_first_function("def build_value():\n    pass\n")
        result = self.method_classifier.get_function_definition(function_definition)
        self.assertIs(function_definition, result, msg="Expected get function definition returns function definition; assertIs failed.")

    def test_get_function_definition_returns_none_for_non_function(self) -> None:
        statement = concrete_syntax_tree.parse_statement("value = 1\n")
        result = self.method_classifier.get_function_definition(statement)
        self.assertIsNone(result, msg="Expected get function definition returns none for non function; assertIsNone failed.")

    def test_classifies_dunder_method(self) -> None:
        function_definition = parse_first_function("def __init__():\n    pass\n")
        method_group = self.method_classifier.classify(function_definition, sort_decorated_methods=False)
        self.assertEqual("dunder", method_group, msg="Expected classifies dunder method; assertEqual failed.")

    def test_classifies_property_method(self) -> None:
        function_definition = parse_first_class("class Example:\n    @property\n    def value(self):\n        return 1\n").body.body[0]
        method_group = self.method_classifier.classify(function_definition, sort_decorated_methods=False)
        self.assertEqual("property", method_group, msg="Expected classifies property method; assertEqual failed.")

    def test_classifies_abstract_method(self) -> None:
        function_definition = parse_first_class("class Example:\n    @abstractmethod\n    def build(self):\n        pass\n").body.body[0]
        method_group = self.method_classifier.classify(function_definition, sort_decorated_methods=False)
        self.assertEqual("abstract_public", method_group, msg="Expected classifies abstract method; assertEqual failed.")

    def test_classifies_decorated_method_when_enabled(self) -> None:
        function_definition = parse_first_class("class Example:\n    @decorator\n    def build(self):\n        pass\n").body.body[0]
        method_group = self.method_classifier.classify(function_definition, sort_decorated_methods=True)
        self.assertEqual("decorated_public", method_group, msg="Expected classifies decorated method when enabled; assertEqual failed.")

    def test_classifies_visibility(self) -> None:
        self.assertEqual("public", self.method_classifier.classify_visibility("build"), msg="Expected classifies visibility; assertEqual failed.")
        self.assertEqual("protected", self.method_classifier.classify_visibility("_build"), msg="Expected classifies visibility; assertEqual failed.")
        self.assertEqual("private", self.method_classifier.classify_visibility("__build"), msg="Expected classifies visibility; assertEqual failed.")

    def test_identifies_sortable_decorated_method_when_disabled(self) -> None:
        function_definition = parse_first_class("class Example:\n    @decorator\n    def build(self):\n        pass\n").body.body[0]
        is_sortable_method = self.method_classifier.is_sortable_method_statement(function_definition, sort_decorated_methods=False)
        self.assertFalse(is_sortable_method, msg="Expected identifies sortable decorated method when disabled; assertFalse failed.")

    def test_identifies_sortable_decorated_method_when_enabled(self) -> None:
        function_definition = parse_first_class("class Example:\n    @decorator\n    def build(self):\n        pass\n").body.body[0]
        is_sortable_method = self.method_classifier.is_sortable_method_statement(function_definition, sort_decorated_methods=True)
        self.assertTrue(is_sortable_method, msg="Expected identifies sortable decorated method when enabled; assertTrue failed.")

    def test_gets_property_order(self) -> None:
        class_definition = parse_first_class("class Example:\n    @value.setter\n    def value(self, value):\n        self._value = value\n")
        function_definition = class_definition.body.body[0]
        property_order = self.method_classifier.get_property_order(function_definition)
        self.assertEqual(1, property_order, msg="Expected gets property order; assertEqual failed.")

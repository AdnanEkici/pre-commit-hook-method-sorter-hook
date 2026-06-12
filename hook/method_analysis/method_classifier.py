from __future__ import annotations

import libcst as concrete_syntax_tree

from hook.method_analysis.decorator_name_resolver import DecoratorNameResolver


class MethodClassifier:
    """Classify class methods into sorting groups based on name and decorators."""

    def __init__(self, decorator_name_resolver: DecoratorNameResolver) -> None:
        """Initialize the classifier with a decorator name resolver.

        Args:
            decorator_name_resolver: Resolver used to convert decorator expressions to names.
        """
        self.decorator_name_resolver = decorator_name_resolver

    def get_function_definition(
        self,
        class_body_statement: concrete_syntax_tree.BaseStatement,
    ) -> concrete_syntax_tree.FunctionDef | None:
        """Return the function definition represented by a class body statement.

        Args:
            class_body_statement: Statement from a class body.

        Returns:
            The function definition when the statement is a method, otherwise None.
        """
        function_definition = None
        if isinstance(class_body_statement, concrete_syntax_tree.FunctionDef):
            function_definition = class_body_statement

        return function_definition

    def is_sortable_method_statement(
        self,
        class_body_statement: concrete_syntax_tree.BaseStatement,
        *,
        sort_decorated_methods: bool,
    ) -> bool:
        """Determine whether a class body statement is eligible for method sorting.

        Args:
            class_body_statement: Statement from a class body.
            sort_decorated_methods: Whether decorated methods should be included in sorting.

        Returns:
            True if the statement is a sortable method, otherwise False.
        """
        function_definition = self.get_function_definition(class_body_statement)

        if function_definition is None:
            is_sortable_method = False
        elif self.is_overload_method(function_definition):
            is_sortable_method = True
        elif self.is_property_method(function_definition):
            is_sortable_method = True
        elif self.is_abstract_method(function_definition):
            is_sortable_method = True
        elif self.is_dunder(function_definition.name.value):
            is_sortable_method = True
        elif self.has_decorators(function_definition) and not sort_decorated_methods:
            is_sortable_method = False
        else:
            is_sortable_method = True

        return is_sortable_method

    def classify(
        self,
        function_definition: concrete_syntax_tree.FunctionDef,
        *,
        sort_decorated_methods: bool,
    ) -> str:
        """Classify a method into a sorting group.

        Args:
            function_definition: Method definition to classify.
            sort_decorated_methods: Whether decorated methods should be assigned to decorated groups.

        Returns:
            Sorting group name for the method.
        """
        method_name = function_definition.name.value

        if self.is_dunder(method_name):
            method_group = "dunder"
        elif self.is_property_method(function_definition):
            method_group = "property"
        else:
            method_group = self._classify_non_special_method(
                function_definition,
                sort_decorated_methods=sort_decorated_methods,
            )

        return method_group

    def classify_visibility(self, method_name: str) -> str:
        """Classify a method name by visibility convention.

        Args:
            method_name: Method name to classify.

        Returns:
            One of public, protected, or private.
        """
        if self.is_private(method_name):
            method_visibility = "private"
        elif self.is_protected(method_name):
            method_visibility = "protected"
        else:
            method_visibility = "public"

        return method_visibility

    def is_dunder(self, method_name: str) -> bool:
        """Return whether a method name follows the dunder convention.

        Args:
            method_name: Method name to inspect.

        Returns:
            True if the method name starts and ends with double underscores, otherwise False.
        """
        is_dunder_method = method_name.startswith("__") and method_name.endswith("__") and len(method_name) > 4
        return is_dunder_method

    def is_private(self, method_name: str) -> bool:
        """Return whether a method name follows the private convention.

        Args:
            method_name: Method name to inspect.

        Returns:
            True if the method name starts with double underscores and is not dunder, otherwise False.
        """
        is_private_method = method_name.startswith("__") and not method_name.endswith("__")
        return is_private_method

    def is_protected(self, method_name: str) -> bool:
        """Return whether a method name follows the protected convention.

        Args:
            method_name: Method name to inspect.

        Returns:
            True if the method name starts with a single underscore, otherwise False.
        """
        is_protected_method = method_name.startswith("_") and not method_name.startswith("__")
        return is_protected_method

    def has_decorators(self, function_definition: concrete_syntax_tree.FunctionDef) -> bool:
        """Return whether a method has decorators.

        Args:
            function_definition: Method definition to inspect.

        Returns:
            True if the method has at least one decorator, otherwise False.
        """
        has_method_decorators = bool(function_definition.decorators)
        return has_method_decorators

    def is_property_method(
        self,
        function_definition: concrete_syntax_tree.FunctionDef,
    ) -> bool:
        """Return whether a method is part of a property definition.

        Args:
            function_definition: Method definition to inspect.

        Returns:
            True if the method has property, setter, or deleter decorators, otherwise False.
        """
        property_method_found = False

        for decorator in function_definition.decorators:
            decorator_name = self.decorator_name_resolver.resolve(decorator.decorator)

            if decorator_name == "property":
                property_method_found = True
                break

            if decorator_name.endswith(".property"):
                property_method_found = True
                break

            if decorator_name.endswith(".setter"):
                property_method_found = True
                break

            if decorator_name.endswith(".deleter"):
                property_method_found = True
                break

        return property_method_found

    def get_property_order(self, function_definition: concrete_syntax_tree.FunctionDef) -> int:
        """Return the sort order for a property accessor method.

        Args:
            function_definition: Method definition to inspect.

        Returns:
            Order value for property accessors: 0 for getter, 1 for setter,
            2 for deleter, and 999 when no property accessor decorator is found.
        """
        property_order = 999

        for decorator in function_definition.decorators:
            decorator_name = self.decorator_name_resolver.resolve(decorator.decorator)

            if decorator_name == "property" or decorator_name.endswith(".property"):
                property_order = 0
                break

            if decorator_name.endswith(".setter"):
                property_order = 1
                break

            if decorator_name.endswith(".deleter"):
                property_order = 2
                break

        return property_order

    def is_abstract_method(self, function_definition: concrete_syntax_tree.FunctionDef) -> bool:
        """Return whether a method is marked as abstract.

        Args:
            function_definition: Method definition to inspect.

        Returns:
            True if the method has an abstractmethod decorator, otherwise False.
        """
        is_abstract_method = self._has_decorator_name(
            function_definition,
            exact_names={"abstractmethod"},
            suffixes={".abstractmethod"},
        )
        return is_abstract_method

    def is_overload_method(self, function_definition: concrete_syntax_tree.FunctionDef) -> bool:
        """Return whether a method is marked as an overload.

        Args:
            function_definition: Method definition to inspect.

        Returns:
            True if the method has an overload decorator, otherwise False.
        """
        is_overload_method = self._has_decorator_name(
            function_definition,
            exact_names={"overload"},
            suffixes={".overload"},
        )
        return is_overload_method

    def _classify_non_special_method(
        self,
        function_definition: concrete_syntax_tree.FunctionDef,
        *,
        sort_decorated_methods: bool,
    ) -> str:
        """Classify a non-dunder, non-property method into a sorting group.

        Args:
            function_definition: Method definition to classify.
            sort_decorated_methods: Whether decorated methods should be assigned to decorated groups.

        Returns:
            Sorting group name for the method.
        """
        method_name = function_definition.name.value
        method_visibility = self.classify_visibility(method_name)

        if self.is_abstract_method(function_definition):
            method_group = f"abstract_{method_visibility}"
        elif self.has_decorators(function_definition):
            if sort_decorated_methods:
                method_group = f"decorated_{method_visibility}"
            else:
                method_group = "unknown"
        else:
            method_group = method_visibility

        return method_group

    def _has_decorator_name(
        self,
        function_definition: concrete_syntax_tree.FunctionDef,
        *,
        exact_names: set[str],
        suffixes: set[str],
    ) -> bool:
        """Return whether a method has a decorator matching the provided names.

        Args:
            function_definition: Method definition to inspect.
            exact_names: Decorator names that must match exactly.
            suffixes: Decorator name suffixes that are accepted as matches.

        Returns:
            True if any decorator matches an exact name or suffix, otherwise False.
        """
        has_matching_decorator = False

        for decorator in function_definition.decorators:
            decorator_name = self.decorator_name_resolver.resolve(decorator.decorator)

            if decorator_name in exact_names:
                has_matching_decorator = True
                break

            if any(decorator_name.endswith(suffix) for suffix in suffixes):
                has_matching_decorator = True
                break

        return has_matching_decorator

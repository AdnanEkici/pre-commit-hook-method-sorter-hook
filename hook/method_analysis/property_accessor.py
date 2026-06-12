from __future__ import annotations

from dataclasses import dataclass

import libcst as concrete_syntax_tree

from hook.method_analysis.decorator_name_resolver import DecoratorNameResolver


@dataclass(frozen=True)
class PropertyAccessorInformation:
    """Store metadata for a property accessor method."""

    property_name: str
    accessor_order: int


class PropertyAccessorResolver:
    """Resolve property accessor information from method decorators."""

    def __init__(self, decorator_name_resolver: DecoratorNameResolver) -> None:
        """Initialize the resolver with a decorator name resolver.

        Args:
            decorator_name_resolver: Resolver used to convert decorator expressions to names.
        """
        self.decorator_name_resolver = decorator_name_resolver

    def get_property_accessor_information(
        self,
        function_definition: concrete_syntax_tree.FunctionDef,
    ) -> PropertyAccessorInformation | None:
        """Return property accessor metadata for a function definition.

        Recognizes property getters, setters, and deleters from their decorators.

        Args:
            function_definition: Function definition to inspect.

        Returns:
            Property accessor information when the function is a property accessor,
            otherwise None.
        """
        property_accessor_information = None

        for decorator in function_definition.decorators:
            decorator_name = self.decorator_name_resolver.resolve(decorator.decorator)

            if decorator_name == "property" or decorator_name.endswith(".property"):
                property_accessor_information = PropertyAccessorInformation(
                    property_name=function_definition.name.value,
                    accessor_order=0,
                )
                break

            if decorator_name.endswith(".setter"):
                property_accessor_information = PropertyAccessorInformation(
                    property_name=function_definition.name.value,
                    accessor_order=1,
                )
                break

            if decorator_name.endswith(".deleter"):
                property_accessor_information = PropertyAccessorInformation(
                    property_name=function_definition.name.value,
                    accessor_order=2,
                )
                break

        return property_accessor_information

    def is_property_accessor(
        self,
        function_definition: concrete_syntax_tree.FunctionDef,
    ) -> bool:
        """Return whether a function definition is a property accessor.

        Args:
            function_definition: Function definition to inspect.

        Returns:
            True if the function is a property getter, setter, or deleter,
            otherwise False.
        """
        property_accessor_information = self.get_property_accessor_information(function_definition)
        property_accessor_exists = property_accessor_information is not None
        return property_accessor_exists

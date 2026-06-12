from __future__ import annotations

import libcst as concrete_syntax_tree

from hook.method_analysis.method_classifier import MethodClassifier
from hook.method_analysis.method_information import MethodInformation
from hook.method_analysis.property_accessor import PropertyAccessorResolver
from hook.method_ordering.method_block import MethodBlock


class MethodBlockBuilder:
    """Build sortable method blocks from class body method statements."""

    def __init__(
        self,
        method_classifier: MethodClassifier,
        property_accessor_resolver: PropertyAccessorResolver,
    ) -> None:
        """_summary_

        Args:
            method_classifier (MethodClassifier): _description_
            property_accessor_resolver (PropertyAccessorResolver): _description_
        """
        self.method_classifier = method_classifier
        self.property_accessor_resolver = property_accessor_resolver

    def build_method_blocks(
        self,
        method_statements: list[concrete_syntax_tree.BaseStatement],
        *,
        sort_decorated_methods: bool,
    ) -> list[MethodBlock]:
        """Build method blocks from class body statements.

        Groups related overload definitions and property accessors into shared
        blocks while keeping regular methods as single-statement blocks.

        Args:
            method_statements: Class body statements to convert into method blocks.
            sort_decorated_methods: Whether decorated methods should be assigned
                to decorated sorting groups.

        Returns:
            Method blocks built from the provided statements.
        """
        method_blocks: list[MethodBlock] = []
        method_statement_index = 0

        while method_statement_index < len(method_statements):
            method_statement = method_statements[method_statement_index]
            function_definition = self.method_classifier.get_function_definition(method_statement)

            if function_definition is None:
                method_block = self._build_unknown_method_block(
                    method_statement,
                    method_statement_index,
                )
                method_blocks.append(method_block)
                method_statement_index += 1
                continue

            if self.method_classifier.is_overload_method(function_definition):
                method_block = self._build_overload_method_block(
                    method_statements,
                    start_index=method_statement_index,
                    function_definition=function_definition,
                )
                method_blocks.append(method_block)
                method_statement_index += len(method_block.statements)
                continue

            if self.property_accessor_resolver.is_property_accessor(function_definition):
                method_block = self._build_property_method_block(
                    method_statements,
                    start_index=method_statement_index,
                    function_definition=function_definition,
                )
                method_blocks.append(method_block)
                method_statement_index += len(method_block.statements)
                continue

            method_block = self._build_regular_method_block(
                method_statement,
                method_statement_index=method_statement_index,
                function_definition=function_definition,
                sort_decorated_methods=sort_decorated_methods,
            )
            method_blocks.append(method_block)
            method_statement_index += 1

        return method_blocks

    def _build_unknown_method_block(
        self,
        method_statement: concrete_syntax_tree.BaseStatement,
        method_statement_index: int,
    ) -> MethodBlock:
        """Build a method block for a statement that cannot be classified as a method.

        Args:
            method_statement: Statement to wrap in an unknown method block.
            method_statement_index: Original index of the statement in the method list.

        Returns:
            Method block with unknown method information.
        """
        method_block = MethodBlock(
            statements=[method_statement],
            method_information=MethodInformation(
                name="",
                group="unknown",
                original_index=method_statement_index,
            ),
        )
        return method_block

    def _build_regular_method_block(
        self,
        method_statement: concrete_syntax_tree.BaseStatement,
        *,
        method_statement_index: int,
        function_definition: concrete_syntax_tree.FunctionDef,
        sort_decorated_methods: bool,
    ) -> MethodBlock:
        """Build a method block for a regular method definition.

        Args:
            method_statement: Statement containing the method definition.
            method_statement_index: Original index of the statement in the method list.
            function_definition: Function definition represented by the statement.
            sort_decorated_methods: Whether decorated methods should be assigned
                to decorated sorting groups.

        Returns:
            Method block containing the regular method statement.
        """
        method_group = self.method_classifier.classify(
            function_definition,
            sort_decorated_methods=sort_decorated_methods,
        )

        method_block = MethodBlock(
            statements=[method_statement],
            method_information=MethodInformation(
                name=function_definition.name.value,
                group=method_group,
                original_index=method_statement_index,
            ),
        )
        return method_block

    def _build_property_method_block(
        self,
        method_statements: list[concrete_syntax_tree.BaseStatement],
        *,
        start_index: int,
        function_definition: concrete_syntax_tree.FunctionDef,
    ) -> MethodBlock:
        """Build a method block for related property accessor methods.

        Consecutive accessors for the same property are grouped together and ordered
        by accessor type while preserving original order within the same accessor type.

        Args:
            method_statements: Method statements available for block construction.
            start_index: Index where the property accessor block starts.
            function_definition: First function definition in the property block.

        Returns:
            Method block containing related property accessor statements.
        """
        property_accessor_information = self.property_accessor_resolver.get_property_accessor_information(function_definition)

        if property_accessor_information is None:
            method_block = self._build_unknown_method_block(
                method_statements[start_index],
                start_index,
            )
            return method_block

        property_name = property_accessor_information.property_name
        property_accessors = [
            (
                method_statements[start_index],
                property_accessor_information.accessor_order,
                start_index,
            )
        ]
        property_block_index = start_index + 1

        while property_block_index < len(method_statements):
            next_method_statement = method_statements[property_block_index]
            next_function_definition = self.method_classifier.get_function_definition(next_method_statement)

            if next_function_definition is None:
                break

            next_property_accessor_information = self.property_accessor_resolver.get_property_accessor_information(next_function_definition)

            if next_property_accessor_information is None:
                break

            if next_property_accessor_information.property_name != property_name:
                break

            property_accessors.append(
                (
                    next_method_statement,
                    next_property_accessor_information.accessor_order,
                    property_block_index,
                )
            )
            property_block_index += 1

        ordered_property_accessors = sorted(
            property_accessors,
            key=lambda property_accessor: (
                property_accessor[1],
                property_accessor[2],
            ),
        )

        property_block_statements = [property_accessor[0] for property_accessor in ordered_property_accessors]

        method_block = MethodBlock(
            statements=property_block_statements,
            method_information=MethodInformation(
                name=property_name,
                group="property",
                original_index=start_index,
            ),
        )
        return method_block

    def _build_overload_method_block(
        self,
        method_statements: list[concrete_syntax_tree.BaseStatement],
        *,
        start_index: int,
        function_definition: concrete_syntax_tree.FunctionDef,
    ) -> MethodBlock:
        """Build a method block for overload definitions of the same method.

        Consecutive overload definitions with the same name are grouped together,
        including the concrete implementation that follows the overload declarations.

        Args:
            method_statements: Method statements available for block construction.
            start_index: Index where the overload block starts.
            function_definition: First function definition in the overload block.

        Returns:
            Method block containing related overload statements.
        """
        overload_method_name = function_definition.name.value
        overload_block_statements = [method_statements[start_index]]
        overload_block_index = start_index + 1

        while overload_block_index < len(method_statements):
            next_method_statement = method_statements[overload_block_index]
            next_function_definition = self.method_classifier.get_function_definition(next_method_statement)

            if next_function_definition is None:
                break

            if next_function_definition.name.value != overload_method_name:
                break

            overload_block_statements.append(next_method_statement)

            if not self.method_classifier.is_overload_method(next_function_definition):
                overload_block_index += 1
                break

            overload_block_index += 1

        method_visibility = self.method_classifier.classify_visibility(overload_method_name)

        method_block = MethodBlock(
            statements=overload_block_statements,
            method_information=MethodInformation(
                name=overload_method_name,
                group=f"decorated_{method_visibility}",
                original_index=start_index,
            ),
        )
        return method_block

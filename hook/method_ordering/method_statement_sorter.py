from __future__ import annotations

import libcst as concrete_syntax_tree

from hook.configuration.sorting_options import SortWithinGroups
from hook.method_analysis.method_information import MethodInformation
from hook.method_ordering.group_order import METHOD_GROUP_ORDER
from hook.method_ordering.method_block import MethodBlock
from hook.method_ordering.method_block_builder import MethodBlockBuilder
from hook.method_ordering.method_group_spacing_normalizer import MethodGroupSpacingNormalizer


class MethodStatementSorter:
    """Sort method statements by configured method group and intra-group order."""

    def __init__(
        self,
        method_block_builder: MethodBlockBuilder,
        method_group_spacing_normalizer: MethodGroupSpacingNormalizer,
    ) -> None:
        """Initialize the sorter with method block and spacing dependencies.

        Args:
            method_block_builder: Builder used to group related method statements into blocks.
            method_group_spacing_normalizer: Normalizer used to adjust spacing after sorting.
        """
        self.method_block_builder = method_block_builder
        self.method_group_spacing_normalizer = method_group_spacing_normalizer

    def sort_method_statement_group(
        self,
        method_statements: list[concrete_syntax_tree.BaseStatement],
        *,
        sort_decorated_methods: bool,
        sort_within_groups: SortWithinGroups,
        is_first_class_body_group: bool,
    ) -> list[concrete_syntax_tree.BaseStatement]:
        """Sort a contiguous group of method statements.

        Method statements are grouped into blocks before sorting so related overloads
        and property accessors remain together.

        Args:
            method_statements: Method statements to sort.
            sort_decorated_methods: Whether decorated methods should be included in sorting.
            sort_within_groups: Strategy for ordering methods within the same group.
            is_first_class_body_group: Whether this group is the first group in the class body.

        Returns:
            Sorted method statements with normalized leading spacing.
        """
        method_blocks = self.method_block_builder.build_method_blocks(
            method_statements,
            sort_decorated_methods=sort_decorated_methods,
        )
        sorted_method_blocks = sorted(
            method_blocks,
            key=lambda method_block: self.get_method_sort_key(
                method_block.method_information,
                sort_within_groups=sort_within_groups,
            ),
        )
        sorted_method_statements = self._flatten_method_blocks(sorted_method_blocks)
        normalized_method_statements = self.method_group_spacing_normalizer.normalize(
            sorted_method_statements,
            is_first_class_body_group=is_first_class_body_group,
        )
        return normalized_method_statements

    def get_method_sort_key(
        self,
        method_information: MethodInformation,
        *,
        sort_within_groups: SortWithinGroups,
    ) -> tuple[int, str | int]:
        """Build the sort key for a method.

        Args:
            method_information: Classification and original-position metadata for the method.
            sort_within_groups: Strategy for ordering methods within the same group.

        Returns:
            Tuple containing the method group order and either the method name or
            original index, depending on the configured intra-group sorting strategy.
        """
        method_group_index = METHOD_GROUP_ORDER.get(
            method_information.group,
            METHOD_GROUP_ORDER["unknown"],
        )

        method_sort_key: tuple[int, str | int]
        if sort_within_groups == "alphabetical":
            method_sort_key = (method_group_index, method_information.name)
        else:
            method_sort_key = (method_group_index, method_information.original_index)

        return method_sort_key

    def _flatten_method_blocks(
        self,
        method_blocks: list[MethodBlock],
    ) -> list[concrete_syntax_tree.BaseStatement]:
        """Flatten method blocks into a statement list.

        Args:
            method_blocks: Method blocks to flatten.

        Returns:
            Ordered method statements from all blocks.
        """
        method_statements: list[concrete_syntax_tree.BaseStatement] = []

        for method_block in method_blocks:
            method_statements.extend(method_block.statements)

        return method_statements

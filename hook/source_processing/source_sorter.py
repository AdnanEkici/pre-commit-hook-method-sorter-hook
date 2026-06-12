from __future__ import annotations

import libcst as concrete_syntax_tree

from hook.configuration.sorting_options import SortWithinGroups
from hook.source_processing.class_body_sorter import ClassBodySorter
from hook.source_processing.method_sorter_transformer import MethodSorterTransformer


class SourceSorter:
    """Sort method definitions within Python source code."""

    def __init__(self, class_body_sorter: ClassBodySorter) -> None:
        """Initialize the source sorter with a class body sorter.

        Args:
            class_body_sorter: Sorter used to reorder method statements inside class bodies.
        """
        self.class_body_sorter = class_body_sorter

    def sort_python_source(
        self,
        source: str,
        *,
        sort_decorated_methods: bool = False,
        sort_within_groups: SortWithinGroups = "preserve",
    ) -> str:
        """Sort method definitions in Python source code.

        Args:
            source: Python source code to parse and sort.
            sort_decorated_methods: Whether decorated methods should be included in sorting.
            sort_within_groups: Strategy for ordering methods within the same group.

        Returns:
            Python source code after applying method sorting.
        """
        module = concrete_syntax_tree.parse_module(source)
        method_sorter_transformer = MethodSorterTransformer(
            self.class_body_sorter,
            sort_decorated_methods=sort_decorated_methods,
            sort_within_groups=sort_within_groups,
        )
        updated_module = module.visit(method_sorter_transformer)
        sorted_source = updated_module.code
        return sorted_source

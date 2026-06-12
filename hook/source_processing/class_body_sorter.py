from __future__ import annotations

import libcst as concrete_syntax_tree

from hook.configuration.sorting_options import SortWithinGroups
from hook.method_analysis.method_classifier import MethodClassifier
from hook.method_ordering.method_statement_sorter import MethodStatementSorter


class ClassBodySorter:
    """Sort sortable method groups within a class body while preserving other statements."""

    def __init__(
        self,
        method_classifier: MethodClassifier,
        method_statement_sorter: MethodStatementSorter,
    ) -> None:
        """Initialize the sorter with method classification and sorting dependencies.

        Args:
            method_classifier: Classifier used to identify sortable method statements.
            method_statement_sorter: Sorter used to order contiguous groups of method statements.
        """
        self.method_classifier = method_classifier
        self.method_statement_sorter = method_statement_sorter

    def sort_class_body_statements(
        self,
        class_body_statements: list[concrete_syntax_tree.BaseStatement],
        *,
        sort_decorated_methods: bool,
        sort_within_groups: SortWithinGroups,
    ) -> list[concrete_syntax_tree.BaseStatement]:
        """Sort sortable method groups within class body statements.

        Contiguous sortable method statements are collected, sorted, and inserted
        back into the class body. Non-sortable statements split method groups and
        remain in their original relative positions.

        Args:
            class_body_statements: Statements from a class body.
            sort_decorated_methods: Whether decorated methods should be included in sorting.
            sort_within_groups: Strategy for ordering methods within the same group.

        Returns:
            Class body statements with sortable method groups sorted.
        """
        sorted_class_body_statements: list[concrete_syntax_tree.BaseStatement] = []
        method_statement_group: list[concrete_syntax_tree.BaseStatement] = []

        for class_body_statement in class_body_statements:
            if self.method_classifier.is_sortable_method_statement(
                class_body_statement,
                sort_decorated_methods=sort_decorated_methods,
            ):
                method_statement_group.append(class_body_statement)
            else:
                sorted_class_body_statements = self._append_sorted_method_group(
                    sorted_class_body_statements,
                    method_statement_group,
                    sort_decorated_methods=sort_decorated_methods,
                    sort_within_groups=sort_within_groups,
                )
                method_statement_group = []
                sorted_class_body_statements.append(class_body_statement)

        sorted_class_body_statements = self._append_sorted_method_group(
            sorted_class_body_statements,
            method_statement_group,
            sort_decorated_methods=sort_decorated_methods,
            sort_within_groups=sort_within_groups,
        )
        return sorted_class_body_statements

    def _append_sorted_method_group(
        self,
        sorted_class_body_statements: list[concrete_syntax_tree.BaseStatement],
        method_statement_group: list[concrete_syntax_tree.BaseStatement],
        *,
        sort_decorated_methods: bool,
        sort_within_groups: SortWithinGroups,
    ) -> list[concrete_syntax_tree.BaseStatement]:
        """Append a sorted method group to accumulated class body statements.

        Args:
            sorted_class_body_statements: Class body statements accumulated so far.
            method_statement_group: Contiguous sortable method statements to sort and append.
            sort_decorated_methods: Whether decorated methods should be included in sorting.
            sort_within_groups: Strategy for ordering methods within the same group.

        Returns:
            Updated class body statements with the sorted method group appended.
        """
        if not method_statement_group:
            updated_class_body_statements = sorted_class_body_statements
        else:
            sorted_method_statement_group = self.method_statement_sorter.sort_method_statement_group(
                method_statement_group,
                sort_decorated_methods=sort_decorated_methods,
                sort_within_groups=sort_within_groups,
                is_first_class_body_group=not sorted_class_body_statements,
            )
            updated_class_body_statements = [
                *sorted_class_body_statements,
                *sorted_method_statement_group,
            ]

        return updated_class_body_statements

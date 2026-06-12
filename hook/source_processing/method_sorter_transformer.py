from __future__ import annotations

import libcst

from hook.configuration.sorting_options import SortWithinGroups
from hook.source_processing.class_body_sorter import ClassBodySorter


class MethodSorterTransformer(libcst.CSTTransformer):
    """Transform class definitions by sorting their method statements."""

    def __init__(
        self,
        class_body_sorter: ClassBodySorter,
        *,
        sort_decorated_methods: bool,
        sort_within_groups: SortWithinGroups,
    ) -> None:
        """Initialize the transformer with sorting configuration.

        Args:
            class_body_sorter: Sorter used to reorder class body statements.
            sort_decorated_methods: Whether decorated methods should be included in sorting.
            sort_within_groups: Strategy for ordering methods within the same group.
        """
        self.class_body_sorter = class_body_sorter
        self.sort_decorated_methods = sort_decorated_methods
        self.sort_within_groups = sort_within_groups
        self.module_header_has_skip_comment = False
        self.first_class_definition_processed = False

    def visit_Module(
        self,
        node: libcst.Module,
    ) -> bool:
        """Record whether the module header contains a method-sorter skip comment.

        Args:
            node: Module currently being visited.

        Returns:
            True so child nodes continue to be visited.
        """
        self.module_header_has_skip_comment = self.has_skip_comment_in_empty_lines(node.header)
        should_visit_children = True
        return should_visit_children

    def leave_ClassDef(
        self,
        original_node: libcst.ClassDef,
        updated_node: libcst.ClassDef,
    ) -> libcst.ClassDef:
        """Sort method statements when leaving a class definition.

        Classes marked with a method-sorter skip comment are returned unchanged.

        Args:
            original_node: Original class definition before child transformations.
            updated_node: Updated class definition after child transformations.

        Returns:
            Class definition with sorted method statements, or the unchanged updated node
            when sorting is skipped or produces no changes.
        """
        should_skip_class = self.should_skip_class_definition(original_node)

        self.first_class_definition_processed = True

        if should_skip_class:
            transformed_class_definition = updated_node
            return transformed_class_definition

        class_body = updated_node.body

        if not isinstance(class_body, libcst.IndentedBlock):
            transformed_class_definition = updated_node
            return transformed_class_definition

        class_body_statements = list(class_body.body)

        sorted_class_body_statements = self.class_body_sorter.sort_class_body_statements(
            class_body_statements,
            sort_decorated_methods=self.sort_decorated_methods,
            sort_within_groups=self.sort_within_groups,
        )

        if sorted_class_body_statements == class_body_statements:
            transformed_class_definition = updated_node
            return transformed_class_definition

        transformed_class_definition = updated_node.with_changes(body=class_body.with_changes(body=sorted_class_body_statements))
        return transformed_class_definition

    def should_skip_class_definition(
        self,
        class_definition: libcst.ClassDef,
    ) -> bool:
        """Return whether sorting should be skipped for a class definition.

        A class is skipped when its leading lines contain the skip comment. The first
        class in a module is also skipped when the skip comment appears in the module
        header.

        Args:
            class_definition: Class definition to inspect.

        Returns:
            True if the class should not be sorted, otherwise False.
        """
        class_leading_lines_have_skip_comment = self.has_skip_comment_in_empty_lines(class_definition.leading_lines)

        module_header_should_skip_first_class = self.module_header_has_skip_comment and not self.first_class_definition_processed

        should_skip_class = class_leading_lines_have_skip_comment or module_header_should_skip_first_class

        return should_skip_class

    def has_skip_comment_in_empty_lines(
        self,
        empty_lines: tuple[libcst.EmptyLine, ...] | list[libcst.EmptyLine],
    ) -> bool:
        """Return whether a sequence of empty lines contains the skip comment.

        Args:
            empty_lines: Empty lines to inspect for a method-sorter skip comment.

        Returns:
            True if a skip comment is present, otherwise False.
        """
        skip_comment_found = False

        for empty_line in empty_lines:
            comment = empty_line.comment

            if comment is None:
                continue

            comment_value = comment.value.strip()

            if comment_value == "# method-sorter: skip":
                skip_comment_found = True
                break

        return skip_comment_found

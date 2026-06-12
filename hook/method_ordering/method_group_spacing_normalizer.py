from __future__ import annotations

from collections.abc import Sequence

import libcst as concrete_syntax_tree


class MethodGroupSpacingNormalizer:
    """Normalize leading blank-line spacing for grouped method statements."""

    def normalize(
        self,
        method_statements: list[concrete_syntax_tree.BaseStatement],
        *,
        is_first_class_body_group: bool,
    ) -> list[concrete_syntax_tree.BaseStatement]:
        """Normalize leading empty lines for a group of method statements.

        The first method in the first class body group receives no leading empty
        line. All other methods receive one leading empty line.

        Args:
            method_statements: Method statements whose leading spacing should be normalized.
            is_first_class_body_group: Whether the group is the first group in the class body.

        Returns:
            Method statements with normalized leading empty lines.
        """
        normalized_method_statements: list[concrete_syntax_tree.BaseStatement] = []

        for method_index, method_statement in enumerate(method_statements):
            if method_index == 0 and is_first_class_body_group:
                normalized_method_statement = self.set_leading_empty_lines(
                    method_statement,
                    [],
                )
            else:
                normalized_method_statement = self.set_leading_empty_lines(
                    method_statement,
                    [concrete_syntax_tree.EmptyLine(indent=False)],
                )

            normalized_method_statements.append(normalized_method_statement)

        return normalized_method_statements

    def set_leading_empty_lines(
        self,
        statement: concrete_syntax_tree.BaseStatement,
        empty_lines: Sequence[concrete_syntax_tree.EmptyLine],
    ) -> concrete_syntax_tree.BaseStatement:
        """Set leading empty lines on a function definition.

        Existing leading comment lines are preserved after the provided empty lines.
        Non-function statements are returned unchanged.

        Args:
            statement: Statement whose leading lines should be updated.
            empty_lines: Empty lines to place before preserved comment lines.

        Returns:
            Updated statement with adjusted leading lines, or the original statement
            when it is not a function definition.
        """
        if not isinstance(statement, concrete_syntax_tree.FunctionDef):
            updated_statement = statement
        else:
            comment_lines = [leading_line for leading_line in statement.leading_lines if leading_line.comment is not None]
            updated_statement = statement.with_changes(
                leading_lines=[
                    *empty_lines,
                    *comment_lines,
                ],
            )

        return updated_statement

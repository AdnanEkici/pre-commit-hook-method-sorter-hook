from __future__ import annotations

import libcst as concrete_syntax_tree


class DecoratorNameResolver:
    """Resolve decorator expressions to their dotted string names."""

    def resolve(self, expression: concrete_syntax_tree.BaseExpression) -> str:
        if isinstance(expression, concrete_syntax_tree.Name):
            decorator_name = expression.value
        elif isinstance(expression, concrete_syntax_tree.Attribute):
            decorator_name = self._resolve_attribute_name(expression)
        elif isinstance(expression, concrete_syntax_tree.Call):
            decorator_name = self.resolve(expression.func)
        else:
            decorator_name = ""

        return decorator_name

    def _resolve_attribute_name(
        self,
        expression: concrete_syntax_tree.Attribute,
    ) -> str:
        """Resolve a decorator expression to its string name.

        Handles simple names, dotted attribute chains, and called decorators.
        Unsupported expression types resolve to an empty string.

        Args:
            expression: Decorator expression to resolve.

        Returns:
            The resolved decorator name, or an empty string if it cannot be resolved.
        """
        decorator_name_parts: list[str] = []
        current_expression: concrete_syntax_tree.BaseExpression = expression

        while isinstance(current_expression, concrete_syntax_tree.Attribute):
            decorator_name_parts.append(current_expression.attr.value)
            current_expression = current_expression.value

        if isinstance(current_expression, concrete_syntax_tree.Name):
            decorator_name_parts.append(current_expression.value)

        decorator_name = ".".join(reversed(decorator_name_parts))
        return decorator_name

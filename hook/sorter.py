from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Literal

import libcst


SortWithinGroups = Literal["preserve", "alphabetical"]


GROUP_ORDER: dict[str, int] = {
    "dunder": 0,
    "property": 1,
    "abstract_public": 2,
    "abstract_protected": 3,
    "abstract_private": 4,
    "decorated_public": 5,
    "decorated_protected": 6,
    "decorated_private": 7,
    "public": 8,
    "protected": 9,
    "private": 10,
    "unknown": 999,
}


@dataclass(frozen=True)
class MethodInfo:
    name: str
    group: str
    original_index: int


@dataclass(frozen=True)
class MethodBlock:
    statements: list[libcst.BaseStatement]
    method_info: MethodInfo


class MethodSorterTransformer(libcst.CSTTransformer):
    def __init__(
        self,
        *,
        sort_decorated_methods: bool,
        sort_within_groups: SortWithinGroups,
    ) -> None:
        self.sort_decorated_methods = sort_decorated_methods
        self.sort_within_groups = sort_within_groups

    def leave_ClassDef(
        self,
        original_node: libcst.ClassDef,
        updated_node: libcst.ClassDef,
    ) -> libcst.ClassDef:
        if has_method_sorter_skip_comment(original_node):
            return updated_node

        class_body = updated_node.body

        if not isinstance(class_body, libcst.IndentedBlock):
            return updated_node

        class_body_statements = list(class_body.body)

        sorted_class_body_statements = sort_class_body_statements(
            class_body_statements,
            sort_decorated_methods=self.sort_decorated_methods,
            sort_within_groups=self.sort_within_groups,
        )

        if sorted_class_body_statements == class_body_statements:
            return updated_node

        return updated_node.with_changes(
            body=class_body.with_changes(body=sorted_class_body_statements)
        )


def sort_python_source(
    source: str,
    *,
    sort_decorated_methods: bool = False,
    sort_within_groups: SortWithinGroups = "preserve",
) -> str:
    module = libcst.parse_module(source)

    method_sorter_transformer = MethodSorterTransformer(
        sort_decorated_methods=sort_decorated_methods,
        sort_within_groups=sort_within_groups,
    )

    updated_module = module.visit(method_sorter_transformer)
    return updated_module.code


def sort_class_body_statements(
    class_body_statements: list[libcst.BaseStatement],
    *,
    sort_decorated_methods: bool,
    sort_within_groups: SortWithinGroups,
) -> list[libcst.BaseStatement]:
    sorted_class_body_statements: list[libcst.BaseStatement] = []
    method_statement_group: list[libcst.BaseStatement] = []

    def flush_method_statement_group() -> None:
        nonlocal method_statement_group

        if not method_statement_group:
            return

        sorted_class_body_statements.extend(
            sort_method_statement_group(
                method_statement_group,
                sort_decorated_methods=sort_decorated_methods,
                sort_within_groups=sort_within_groups,
                is_first_class_body_group=not sorted_class_body_statements,
            )
        )
        method_statement_group = []

    for class_body_statement in class_body_statements:
        if is_sortable_method_statement(
            class_body_statement,
            sort_decorated_methods=sort_decorated_methods,
        ):
            method_statement_group.append(class_body_statement)
        else:
            flush_method_statement_group()
            sorted_class_body_statements.append(class_body_statement)

    flush_method_statement_group()

    return sorted_class_body_statements


def sort_method_statement_group(
    method_statements: list[libcst.BaseStatement],
    *,
    sort_decorated_methods: bool,
    sort_within_groups: SortWithinGroups,
    is_first_class_body_group: bool,
) -> list[libcst.BaseStatement]:
    method_blocks = build_method_blocks(
        method_statements,
        sort_decorated_methods=sort_decorated_methods,
    )

    sorted_method_blocks = sorted(
        method_blocks,
        key=lambda method_block: get_method_sort_key(
            method_block.method_info,
            sort_within_groups=sort_within_groups,
        ),
    )

    sorted_method_statements: list[libcst.BaseStatement] = []

    for method_block in sorted_method_blocks:
        sorted_method_statements.extend(method_block.statements)

    return normalize_method_statement_group_spacing(
        sorted_method_statements,
        is_first_class_body_group=is_first_class_body_group,
    )


def build_method_blocks(
    method_statements: list[libcst.BaseStatement],
    *,
    sort_decorated_methods: bool,
) -> list[MethodBlock]:
    method_blocks: list[MethodBlock] = []
    method_statement_index = 0

    while method_statement_index < len(method_statements):
        method_statement = method_statements[method_statement_index]
        function_definition = get_function_definition(method_statement)

        if function_definition is None:
            method_blocks.append(
                MethodBlock(
                    statements=[method_statement],
                    method_info=MethodInfo(
                        name="",
                        group="unknown",
                        original_index=method_statement_index,
                    ),
                )
            )
            method_statement_index += 1
            continue

        if is_overload_method(function_definition):
            overload_method_block = build_overload_method_block(
                method_statements,
                start_index=method_statement_index,
                function_definition=function_definition,
            )
            method_blocks.append(overload_method_block)
            method_statement_index += len(overload_method_block.statements)
            continue

        method_group = classify_method(
            function_definition,
            sort_decorated_methods=sort_decorated_methods,
        )

        method_original_index = method_statement_index

        if method_group == "property":
            method_original_index = get_property_order(function_definition)

        method_blocks.append(
            MethodBlock(
                statements=[method_statement],
                method_info=MethodInfo(
                    name=function_definition.name.value,
                    group=method_group,
                    original_index=method_original_index,
                ),
            )
        )
        method_statement_index += 1

    return method_blocks


def build_overload_method_block(
    method_statements: list[libcst.BaseStatement],
    *,
    start_index: int,
    function_definition: libcst.FunctionDef,
) -> MethodBlock:
    overload_method_name = function_definition.name.value
    overload_block_statements = [method_statements[start_index]]
    overload_block_index = start_index + 1

    while overload_block_index < len(method_statements):
        next_method_statement = method_statements[overload_block_index]
        next_function_definition = get_function_definition(next_method_statement)

        if next_function_definition is None:
            break

        if next_function_definition.name.value != overload_method_name:
            break

        overload_block_statements.append(next_method_statement)

        if not is_overload_method(next_function_definition):
            overload_block_index += 1
            break

        overload_block_index += 1

    return MethodBlock(
        statements=overload_block_statements,
        method_info=MethodInfo(
            name=overload_method_name,
            group=f"decorated_{classify_visibility(overload_method_name)}",
            original_index=start_index,
        ),
    )


def get_method_sort_key(
    method_info: MethodInfo,
    *,
    sort_within_groups: SortWithinGroups,
) -> tuple[int, str | int]:
    method_group_index = GROUP_ORDER.get(method_info.group, GROUP_ORDER["unknown"])

    if sort_within_groups == "alphabetical":
        return method_group_index, method_info.name

    return method_group_index, method_info.original_index


def normalize_method_statement_group_spacing(
    method_statements: list[libcst.BaseStatement],
    *,
    is_first_class_body_group: bool,
) -> list[libcst.BaseStatement]:
    normalized_method_statements: list[libcst.BaseStatement] = []

    for method_index, method_statement in enumerate(method_statements):
        if method_index == 0 and is_first_class_body_group:
            normalized_method_statements.append(
                set_leading_empty_lines(method_statement, [])
            )
            continue

        normalized_method_statements.append(
            set_leading_empty_lines(
                method_statement,
                [libcst.EmptyLine(indent=False)],
            )
        )

    return normalized_method_statements


def set_leading_empty_lines(
    statement: libcst.BaseStatement,
    empty_lines: Sequence[libcst.EmptyLine],
) -> libcst.BaseStatement:
    if not isinstance(statement, libcst.FunctionDef):
        return statement

    comment_lines = [
        leading_line
        for leading_line in statement.leading_lines
        if leading_line.comment is not None
    ]

    return statement.with_changes(
        leading_lines=[
            *empty_lines,
            *comment_lines,
        ],
    )


def is_sortable_method_statement(
    class_body_statement: libcst.BaseStatement,
    *,
    sort_decorated_methods: bool,
) -> bool:
    function_definition = get_function_definition(class_body_statement)

    if function_definition is None:
        return False

    if is_overload_method(function_definition):
        return True

    if is_property_method(function_definition):
        return True

    if is_abstract_method(function_definition):
        return True

    if is_dunder(function_definition.name.value):
        return True

    if has_decorators(function_definition) and not sort_decorated_methods:
        return False

    return True


def get_function_definition(
    class_body_statement: libcst.BaseStatement,
) -> libcst.FunctionDef | None:
    if isinstance(class_body_statement, libcst.FunctionDef):
        return class_body_statement

    return None


def classify_method(
    function_definition: libcst.FunctionDef,
    *,
    sort_decorated_methods: bool,
) -> str:
    method_name = function_definition.name.value

    if is_dunder(method_name):
        return "dunder"

    if is_property_method(function_definition):
        return "property"

    method_visibility = classify_visibility(method_name)

    if is_abstract_method(function_definition):
        return f"abstract_{method_visibility}"

    if has_decorators(function_definition):
        if sort_decorated_methods:
            return f"decorated_{method_visibility}"

        return "unknown"

    return method_visibility


def classify_visibility(method_name: str) -> str:
    if is_private(method_name):
        return "private"

    if is_protected(method_name):
        return "protected"

    return "public"


def is_dunder(method_name: str) -> bool:
    return (
        method_name.startswith("__")
        and method_name.endswith("__")
        and len(method_name) > 4
    )


def is_private(method_name: str) -> bool:
    return method_name.startswith("__") and not method_name.endswith("__")


def is_protected(method_name: str) -> bool:
    return method_name.startswith("_") and not method_name.startswith("__")


def has_decorators(function_definition: libcst.FunctionDef) -> bool:
    return bool(function_definition.decorators)


def is_property_method(function_definition: libcst.FunctionDef) -> bool:
    for decorator in function_definition.decorators:
        decorator_full_name = get_decorator_name(decorator.decorator)

        if decorator_full_name == "property":
            return True

        if decorator_full_name.endswith(".setter"):
            return True

        if decorator_full_name.endswith(".deleter"):
            return True

    return False


def get_property_order(function_definition: libcst.FunctionDef) -> int:
    for decorator in function_definition.decorators:
        decorator_full_name = get_decorator_name(decorator.decorator)

        if decorator_full_name == "property":
            return 0

        if decorator_full_name.endswith(".setter"):
            return 1

        if decorator_full_name.endswith(".deleter"):
            return 2

    return 999


def is_abstract_method(function_definition: libcst.FunctionDef) -> bool:
    for decorator in function_definition.decorators:
        decorator_full_name = get_decorator_name(decorator.decorator)

        if decorator_full_name == "abstractmethod":
            return True

        if decorator_full_name.endswith(".abstractmethod"):
            return True

    return False


def is_overload_method(function_definition: libcst.FunctionDef) -> bool:
    for decorator in function_definition.decorators:
        decorator_full_name = get_decorator_name(decorator.decorator)

        if decorator_full_name == "overload":
            return True

        if decorator_full_name.endswith(".overload"):
            return True

    return False


def get_decorator_name(expression: libcst.BaseExpression) -> str:
    if isinstance(expression, libcst.Name):
        return expression.value

    if isinstance(expression, libcst.Attribute):
        decorator_name_parts: list[str] = []
        current_expression: libcst.BaseExpression = expression

        while isinstance(current_expression, libcst.Attribute):
            decorator_name_parts.append(current_expression.attr.value)
            current_expression = current_expression.value

        if isinstance(current_expression, libcst.Name):
            decorator_name_parts.append(current_expression.value)

        return ".".join(reversed(decorator_name_parts))

    if isinstance(expression, libcst.Call):
        return get_decorator_name(expression.func)

    return ""


def has_method_sorter_skip_comment(class_definition: libcst.ClassDef) -> bool:
    return False
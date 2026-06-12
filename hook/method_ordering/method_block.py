from __future__ import annotations

from dataclasses import dataclass

import libcst as concrete_syntax_tree

from hook.method_analysis.method_information import MethodInformation


@dataclass(frozen=True)
class MethodBlock:
    """Store a group of method statements with their sorting metadata."""

    statements: list[concrete_syntax_tree.BaseStatement]
    method_information: MethodInformation

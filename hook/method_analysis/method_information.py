from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MethodInformation:
    """Store classification metadata for a method found in a class body."""

    name: str
    group: str
    original_index: int

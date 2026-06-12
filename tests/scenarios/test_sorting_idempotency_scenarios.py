from __future__ import annotations

import unittest

from hook.configuration.sorting_options import SortWithinGroups
from tests.test_utils import create_source_sorter


class SortingIdempotencyScenariosTest(unittest.TestCase):
    """Verify that method sorting is stable across repeated runs.

    These tests check that sorting already-sorted source leaves it unchanged and
    that applying the sorter multiple times does not keep modifying formatting,
    method order, or grouped method structures after the first pass.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def assert_sorting_is_idempotent(
        self,
        source: str,
        *,
        sort_decorated_methods: bool = False,
        sort_within_groups: SortWithinGroups = "preserve",
    ) -> None:
        once_sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=sort_decorated_methods,
            sort_within_groups=sort_within_groups,
        )
        twice_sorted_source = self.source_sorter.sort_python_source(
            once_sorted_source,
            sort_decorated_methods=sort_decorated_methods,
            sort_within_groups=sort_within_groups,
        )

        self.assertEqual(
            once_sorted_source,
            twice_sorted_source,
            msg=("Expected source sorting to be idempotent after the first pass. " "A second sort should not change the already sorted source."),
        )

    def test_idempotent_for_regular_visibility_sorting(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    def _protected(self):
        pass

    def public(self):
        pass
"""

        self.assert_sorting_is_idempotent(source)

    def test_idempotent_for_alphabetical_sorting(self) -> None:
        source = """\
class Example:
    def zebra(self):
        pass

    def alpha(self):
        pass

    def build(self):
        pass
"""

        self.assert_sorting_is_idempotent(
            source,
            sort_within_groups="alphabetical",
        )

    def test_idempotent_for_property_sorting(self) -> None:
        source = """\
class Example:
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def name(self):
        return self._name

    def public(self):
        pass
"""

        self.assert_sorting_is_idempotent(source)

    def test_idempotent_for_dunder_sorting(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    def __init__(self):
        self.value = 1
"""

        self.assert_sorting_is_idempotent(source)

    def test_idempotent_for_decorated_method_sorting(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @classmethod
    def create(class_object):
        return class_object()
"""

        self.assert_sorting_is_idempotent(
            source,
            sort_decorated_methods=True,
        )

    def test_idempotent_for_top_level_function_module(self) -> None:
        source = """\
def zebra_function():
    pass

def alpha_function():
    pass

def build_function():
    pass
"""

        self.assert_sorting_is_idempotent(
            source,
            sort_within_groups="alphabetical",
        )

    def test_idempotent_for_overload_sorting(self) -> None:
        source = """\
class Example:
    def build(self):
        pass

    @typing.overload
    def load(self, value: str) -> str:
        ...

    @typing.overload
    def load(self, value: int) -> int:
        ...

    def load(self, value):
        return value
"""

        self.assert_sorting_is_idempotent(
            source,
            sort_decorated_methods=True,
        )

    def test_idempotent_for_skip_comment(self) -> None:
        source = """\
# method-sorter: skip
class Example:
    def __private(self):
        pass

    def public(self):
        pass
"""

        self.assert_sorting_is_idempotent(source)

    def test_idempotent_for_class_structure_boundaries(self) -> None:
        source = """\
class Example:
    def __private_before(self):
        pass

    value: int = 1

    def public_after(self):
        pass
"""

        self.assert_sorting_is_idempotent(source)

from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class OverloadMethodScenariosTest(unittest.TestCase):
    """Verify sorting behavior for overload method groups.

    These tests check that consecutive overload declarations and their concrete
    implementation are treated as one method block, preserving their internal
    order while allowing the whole overload family to move according to method
    group sorting rules.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_overload_block_stays_together_and_moves_before_regular_public_method(self) -> None:
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

        expected_source = """\
class Example:
    @typing.overload
    def load(self, value: str) -> str:
        ...

    @typing.overload
    def load(self, value: int) -> int:
        ...

    def load(self, value):
        return value

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected overload declarations and implementation to stay together " "as one block and sort before regular public methods."),
        )

    def test_overload_block_preserves_internal_order(self) -> None:
        source = """\
class Example:
    @typing.overload
    def load(self, value: int) -> int:
        ...

    @typing.overload
    def load(self, value: str) -> str:
        ...

    def load(self, value):
        return value
"""

        expected_source = """\
class Example:
    @typing.overload
    def load(self, value: int) -> int:
        ...

    @typing.overload
    def load(self, value: str) -> str:
        ...

    def load(self, value):
        return value
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected overload block internal declaration order to be preserved " "even when alphabetical sorting is enabled."),
        )

    def test_protected_overload_block_stays_together(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @typing.overload
    def _load(self, value: str) -> str:
        ...

    @typing.overload
    def _load(self, value: int) -> int:
        ...

    def _load(self, value):
        return value
"""

        expected_source = """\
class Example:
    @typing.overload
    def _load(self, value: str) -> str:
        ...

    @typing.overload
    def _load(self, value: int) -> int:
        ...

    def _load(self, value):
        return value

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected protected overload block to stay together and sort as " "a decorated protected method block."),
        )

    def test_private_overload_block_stays_together(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @typing.overload
    def __load(self, value: str) -> str:
        ...

    @typing.overload
    def __load(self, value: int) -> int:
        ...

    def __load(self, value):
        return value
"""

        expected_source = """\
class Example:
    @typing.overload
    def __load(self, value: str) -> str:
        ...

    @typing.overload
    def __load(self, value: int) -> int:
        ...

    def __load(self, value):
        return value

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected private overload block to stay together and sort as " "a decorated private method block."),
        )

    def test_plain_overload_decorator_is_supported(self) -> None:
        source = """\
class Example:
    def build(self):
        pass

    @overload
    def load(self, value: str) -> str:
        ...

    @overload
    def load(self, value: int) -> int:
        ...

    def load(self, value):
        return value
"""

        expected_source = """\
class Example:
    @overload
    def load(self, value: str) -> str:
        ...

    @overload
    def load(self, value: int) -> int:
        ...

    def load(self, value):
        return value

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected plain overload decorator to be recognized and grouped " "with its implementation."),
        )

    def test_overload_declarations_without_implementation_stay_together(self) -> None:
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
"""

        expected_source = """\
class Example:
    @typing.overload
    def load(self, value: str) -> str:
        ...

    @typing.overload
    def load(self, value: int) -> int:
        ...

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected overload declarations without implementation to stay " "together as one overload block."),
        )

    def test_overload_block_does_not_merge_across_different_method_name(self) -> None:
        source = """\
class Example:
    @typing.overload
    def load(self, value: str) -> str:
        ...

    def build(self):
        pass

    @typing.overload
    def load(self, value: int) -> int:
        ...
"""

        expected_source = """\
class Example:
    @typing.overload
    def load(self, value: str) -> str:
        ...

    @typing.overload
    def load(self, value: int) -> int:
        ...

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected separated overload declarations to remain independent " "blocks but still sort before regular public methods."),
        )

    def test_top_level_overload_functions_remain_unchanged(self) -> None:
        source = """\
@typing.overload
def load(value: str) -> str:
    ...

@typing.overload
def load(value: int) -> int:
    ...

def load(value):
    return value

def build():
    pass
"""

        expected_source = """\
@typing.overload
def load(value: str) -> str:
    ...

@typing.overload
def load(value: int) -> int:
    ...

def load(value):
    return value

def build():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level overload functions to remain unchanged because " "only class-body methods are sorted."),
        )

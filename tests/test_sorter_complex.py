import unittest

from hook.sorter import sort_python_source
import tempfile

class TestComplexMethodSorting(unittest.TestCase):
    def test_keeps_module_level_functions_unchanged(self) -> None:
        source = '''\
def zeta():
    pass


def alpha():
    pass


class Example:
    def run(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
def zeta():
    pass


def alpha():
    pass


class Example:
    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_multiple_classes_independently(self) -> None:
        source = '''\
class First:
    def run(self):
        pass

    def __init__(self):
        pass


class Second:
    def _helper(self):
        pass

    def build(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class First:
    def __init__(self):
        pass

    def run(self):
        pass


class Second:
    def __init__(self):
        pass

    def build(self):
        pass

    def _helper(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_nested_class_methods_without_moving_nested_class(self) -> None:
        source = '''\
class Outer:
    def outer_run(self):
        pass

    def __init__(self):
        pass

    class Inner:
        def inner_run(self):
            pass

        def __init__(self):
            pass
'''

        expected = '''\
class Outer:
    def __init__(self):
        pass

    def outer_run(self):
        pass

    class Inner:
        def __init__(self):
            pass

        def inner_run(self):
            pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_keeps_class_attribute_boundaries(self) -> None:
        source = '''\
class Example:
    first_value = 1

    def zeta(self):
        pass

    def alpha(self):
        pass

    second_value = 2

    def _helper(self):
        pass

    def build(self):
        pass
'''

        expected = '''\
class Example:
    first_value = 1

    def zeta(self):
        pass

    def alpha(self):
        pass

    second_value = 2

    def build(self):
        pass

    def _helper(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_keeps_pass_boundary(self) -> None:
        source = '''\
class Example:
    pass

    def run(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    pass

    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_keeps_ellipsis_boundary(self) -> None:
        source = '''\
class Example:
    ...

    def run(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    ...

    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_keeps_if_boundary(self) -> None:
        source = '''\
class Example:
    if True:
        value = 1

    def run(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    if True:
        value = 1

    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_does_not_sort_decorated_classmethod_by_default(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @classmethod
    def create(cls):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def plain(self):
        pass

    @classmethod
    def create(cls):
        pass

    def __init__(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_decorated_classmethod_when_enabled(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @classmethod
    def create(cls):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    @classmethod
    def create(cls):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_decorated_methods=True),
            expected,
        )

    def test_does_not_sort_staticmethod_by_default(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @staticmethod
    def validate(value):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def plain(self):
        pass

    @staticmethod
    def validate(value):
        pass

    def __init__(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_staticmethod_when_enabled(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @staticmethod
    def validate(value):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    @staticmethod
    def validate(value):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_decorated_methods=True),
            expected,
        )

    def test_detects_called_decorator_as_decorated_method(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @decorator_factory("value")
    def decorated(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def plain(self):
        pass

    @decorator_factory("value")
    def decorated(self):
        pass

    def __init__(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_called_decorator_when_enabled(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @decorator_factory("value")
    def decorated(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    @decorator_factory("value")
    def decorated(self):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_decorated_methods=True),
            expected,
        )

    def test_detects_attribute_decorator_as_decorated_method(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @router.get("/users")
    def list_users(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def plain(self):
        pass

    @router.get("/users")
    def list_users(self):
        pass

    def __init__(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_attribute_decorator_when_enabled(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @router.get("/users")
    def list_users(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    @router.get("/users")
    def list_users(self):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_decorated_methods=True),
            expected,
        )

    def test_sorts_abc_attribute_abstractmethod(self) -> None:
        source = '''\
import abc


class Example:
    @abc.abstractmethod
    def _build(self):
        pass

    def __init__(self):
        pass

    @abc.abstractmethod
    def build(self):
        pass
'''

        expected = '''\
import abc


class Example:
    def __init__(self):
        pass

    @abc.abstractmethod
    def build(self):
        pass

    @abc.abstractmethod
    def _build(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_abstract_classmethod_as_abstract(self) -> None:
        source = '''\
from abc import abstractmethod


class Example:
    def plain(self):
        pass

    @classmethod
    @abstractmethod
    def create(cls):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
from abc import abstractmethod


class Example:
    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def create(cls):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_abstract_staticmethod_as_abstract(self) -> None:
        source = '''\
from abc import abstractmethod


class Example:
    def plain(self):
        pass

    @staticmethod
    @abstractmethod
    def validate(value):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
from abc import abstractmethod


class Example:
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def validate(value):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_property_getter_before_public_method(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
'''

        expected = '''\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_keeps_property_getter_and_setter_together(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
'''

        expected = '''\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_keeps_property_getter_setter_and_deleter_together(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    @name.deleter
    def name(self):
        del self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
'''

        expected = '''\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @name.deleter
    def name(self):
        del self._name

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_comments_on_public_method(self) -> None:
        source = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        pass

    # Validate payload.
    def validate(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        pass

    # Validate payload.
    def validate(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_multiple_comments_on_moved_method(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    # Create instance state.
    # Called by Python during construction.
    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    # Create instance state.
    # Called by Python during construction.
    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_inline_comments_inside_method_body(self) -> None:
        source = '''\
class Example:
    def run(self):
        value = 1  # Keep this inline comment.
        return value

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        value = 1  # Keep this inline comment.
        return value
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_docstring_inside_method_body(self) -> None:
        source = '''\
class Example:
    def run(self):
        """Run the example."""
        pass

    def __init__(self):
        """Create the example."""
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        """Create the example."""
        pass

    def run(self):
        """Run the example."""
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_class_docstring_boundary(self) -> None:
        source = '''\
class Example:
    """Example class."""

    def run(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    """Example class."""

    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_async_and_sync_methods_by_group(self) -> None:
        source = '''\
class Example:
    async def _fetch(self):
        pass

    def run(self):
        pass

    async def __aenter__(self):
        return self

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    async def __aenter__(self):
        return self

    def __init__(self):
        pass

    def run(self):
        pass

    async def _fetch(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_handles_multiline_function_signature(self) -> None:
        source = '''\
class Example:
    def run(
        self,
        value,
    ):
        pass

    def __init__(
        self,
        name,
    ):
        self.name = name
'''

        expected = '''\
class Example:
    def __init__(
        self,
        name,
    ):
        self.name = name

    def run(
        self,
        value,
    ):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_handles_positional_only_and_keyword_only_arguments(self) -> None:
        source = '''\
class Example:
    def run(self, value, /, *, enabled=True):
        pass

    def __init__(self, name, /, *, active=True):
        self.name = name
'''

        expected = '''\
class Example:
    def __init__(self, name, /, *, active=True):
        self.name = name

    def run(self, value, /, *, enabled=True):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_handles_return_type_annotations(self) -> None:
        source = '''\
class Example:
    def run(self) -> None:
        pass

    def __init__(self) -> None:
        pass
'''

        expected = '''\
class Example:
    def __init__(self) -> None:
        pass

    def run(self) -> None:
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_handles_type_parameters(self) -> None:
        source = '''\
class Example:
    def run[T](self, value: T) -> T:
        return value

    def __init__(self) -> None:
        pass
'''

        expected = '''\
class Example:
    def __init__(self) -> None:
        pass

    def run[T](self, value: T) -> T:
        return value
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_handles_match_statement_inside_method(self) -> None:
        source = '''\
class Example:
    def run(self, value):
        match value:
            case 1:
                return "one"
            case _:
                return "other"

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    def run(self, value):
        match value:
            case 1:
                return "one"
            case _:
                return "other"
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_overload_group(self) -> None:
        source = '''\
from typing import overload


class Example:
    def run(self):
        pass

    @overload
    def parse(self, value: str) -> str:
        ...

    @overload
    def parse(self, value: bytes) -> bytes:
        ...

    def parse(self, value):
        return value

    def __init__(self):
        pass
'''

        expected = '''\
from typing import overload


class Example:
    def __init__(self):
        pass

    @overload
    def parse(self, value: str) -> str:
        ...

    @overload
    def parse(self, value: bytes) -> bytes:
        ...

    def parse(self, value):
        return value

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_singledispatchmethod_group_by_default(self) -> None:
        source = '''\
from functools import singledispatchmethod


class Example:
    def run(self):
        pass

    @singledispatchmethod
    def handle(self, value):
        pass

    @handle.register
    def _(self, value: str):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
from functools import singledispatchmethod


class Example:
    def run(self):
        pass

    @singledispatchmethod
    def handle(self, value):
        pass

    @handle.register
    def _(self, value: str):
        pass

    def __init__(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_pytest_fixture_order_by_default(self) -> None:
        source = '''\
import pytest


class TestExample:
    def test_b(self):
        pass

    @pytest.fixture
    def resource(self):
        return object()

    def test_a(self):
        pass
'''

        expected = '''\
import pytest


class TestExample:
    def test_b(self):
        pass

    @pytest.fixture
    def resource(self):
        return object()

    def test_a(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_django_style_inner_meta_boundary(self) -> None:
        source = '''\
class Example:
    def zeta(self):
        pass

    class Meta:
        ordering = ["name"]

    def alpha(self):
        pass
'''

        expected = '''\
class Example:
    def zeta(self):
        pass

    class Meta:
        ordering = ["name"]

    def alpha(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_pydantic_config_boundary(self) -> None:
        source = '''\
class Example:
    def zeta(self):
        pass

    model_config = {"frozen": True}

    def alpha(self):
        pass
'''

        expected = '''\
class Example:
    def zeta(self):
        pass

    model_config = {"frozen": True}

    def alpha(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_dunder_relative_order_when_preserve_enabled(self) -> None:
        source = '''\
class Example:
    def __str__(self):
        return "example"

    def __init__(self):
        pass

    def __repr__(self):
        return "Example()"
'''

        expected = '''\
class Example:
    def __str__(self):
        return "example"

    def __init__(self):
        pass

    def __repr__(self):
        return "Example()"
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_dunder_alphabetically_when_enabled(self) -> None:
        source = '''\
class Example:
    def __str__(self):
        return "example"

    def __init__(self):
        pass

    def __repr__(self):
        return "Example()"
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    def __repr__(self):
        return "Example()"

    def __str__(self):
        return "example"
'''

        self.assertEqual(
            sort_python_source(source, sort_within_groups="alphabetical"),
            expected,
        )

    def test_preserves_private_relative_order_when_preserve_enabled(self) -> None:
        source = '''\
class Example:
    def __zeta(self):
        pass

    def __alpha(self):
        pass
'''

        expected = '''\
class Example:
    def __zeta(self):
        pass

    def __alpha(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_private_alphabetically_when_enabled(self) -> None:
        source = '''\
class Example:
    def __zeta(self):
        pass

    def __alpha(self):
        pass
'''

        expected = '''\
class Example:
    def __alpha(self):
        pass

    def __zeta(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_within_groups="alphabetical"),
            expected,
        )

    def test_preserves_protected_relative_order_when_preserve_enabled(self) -> None:
        source = '''\
class Example:
    def _zeta(self):
        pass

    def _alpha(self):
        pass
'''

        expected = '''\
class Example:
    def _zeta(self):
        pass

    def _alpha(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_protected_alphabetically_when_enabled(self) -> None:
        source = '''\
class Example:
    def _zeta(self):
        pass

    def _alpha(self):
        pass
'''

        expected = '''\
class Example:
    def _alpha(self):
        pass

    def _zeta(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_within_groups="alphabetical"),
            expected,
        )

    def test_idempotent_after_sorting(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    def __init__(self):
        pass

    def _helper(self):
        pass
'''

        once_sorted = sort_python_source(source)
        twice_sorted = sort_python_source(once_sorted)

        self.assertEqual(once_sorted, twice_sorted)


def test_file_with_imports_constants_and_no_classes_is_unchanged(self) -> None:
    source = '''\
import os
from pathlib import Path


VALUE = 1


def zeta() -> None:
    pass


def alpha() -> None:
    pass
'''

    expected = '''\
import os
from pathlib import Path


VALUE = 1


def zeta() -> None:
    pass


def alpha() -> None:
    pass
'''

    self.assertEqual(sort_python_source(source), expected)
    
    
def test_file_with_only_imports_is_unchanged(self) -> None:
    source = '''\
import os
import sys

from pathlib import Path
'''

    expected = '''\
import os
import sys

from pathlib import Path
'''

    self.assertEqual(sort_python_source(source), expected)

def test_empty_file_is_unchanged(self) -> None:
    source = ""

    expected = ""

    self.assertEqual(sort_python_source(source), expected)

def test_empty_file_is_unchanged(self) -> None:
    source = ""

    expected = ""

    self.assertEqual(sort_python_source(source), expected)


def test_file_with_only_comments_is_unchanged(self) -> None:
    source = '''\
# Module comment.
# Another module comment.
'''

    expected = '''\
# Module comment.
# Another module comment.
'''

    self.assertEqual(sort_python_source(source), expected)


if __name__ == "__main__":
    unittest.main()
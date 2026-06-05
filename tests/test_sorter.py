import unittest

from hook.sorter import (
    classify_visibility,
    is_dunder,
    is_private,
    is_protected,
    sort_python_source,
)


class TestMethodVisibilityClassification(unittest.TestCase):
    def test_dunder_name_is_detected(self) -> None:
        self.assertTrue(is_dunder("__init__"))
        self.assertTrue(is_dunder("__str__"))

    def test_private_name_is_detected(self) -> None:
        self.assertTrue(is_private("__build"))
        self.assertFalse(is_private("__init__"))

    def test_protected_name_is_detected(self) -> None:
        self.assertTrue(is_protected("_build"))
        self.assertFalse(is_protected("__build"))
        self.assertFalse(is_protected("build"))

    def test_visibility_is_classified(self) -> None:
        self.assertEqual(classify_visibility("build"), "public")
        self.assertEqual(classify_visibility("_build"), "protected")
        self.assertEqual(classify_visibility("__build"), "private")


class TestMethodSorting(unittest.TestCase):
    def test_sorts_basic_methods_by_group_preserving_order_inside_group(self) -> None:
        source = '''\
class Example:
    def _helper(self):
        pass

    def run(self):
        pass

    def __init__(self):
        pass

    def __private(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    def run(self):
        pass

    def _helper(self):
        pass

    def __private(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_alphabetically_inside_group_when_enabled(self) -> None:
        source = '''\
class Example:
    def zebra(self):
        pass

    def alpha(self):
        pass

    def beta(self):
        pass
'''

        expected = '''\
class Example:
    def alpha(self):
        pass

    def beta(self):
        pass

    def zebra(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_within_groups="alphabetical"),
            expected,
        )

    def test_sorts_properties_before_abstract_and_public_methods(self) -> None:
        source = '''\
from abc import abstractmethod


class Example:
    def run(self):
        pass

    @abstractmethod
    def build(self):
        pass

    @property
    def name(self):
        return "example"

    def __init__(self):
        pass
'''

        expected = '''\
from abc import abstractmethod


class Example:
    def __init__(self):
        pass

    @property
    def name(self):
        return "example"

    @abstractmethod
    def build(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_abstract_methods_by_visibility(self) -> None:
        source = '''\
from abc import abstractmethod


class Example:
    @abstractmethod
    def __private(self):
        pass

    @abstractmethod
    def _protected(self):
        pass

    @abstractmethod
    def public(self):
        pass
'''

        expected = '''\
from abc import abstractmethod


class Example:
    @abstractmethod
    def public(self):
        pass

    @abstractmethod
    def _protected(self):
        pass

    @abstractmethod
    def __private(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_does_not_sort_decorated_methods_by_default(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @custom_decorator
    def decorated(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def plain(self):
        pass

    @custom_decorator
    def decorated(self):
        pass

    def __init__(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_decorated_methods_when_enabled(self) -> None:
        source = '''\
class Example:
    def plain(self):
        pass

    @custom_decorator
    def _decorated_protected(self):
        pass

    @custom_decorator
    def decorated_public(self):
        pass

    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    def __init__(self):
        pass

    @custom_decorator
    def decorated_public(self):
        pass

    @custom_decorator
    def _decorated_protected(self):
        pass

    def plain(self):
        pass
'''

        self.assertEqual(
            sort_python_source(source, sort_decorated_methods=True),
            expected,
        )

    def test_does_not_move_methods_across_class_attributes(self) -> None:
        source = '''\
class Example:
    def zeta(self):
        pass

    def alpha(self):
        pass

    value = 1

    def _helper(self):
        pass

    def run(self):
        pass
'''

        expected = '''\
class Example:
    def zeta(self):
        pass

    def alpha(self):
        pass

    value = 1

    def run(self):
        pass

    def _helper(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_nested_class_position(self) -> None:
        source = '''\
class Example:
    def zeta(self):
        pass

    class Meta:
        pass

    def _helper(self):
        pass

    def run(self):
        pass
'''

        expected = '''\
class Example:
    def zeta(self):
        pass

    class Meta:
        pass

    def run(self):
        pass

    def _helper(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_sorts_async_methods(self) -> None:
        source = '''\
class Example:
    async def _fetch_private(self):
        pass

    async def fetch(self):
        pass

    async def __aenter__(self):
        return self
'''

        expected = '''\
class Example:
    async def __aenter__(self):
        return self

    async def fetch(self):
        pass

    async def _fetch_private(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)

    def test_preserves_comments_attached_to_methods(self) -> None:
        source = '''\
class Example:
    def run(self):
        pass

    # Create instance state.
    def __init__(self):
        pass
'''

        expected = '''\
class Example:
    # Create instance state.
    def __init__(self):
        pass

    def run(self):
        pass
'''

        self.assertEqual(sort_python_source(source), expected)


if __name__ == "__main__":
    unittest.main()
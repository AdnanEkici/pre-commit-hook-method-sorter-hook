from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class ClassBodyBoundaryScenariosTest(unittest.TestCase):
    """Verify method sorting across realistic class-body boundary scenarios.

    These tests check that nested classes, enum-like classes, exception classes,
    class attributes, and attribute-only classes remain structural boundaries,
    while sortable method groups inside each class are still ordered independently
    according to the configured sorting rules.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_nested_enum_class_with_staticmethod_is_preserved_as_boundary(self) -> None:
        source = """\
class Example:
    def __private_before(self):
        pass

    class State(Enum):
        CREATED = "created"
        RUNNING = "running"
        FINISHED = "finished"

        @staticmethod
        def values():
            return [
                State.CREATED,
                State.RUNNING,
                State.FINISHED,
            ]

    def public_after(self):
        pass
"""

        expected_source = """\
class Example:
    def __private_before(self):
        pass

    class State(Enum):
        CREATED = "created"
        RUNNING = "running"
        FINISHED = "finished"

        @staticmethod
        def values():
            return [
                State.CREATED,
                State.RUNNING,
                State.FINISHED,
            ]

    def public_after(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected nested enum class to remain a class-body boundary for " "outer methods while preserving enum attributes and staticmethod."
            ),
        )

    def test_sorts_methods_inside_nested_enum_class_when_sortable(self) -> None:
        source = """\
class Example:
    class State(Enum):
        CREATED = "created"

        def __private(self):
            pass

        def public(self):
            pass
"""

        expected_source = """\
class Example:
    class State(Enum):
        CREATED = "created"

        def public(self):
            pass

        def __private(self):
            pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods inside a nested enum-like class to be sorted while " "enum value assignments remain in place."),
        )

    def test_attribute_only_class_remains_unchanged(self) -> None:
        source = """\
class TerminalColors:
    PURPLE = "\\033[95m"
    CYAN = "\\033[96m"
    DARKCYAN = "\\033[36m"
    BLUE = "\\033[94m"
    GREEN = "\\033[92m"
    YELLOW = "\\033[93m"
    RED = "\\033[91m"
    BOLD = "\\033[1m"
    UNDERLINE = "\\033[4m"
    END = "\\033[0m"
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg="Expected attribute-only class to remain unchanged.",
        )

    def test_class_attribute_before_methods_remains_before_sorted_method_group(self) -> None:
        source = """\
class Example:
    converter = create_converter()

    def public(self):
        pass

    def __init__(self):
        self.converter = self.converter
"""

        expected_source = """\
class Example:
    converter = create_converter()

    def __init__(self):
        self.converter = self.converter

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected class attribute to remain before the method group while " "methods after the attribute are sorted."),
        )

    def test_multiple_mixed_production_classes_are_sorted_independently(self) -> None:
        source = '''\
class Dataset(torch.utils.data.Dataset):
    to_tensor = torchvision.transforms.ToTensor()

    def get_item(self, index):
        return index

    def __len__(self):
        return 0

class TerminalColors:
    PURPLE = "\\033[95m"
    END = "\\033[0m"

class Compose(BaseCompose):
    """Compose multiple augmentations."""

    def _helper(self):
        pass

    def __call__(self, *arguments, **data):
        return data
'''

        expected_source = '''\
class Dataset(torch.utils.data.Dataset):
    to_tensor = torchvision.transforms.ToTensor()

    def __len__(self):
        return 0

    def get_item(self, index):
        return index

class TerminalColors:
    PURPLE = "\\033[95m"
    END = "\\033[0m"

class Compose(BaseCompose):
    """Compose multiple augmentations."""

    def __call__(self, *arguments, **data):
        return data

    def _helper(self):
        pass
'''

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected multiple mixed production-style classes to be sorted " "independently while attribute-only classes remain unchanged."),
        )

    def test_nested_exception_classes_remain_boundaries_inside_class(self) -> None:
        source = """\
class Handler:
    def __private_before(self):
        pass

    class MissingParameterError(Exception):
        pass

    class HttpError(Exception):
        pass

    def public_after(self):
        pass
"""

        expected_source = """\
class Handler:
    def __private_before(self):
        pass

    class MissingParameterError(Exception):
        pass

    class HttpError(Exception):
        pass

    def public_after(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected nested exception classes to remain class-body boundaries " "so outer methods are not moved across them."),
        )

    def test_class_level_constant_remains_before_sorted_methods(self) -> None:
        source = """\
class DatasetManager:
    temp_dir_default = os.sep + "tmp" + os.sep + "DatumAid" + os.sep

    def public(self):
        pass

    @classmethod
    def from_yaml(class_object):
        return class_object()

    def __del__(self):
        pass

    def __private(self):
        pass
"""

        expected_source = """\
class DatasetManager:
    temp_dir_default = os.sep + "tmp" + os.sep + "DatumAid" + os.sep

    def __del__(self):
        pass

    @classmethod
    def from_yaml(class_object):
        return class_object()

    def public(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected class-level constant to remain before the method group "
                "while methods after it are sorted by dunder, decorated, public, "
                "and private groups."
            ),
        )

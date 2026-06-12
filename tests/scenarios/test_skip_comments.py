from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class SkipCommentScenariosTest(unittest.TestCase):
    """Verify that method-sorter skip comments prevent class method sorting.

    These tests check that skip comments in the module header or directly before
    a class definition leave the targeted class unchanged, while allowing other
    classes without skip comments to continue using normal method sorting rules.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_module_header_skip_comment_skips_first_class_only(self) -> None:
        source = """\
# method-sorter: skip
class First:
    def __private(self):
        pass

    def public(self):
        pass

class Second:
    def __private(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
# method-sorter: skip
class First:
    def __private(self):
        pass

    def public(self):
        pass

class Second:
    def public(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected module-header skip comment to skip only the first class " "while later classes are still sorted."),
        )

    def test_class_leading_skip_comment_skips_attached_class_only(self) -> None:
        source = """\
class First:
    def __private(self):
        pass

    def public(self):
        pass

# method-sorter: skip
class Second:
    def __private(self):
        pass

    def public(self):
        pass

class Third:
    def __private(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
class First:
    def public(self):
        pass

    def __private(self):
        pass

# method-sorter: skip
class Second:
    def __private(self):
        pass

    def public(self):
        pass

class Third:
    def public(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected class-level skip comment to skip only the class it is " "attached to."),
        )

    def test_nested_class_skip_comment_skips_nested_class_only(self) -> None:
        source = """\
class Outer:
    # method-sorter: skip
    class Inner:
        def __private(self):
            pass

        def public(self):
            pass

    def __private_outer(self):
        pass

    def public_outer(self):
        pass
"""

        expected_source = """\
class Outer:
    # method-sorter: skip
    class Inner:
        def __private(self):
            pass

        def public(self):
            pass

    def public_outer(self):
        pass

    def __private_outer(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected skip comment attached to nested class to skip only the " "nested class body while the outer class methods are still sorted."
            ),
        )

    def test_unrelated_comment_does_not_skip_class(self) -> None:
        source = """\
# method-sorter skip
class Example:
    def __private(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
# method-sorter skip
class Example:
    def public(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected only the exact '# method-sorter: skip' comment to skip " "sorting. Similar comments must not disable sorting."),
        )

    def test_skip_comment_inside_class_body_does_not_skip_following_method(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    # method-sorter: skip
    def public(self):
        pass
"""

        expected_source = """\
class Example:
    # method-sorter: skip
    def public(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected skip comment inside a class body to behave as a normal "
                "method comment, not as a method-level skip directive. The comment "
                "should move with the public method while sorting still occurs."
            ),
        )

    def test_module_header_skip_comment_after_import_does_not_skip_class(self) -> None:
        source = """\
import os

# method-sorter: skip
class Example:
    def __private(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
import os

# method-sorter: skip
class Example:
    def __private(self):
        pass

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected skip comment directly leading a class to skip that class, " "even when imports appear before it."),
        )

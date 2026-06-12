from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class RegularMethodVisibilityScenariosTest(unittest.TestCase):
    """Verify sorting behavior for regular methods by visibility convention.

    These tests check that public, protected, and private methods are classified
    into separate visibility groups and ordered according to the configured method
    group priority while preserving or sorting order within each group as requested.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_sorts_public_protected_and_private_methods_by_group_order(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    def _protected(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def public(self):
        pass

    def _protected(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected regular methods to be sorted by visibility group order: " "public methods before protected methods before private methods."
            ),
        )

    def test_preserves_public_method_order_when_preserving_group_order(self) -> None:
        source = """\
class Example:
    def zebra(self):
        pass

    def alpha(self):
        pass

    def build(self):
        pass
"""

        expected_source = """\
class Example:
    def zebra(self):
        pass

    def alpha(self):
        pass

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected public methods to keep their original order when " "sort_within_groups is preserve."),
        )

    def test_sorts_public_methods_alphabetically_when_requested(self) -> None:
        source = """\
class Example:
    def zebra(self):
        pass

    def alpha(self):
        pass

    def build(self):
        pass
"""

        expected_source = """\
class Example:
    def alpha(self):
        pass

    def build(self):
        pass

    def zebra(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected public methods to be sorted alphabetically when " "sort_within_groups is alphabetical."),
        )

    def test_preserves_protected_method_order_when_preserving_group_order(self) -> None:
        source = """\
class Example:
    def _zebra(self):
        pass

    def _alpha(self):
        pass

    def _build(self):
        pass
"""

        expected_source = """\
class Example:
    def _zebra(self):
        pass

    def _alpha(self):
        pass

    def _build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected protected methods to keep their original order when " "sort_within_groups is preserve."),
        )

    def test_sorts_protected_methods_alphabetically_when_requested(self) -> None:
        source = """\
class Example:
    def _zebra(self):
        pass

    def _alpha(self):
        pass

    def _build(self):
        pass
"""

        expected_source = """\
class Example:
    def _alpha(self):
        pass

    def _build(self):
        pass

    def _zebra(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected protected methods to be sorted alphabetically when " "sort_within_groups is alphabetical."),
        )

    def test_preserves_private_method_order_when_preserving_group_order(self) -> None:
        source = """\
class Example:
    def __zebra(self):
        pass

    def __alpha(self):
        pass

    def __build(self):
        pass
"""

        expected_source = """\
class Example:
    def __zebra(self):
        pass

    def __alpha(self):
        pass

    def __build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected private methods to keep their original order when " "sort_within_groups is preserve."),
        )

    def test_sorts_private_methods_alphabetically_when_requested(self) -> None:
        source = """\
class Example:
    def __zebra(self):
        pass

    def __alpha(self):
        pass

    def __build(self):
        pass
"""

        expected_source = """\
class Example:
    def __alpha(self):
        pass

    def __build(self):
        pass

    def __zebra(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected private methods to be sorted alphabetically when " "sort_within_groups is alphabetical."),
        )

    def test_keeps_public_methods_before_protected_methods_when_alphabetical_sorting_is_requested(self) -> None:
        source = """\
class Example:
    def _alpha(self):
        pass

    def zebra(self):
        pass

    def _zebra(self):
        pass

    def alpha(self):
        pass
"""

        expected_source = """\
class Example:
    def alpha(self):
        pass

    def zebra(self):
        pass

    def _alpha(self):
        pass

    def _zebra(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected alphabetical sorting to apply inside each visibility "
                "group without allowing protected methods to move before public "
                "methods."
            ),
        )

    def test_keeps_protected_methods_before_private_methods_when_alphabetical_sorting_is_requested(self) -> None:
        source = """\
class Example:
    def __alpha(self):
        pass

    def _zebra(self):
        pass

    def __zebra(self):
        pass

    def _alpha(self):
        pass
"""

        expected_source = """\
class Example:
    def _alpha(self):
        pass

    def _zebra(self):
        pass

    def __alpha(self):
        pass

    def __zebra(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected alphabetical sorting to apply inside each visibility "
                "group without allowing private methods to move before protected "
                "methods."
            ),
        )

    def test_preserves_method_comments_when_methods_are_sorted_by_visibility(self) -> None:
        source = """\
class Example:
    # Private method comment
    def __private(self):
        pass

    # Protected method comment
    def _protected(self):
        pass

    # Public method comment
    def public(self):
        pass
"""

        expected_source = """\
class Example:
    # Public method comment
    def public(self):
        pass

    # Protected method comment
    def _protected(self):
        pass

    # Private method comment
    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected comments attached to public, protected, and private " "methods to move with their corresponding methods during sorting."),
        )

    def test_preserves_multiple_comment_lines_when_methods_are_sorted(self) -> None:
        source = """\
class Example:
    # Private comment line one
    # Private comment line two
    def __private(self):
        pass

    # Public comment line one
    # Public comment line two
    def public(self):
        pass
"""

        expected_source = """\
class Example:
    # Public comment line one
    # Public comment line two
    def public(self):
        pass

    # Private comment line one
    # Private comment line two
    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected multiple comment lines attached to methods to move with " "their corresponding methods during sorting."),
        )

    def test_preserves_method_docstrings_when_methods_are_sorted(self) -> None:
        source = '''\
class Example:
    def __private(self):
        """Run private behavior."""
        pass

    def public(self):
        """Run public behavior."""
        pass
'''

        expected_source = '''\
class Example:
    def public(self):
        """Run public behavior."""
        pass

    def __private(self):
        """Run private behavior."""
        pass
'''

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected method docstrings to stay inside their method bodies " "when methods are sorted by visibility."),
        )

    def test_preserves_method_type_annotations_when_methods_are_sorted(self) -> None:
        source = """\
class Example:
    def __private(self, value: int) -> str:
        return str(value)

    def public(self, value: str) -> int:
        return len(value)
"""

        expected_source = """\
class Example:
    def public(self, value: str) -> int:
        return len(value)

    def __private(self, value: int) -> str:
        return str(value)
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected method parameter and return annotations to be preserved " "when methods are sorted by visibility."),
        )

    def test_preserves_inline_method_bodies_when_methods_are_sorted(self) -> None:
        source = """\
class Example:
    def __private(self): return "private"

    def _protected(self): return "protected"

    def public(self): return "public"
"""

        expected_source = """\
class Example:
    def public(self): return "public"

    def _protected(self): return "protected"

    def __private(self): return "private"
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected inline method bodies to be preserved when public, " "protected, and private methods are sorted by visibility."),
        )

    def test_does_not_sort_top_level_functions_without_class(self) -> None:
        source = """\
def __private():
    pass

def _protected():
    pass

def public():
    pass
"""

        expected_source = """\
def __private():
    pass

def _protected():
    pass

def public():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected top-level functions to remain unchanged because the " "source sorter only sorts methods inside class bodies."),
        )

    def test_sorts_class_methods_without_changing_surrounding_top_level_functions(self) -> None:
        source = """\
def module_before():
    pass

class Example:
    def __private(self):
        pass

    def public(self):
        pass

def module_after():
    pass
"""

        expected_source = """\
def module_before():
    pass

class Example:
    def public(self):
        pass

    def __private(self):
        pass

def module_after():
    pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods inside class bodies to be sorted while top-level " "functions before and after the class remain in place."),
        )

    def test_does_not_move_methods_across_public_class_attribute(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    value = create_value()

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    value = create_value()

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods not to move across public class attributes " "because class attributes are class-body sorting boundaries."),
        )

    def test_does_not_move_methods_across_protected_class_attribute(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    _value = create_value()

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    _value = create_value()

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods not to move across protected class attributes " "because class attributes are class-body sorting boundaries."),
        )

    def test_does_not_move_methods_across_private_class_attribute(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    __value = create_value()

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    __value = create_value()

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods not to move across private class attributes " "because class attributes are class-body sorting boundaries."),
        )

    def test_does_not_move_methods_across_dunder_class_attribute(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    __slots__ = ("value",)

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    __slots__ = ("value",)

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods not to move across dunder class attributes " "because class attributes are class-body sorting boundaries."),
        )

    def test_sorts_methods_inside_public_inner_class(self) -> None:
        source = """\
class Outer:
    class Inner:
        def __private(self):
            pass

        def _protected(self):
            pass

        def public(self):
            pass
"""

        expected_source = """\
class Outer:
    class Inner:
        def public(self):
            pass

        def _protected(self):
            pass

        def __private(self):
            pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods inside public inner classes to be sorted because " "nested class definitions are visited."),
        )

    def test_sorts_methods_inside_protected_inner_class(self) -> None:
        source = """\
class Outer:
    class _Inner:
        def __private(self):
            pass

        def _protected(self):
            pass

        def public(self):
            pass
"""

        expected_source = """\
class Outer:
    class _Inner:
        def public(self):
            pass

        def _protected(self):
            pass

        def __private(self):
            pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods inside protected inner classes to be sorted " "because nested class definitions are visited."),
        )

    def test_sorts_methods_inside_private_inner_class(self) -> None:
        source = """\
class Outer:
    class __Inner:
        def __private(self):
            pass

        def _protected(self):
            pass

        def public(self):
            pass
"""

        expected_source = """\
class Outer:
    class __Inner:
        def public(self):
            pass

        def _protected(self):
            pass

        def __private(self):
            pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected methods inside private inner classes to be sorted because " "nested class definitions are visited."),
        )

    def test_does_not_move_outer_methods_across_public_inner_class(self) -> None:
        source = """\
class Outer:
    def __private(self):
        pass

    class Inner:
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Outer:
    def __private(self):
        pass

    class Inner:
        pass

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected outer class methods not to move across public inner "
                "classes because nested class definitions are class-body sorting "
                "boundaries."
            ),
        )

    def test_does_not_move_outer_methods_across_protected_inner_class(self) -> None:
        source = """\
class Outer:
    def __private(self):
        pass

    class _Inner:
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Outer:
    def __private(self):
        pass

    class _Inner:
        pass

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected outer class methods not to move across protected inner "
                "classes because nested class definitions are class-body sorting "
                "boundaries."
            ),
        )

    def test_does_not_move_outer_methods_across_private_inner_class(self) -> None:
        source = """\
class Outer:
    def __private(self):
        pass

    class __Inner:
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Outer:
    def __private(self):
        pass

    class __Inner:
        pass

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected outer class methods not to move across private inner "
                "classes because nested class definitions are class-body sorting "
                "boundaries."
            ),
        )

    def test_sorts_methods_before_and_after_inner_class_independently(self) -> None:
        source = """\
class Outer:
    def __private_before(self):
        pass

    def public_before(self):
        pass

    class Inner:
        pass

    def __private_after(self):
        pass

    def public_after(self):
        pass
"""

        expected_source = """\
class Outer:
    def public_before(self):
        pass

    def __private_before(self):
        pass

    class Inner:
        pass

    def public_after(self):
        pass

    def __private_after(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected method groups before and after an inner class boundary " "to be sorted independently without crossing the inner class."),
        )

    def test_sorts_methods_before_and_after_class_attribute_independently(self) -> None:
        source = """\
class Example:
    def __private_before(self):
        pass

    def public_before(self):
        pass

    value = create_value()

    def __private_after(self):
        pass

    def public_after(self):
        pass
"""

        expected_source = """\
class Example:
    def public_before(self):
        pass

    def __private_before(self):
        pass

    value = create_value()

    def public_after(self):
        pass

    def __private_after(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected method groups before and after a class attribute boundary " "to be sorted independently without crossing the attribute."),
        )

    def test_sorts_async_public_protected_and_private_methods_by_group_order(self) -> None:
        source = """\
class Example:
    async def __private(self):
        pass

    async def _protected(self):
        pass

    async def public(self):
        pass
"""

        expected_source = """\
class Example:
    async def public(self):
        pass

    async def _protected(self):
        pass

    async def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected async public, protected, and private methods to be sorted " "by the same visibility group order as regular methods."),
        )

    def test_sorts_mixed_sync_and_async_methods_by_visibility_group(self) -> None:
        source = """\
class Example:
    async def __private_async(self):
        pass

    def _protected_sync(self):
        pass

    async def public_async(self):
        pass

    def public_sync(self):
        pass
"""

        expected_source = """\
class Example:
    async def public_async(self):
        pass

    def public_sync(self):
        pass

    def _protected_sync(self):
        pass

    async def __private_async(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected sync and async methods to be sorted by visibility group " "while preserving original order inside the public group."),
        )

    def test_sorts_mixed_sync_and_async_methods_alphabetically_inside_visibility_group(self) -> None:
        source = """\
class Example:
    async def zebra(self):
        pass

    def alpha(self):
        pass

    async def build(self):
        pass
"""

        expected_source = """\
class Example:
    def alpha(self):
        pass

    async def build(self):
        pass

    async def zebra(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected sync and async methods in the same visibility group to " "sort alphabetically by method name when requested."),
        )

    def test_decorated_public_method_creates_boundary_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    @staticmethod
    def helper():
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    @staticmethod
    def helper():
        pass

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected decorated public methods to create a sorting boundary " "when decorated method sorting is disabled."),
        )

    def test_decorated_methods_are_sorted_by_visibility_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class Example:
    @custom_decorator
    def __private(self):
        pass

    @custom_decorator
    def _protected(self):
        pass

    @custom_decorator
    def public(self):
        pass
"""

        expected_source = """\
class Example:
    @custom_decorator
    def public(self):
        pass

    @custom_decorator
    def _protected(self):
        pass

    @custom_decorator
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
                "Expected decorated public, protected, and private methods to be "
                "sorted by decorated visibility group when decorated method sorting "
                "is enabled."
            ),
        )

    def test_decorated_methods_stay_before_regular_methods_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @custom_decorator
    def decorated_public(self):
        pass

    def _protected(self):
        pass
"""

        expected_source = """\
class Example:
    @custom_decorator
    def decorated_public(self):
        pass

    def public(self):
        pass

    def _protected(self):
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
                "Expected decorated methods to be sorted before regular public, " "protected, and private methods when decorated sorting is enabled."
            ),
        )

    def test_abstract_methods_are_sorted_before_decorated_and_regular_methods(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @custom_decorator
    def decorated(self):
        pass

    @abc.abstractmethod
    def abstract(self):
        pass
"""

        expected_source = """\
class Example:
    @abc.abstractmethod
    def abstract(self):
        pass

    @custom_decorator
    def decorated(self):
        pass

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
            msg=("Expected abstract methods to be sorted before decorated and " "regular methods according to method group order."),
        )

    def test_skip_comment_prevents_sorting_regular_methods_inside_class(self) -> None:
        source = """\
# method-sorter: skip
class Example:
    def __private(self):
        pass

    def _protected(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
# method-sorter: skip
class Example:
    def __private(self):
        pass

    def _protected(self):
        pass

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected class-level skip comment to prevent sorting of public, " "protected, and private methods inside the class."),
        )

    def test_section_header_comments_move_with_following_method(self) -> None:
        source = """\
class Example:
    # --- private functions ---
    def __private(self):
        pass

    # --- public functions ---
    def public(self):
        pass
"""

        expected_source = """\
class Example:
    # --- public functions ---
    def public(self):
        pass

    # --- private functions ---
    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected section-header comments to move with the following method " "because leading comments are attached to method statements."),
        )

    def test_section_header_comments_are_preserved_when_methods_are_already_sorted(self) -> None:
        source = """\
class Example:
    # --- public functions ---
    def public(self):
        pass

    # --- protected functions ---
    def _protected(self):
        pass

    # --- private functions ---
    def __private(self):
        pass
"""

        expected_source = """\
class Example:
    # --- public functions ---
    def public(self):
        pass

    # --- protected functions ---
    def _protected(self):
        pass

    # --- private functions ---
    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected section-header comments to remain correctly placed when " "the method groups are already sorted."),
        )

    def test_framework_lifecycle_methods_preserve_original_order_by_default(self) -> None:
        source = """\
class ModelBase:
    def on_validation_epoch_start(self):
        pass

    def on_test_start(self):
        pass

    def on_train_epoch_start(self):
        pass

    def on_fit_start(self):
        pass

    def setup(self, stage):
        pass

    def configure_optimizers(self):
        pass

    def training_step(self, batch, batch_index):
        pass

    def validation_step(self, batch, batch_index):
        pass

    def test_step(self, batch, batch_index):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            source,
            sorted_source,
            msg=("Expected public framework lifecycle methods to preserve original " "order when sort_within_groups is preserve."),
        )

    def test_framework_lifecycle_methods_sort_alphabetically_when_requested(self) -> None:
        source = """\
class ModelBase:
    def on_validation_epoch_start(self):
        pass

    def on_test_start(self):
        pass

    def on_train_epoch_start(self):
        pass

    def on_fit_start(self):
        pass

    def setup(self, stage):
        pass

    def configure_optimizers(self):
        pass

    def training_step(self, batch, batch_index):
        pass

    def validation_step(self, batch, batch_index):
        pass

    def test_step(self, batch, batch_index):
        pass
"""

        expected_source = """\
class ModelBase:
    def configure_optimizers(self):
        pass

    def on_fit_start(self):
        pass

    def on_test_start(self):
        pass

    def on_train_epoch_start(self):
        pass

    def on_validation_epoch_start(self):
        pass

    def setup(self, stage):
        pass

    def test_step(self, batch, batch_index):
        pass

    def training_step(self, batch, batch_index):
        pass

    def validation_step(self, batch, batch_index):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected public framework lifecycle methods to sort alphabetically " "only when sort_within_groups is alphabetical."),
        )

    def test_compose_like_class_with_docstring_init_call_and_protected_helper_is_sorted(self) -> None:
        source = '''\
class Compose(BaseCompose):
    """Compose multiple augmentations."""

    def _helper(self):
        pass

    def __call__(self, *arguments, **data):
        return data

    def __init__(self, augmentations):
        self.augmentations = augmentations
'''

        expected_source = '''\
class Compose(BaseCompose):
    """Compose multiple augmentations."""

    def __call__(self, *arguments, **data):
        return data

    def __init__(self, augmentations):
        self.augmentations = augmentations

    def _helper(self):
        pass
'''

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected inherited Compose-like class to preserve docstring and " "sort dunder methods before protected helpers."),
        )

    def test_dataset_like_class_with_attribute_dunder_and_staticmethod_is_sorted_after_attribute(self) -> None:
        source = """\
class Dataset(torch.utils.data.Dataset):
    to_tensor = torchvision.transforms.ToTensor()

    @staticmethod
    def convert(image):
        return image

    def __len__(self):
        return 0

    def get_item(self, index):
        return index
"""

        expected_source = """\
class Dataset(torch.utils.data.Dataset):
    to_tensor = torchvision.transforms.ToTensor()

    def __len__(self):
        return 0

    @staticmethod
    def convert(image):
        return image

    def get_item(self, index):
        return index
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected dataset-like class attribute to stay first while methods " "after it are sorted by dunder, decorated, and public groups."),
        )

    def test_inherited_class_base_expression_is_preserved_when_methods_are_sorted(self) -> None:
        source = """\
class Example(torch.utils.data.Dataset):
    def public(self):
        pass

    def __len__(self):
        return 0
"""

        expected_source = """\
class Example(torch.utils.data.Dataset):
    def __len__(self):
        return 0

    def public(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected class inheritance base expression to be preserved when " "methods inside the class body are sorted."),
        )

    def test_sorts_large_private_helper_block_after_public_methods(self) -> None:
        source = """\
class DatasetManager:
    def __err(self):
        pass

    def __prepare_dataset_files(self):
        pass

    def __import_datasets_from_yaml(self):
        pass

    def __get_fun_from_exec_conf(self):
        pass

    def __add_annotation_id_to_yaml(self):
        pass

    def process(self):
        pass

    def export(self):
        pass
"""

        expected_source = """\
class DatasetManager:
    def process(self):
        pass

    def export(self):
        pass

    def __err(self):
        pass

    def __prepare_dataset_files(self):
        pass

    def __import_datasets_from_yaml(self):
        pass

    def __get_fun_from_exec_conf(self):
        pass

    def __add_annotation_id_to_yaml(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected large private helper block to move after public methods " "while preserving private helper order by default."),
        )

    def test_preserves_private_method_docstring_and_multiline_body_when_sorted(self) -> None:
        source = '''\
class DatasetManager:
    def public(self):
        pass

    def __create_labels_dataframe(self):
        """Create labels dataframe from category metadata."""
        labels = [
            {
                "name": category["name"],
                "identifier": category["id"],
            }
            for category in self.categories
        ]
        return labels
'''

        expected_source = '''\
class DatasetManager:
    def public(self):
        pass

    def __create_labels_dataframe(self):
        """Create labels dataframe from category metadata."""
        labels = [
            {
                "name": category["name"],
                "identifier": category["id"],
            }
            for category in self.categories
        ]
        return labels
'''

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=("Expected private method docstring and multiline body to be " "preserved when method visibility sorting runs."),
        )

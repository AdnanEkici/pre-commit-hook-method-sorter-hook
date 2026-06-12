from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class DecoratedMethodScenariosTest(unittest.TestCase):
    """Verify sorting behavior for decorated methods.

    These tests check that decorated methods are treated as sorting boundaries
    when decorated-method sorting is disabled, and that they participate in the
    configured method ordering when decorated-method sorting is enabled.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_staticmethod_creates_boundary_when_decorated_sorting_is_disabled(self) -> None:
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
            msg=("Expected staticmethod to create a sorting boundary when decorated " "method sorting is disabled."),
        )

    def test_classmethod_creates_boundary_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    @classmethod
    def create(class_object):
        return class_object()

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    @classmethod
    def create(class_object):
        return class_object()

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
            msg=("Expected classmethod to create a sorting boundary when decorated " "method sorting is disabled."),
        )

    def test_custom_decorator_creates_boundary_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
class Example:
    def __private(self):
        pass

    @custom_decorator
    def helper(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __private(self):
        pass

    @custom_decorator
    def helper(self):
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
            msg=("Expected custom decorated method to create a sorting boundary " "when decorated method sorting is disabled."),
        )

    def test_decorated_methods_sort_by_visibility_when_decorated_sorting_is_enabled(self) -> None:
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
            msg=("Expected decorated methods to sort by decorated visibility group: " "public before protected before private."),
        )

    def test_decorated_methods_sort_before_regular_methods_when_enabled(self) -> None:
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
            msg=("Expected decorated methods to sort before regular public, " "protected, and private methods when decorated sorting is enabled."),
        )

    def test_decorator_call_is_preserved_when_sorted(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @custom_decorator(enabled=True)
    def decorated_public(self):
        pass
"""

        expected_source = """\
class Example:
    @custom_decorator(enabled=True)
    def decorated_public(self):
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
            msg=("Expected decorator calls to be preserved when decorated methods " "are sorted."),
        )

    def test_stacked_decorators_are_preserved_when_sorted(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @first_decorator
    @second_decorator
    def decorated_public(self):
        pass
"""

        expected_source = """\
class Example:
    @first_decorator
    @second_decorator
    def decorated_public(self):
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
            msg=("Expected stacked decorators to remain attached to their method " "when decorated methods are sorted."),
        )

    def test_comment_attached_to_decorated_method_is_preserved_when_sorted(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    # Decorated method comment
    @custom_decorator
    def decorated_public(self):
        pass
"""

        expected_source = """\
class Example:
    # Decorated method comment
    @custom_decorator
    def decorated_public(self):
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
            msg=("Expected comments attached to decorated methods to move with " "the decorated method during sorting."),
        )

    def test_abstract_methods_sort_before_decorated_and_regular_methods(self) -> None:
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
            msg=("Expected abstract methods to sort before decorated and regular " "methods according to method group order."),
        )

    def test_abstract_methods_sort_by_visibility(self) -> None:
        source = """\
class Example:
    @abc.abstractmethod
    def __private(self):
        pass

    @abc.abstractmethod
    def _protected(self):
        pass

    @abc.abstractmethod
    def public(self):
        pass
"""

        expected_source = """\
class Example:
    @abc.abstractmethod
    def public(self):
        pass

    @abc.abstractmethod
    def _protected(self):
        pass

    @abc.abstractmethod
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
            msg=("Expected abstract methods to sort by abstract visibility group: " "public before protected before private."),
        )

    def test_local_decorator_method_stays_before_method_using_it_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
class Example:
    def __local_decorator(function):
        return function

    @__local_decorator
    def callback(self):
        pass

    def public(self):
        pass
"""

        expected_source = """\
class Example:
    def __local_decorator(function):
        return function

    @__local_decorator
    def callback(self):
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
            msg=("Expected a class-local decorator method to stay before the method " "using it when decorated method sorting is disabled."),
        )

    def test_local_decorator_dependency_documents_current_enabled_sorting_behavior(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    def __local_decorator(function):
        return function

    @__local_decorator
    def callback(self):
        pass
"""

        expected_source = """\
class Example:
    @__local_decorator
    def callback(self):
        pass

    def public(self):
        pass

    def __local_decorator(function):
        return function
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected_source,
            sorted_source,
            msg=(
                "Expected current sorter behavior to move decorated methods before "
                "regular methods when decorated sorting is enabled. This documents "
                "that class-local decorator dependencies may need a future safety rule."
            ),
        )

    def test_complex_decorator_call_with_attribute_argument_is_preserved_when_sorted(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @copy_doc(Parent.method)
    def feed_batch(self, batch):
        return batch
"""

        expected_source = """\
class Example:
    @copy_doc(Parent.method)
    def feed_batch(self, batch):
        return batch

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
            msg=("Expected decorator call with attribute argument to be preserved " "when the decorated method is sorted."),
        )

    def test_multiline_decorator_call_with_attribute_argument_is_preserved_when_sorted(self) -> None:
        source = """\
class Example:
    def public(self):
        pass

    @copy_doc(
        Parent.method,
    )
    def feed_batch(self, batch):
        return batch
"""

        expected_source = """\
class Example:
    @copy_doc(
        Parent.method,
    )
    def feed_batch(self, batch):
        return batch

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
            msg=("Expected multiline decorator call with attribute argument to be " "preserved when the decorated method is sorted."),
        )

    def test_staticmethod_callback_section_sorts_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class ModelBase:
    # --- callback functions ---
    @callback_decorator
    def on_train_epoch_start(self):
        pass

    # --- static functions ---
    @staticmethod
    def seed_everything(seed):
        return seed

    def public(self):
        pass
"""

        expected_source = """\
class ModelBase:
    # --- callback functions ---
    @callback_decorator
    def on_train_epoch_start(self):
        pass

    # --- static functions ---
    @staticmethod
    def seed_everything(seed):
        return seed

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
            msg=("Expected callback and staticmethod sections to remain in decorated " "public group order when already sorted."),
        )

    def test_staticmethod_callback_section_can_move_ahead_of_public_methods_when_enabled(self) -> None:
        source = """\
class ModelBase:
    def public(self):
        pass

    # --- callback functions ---
    @callback_decorator
    def on_train_epoch_start(self):
        pass

    # --- static functions ---
    @staticmethod
    def seed_everything(seed):
        return seed
"""

        expected_source = """\
class ModelBase:
    # --- callback functions ---
    @callback_decorator
    def on_train_epoch_start(self):
        pass

    # --- static functions ---
    @staticmethod
    def seed_everything(seed):
        return seed

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
            msg=(
                "Expected decorated callback and staticmethod sections to move " "ahead of regular public methods when decorated sorting is enabled."
            ),
        )

    def test_sorts_dunder_classmethod_public_and_private_methods_together_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class DatasetManager:
    def public(self):
        pass

    def __private(self):
        pass

    @classmethod
    def from_yaml(class_object):
        return class_object()

    def __del__(self):
        pass
"""

        expected_source = """\
class DatasetManager:
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
                "Expected dunder, classmethod, public, and private methods to sort "
                "together by method group order when decorated method sorting is enabled."
            ),
        )

    def test_preserves_staticmethod_with_callable_annotation_when_sorted(self) -> None:
        source = """\
class DatasetManager:
    def public(self):
        pass

    @staticmethod
    def duplicate_finder(
        values: list[str],
        comparator: Callable[[str, str], bool],
    ) -> list[str]:
        return values
"""

        expected_source = """\
class DatasetManager:
    @staticmethod
    def duplicate_finder(
        values: list[str],
        comparator: Callable[[str, str], bool],
    ) -> list[str]:
        return values

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
            msg=("Expected staticmethod with Callable annotation to preserve its " "decorator and multiline signature when sorted."),
        )

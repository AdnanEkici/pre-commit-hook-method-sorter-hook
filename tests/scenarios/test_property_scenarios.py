from __future__ import annotations

import unittest

from tests.test_utils import create_source_sorter


class PropertyScenariosTest(unittest.TestCase):
    """Verify sorting behavior for property accessor method groups.

    These tests check that property getters, setters, and deleters are recognized
    as related accessors, kept together as one property family, and ordered by
    accessor type without being split apart during method sorting.
    """

    def setUp(self) -> None:
        self.source_sorter = create_source_sorter()

    def test_keeps_property_getter_and_setter_together(self) -> None:
        source = """\
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
"""

        expected = """\
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
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected property getter and setter to stay together as one property "
                "family, with getter before setter, while the class is sorted by "
                "method group order."
            ),
        )

    def test_keeps_property_getter_setter_and_deleter_together(self) -> None:
        source = """\
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
"""

        expected = """\
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
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected property getter, setter, and deleter to stay together "
                "and to be ordered as getter, setter, deleter inside the property "
                "family."
            ),
        )

    def test_keeps_multiple_property_families_together_when_preserving_order(self) -> None:
        source = """\
class Example:
    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value
"""

        expected = """\
class Example:
    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected separate property families to remain grouped and to keep "
                "their original family order when sort_within_groups is preserve."
            ),
        )

    def test_sorts_multiple_property_families_alphabetically(self) -> None:
        source = """\
class Example:
    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value

    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value
"""

        expected = """\
class Example:
    @property
    def alpha(self):
        return self._alpha

    @alpha.setter
    def alpha(self, value):
        self._alpha = value

    @property
    def beta(self):
        return self._beta

    @beta.setter
    def beta(self, value):
        self._beta = value
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_within_groups="alphabetical",
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property families to sort alphabetically by property name " "without splitting getters and setters."),
        )

    def test_preserves_property_comment_lines(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    # Setter comment
    @name.setter
    def name(self, value):
        self._name = value

    # Getter comment
    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    # Getter comment
    @property
    def name(self):
        return self._name

    # Setter comment
    @name.setter
    def name(self, value):
        self._name = value

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected comment lines attached to property getter and setter to " "move with their corresponding accessor statements."),
        )

    def test_preserves_multiple_property_comment_lines(self) -> None:
        source = """\
class Example:
    # Setter comment line one
    # Setter comment line two
    @name.setter
    def name(self, value):
        self._name = value

    # Getter comment line one
    # Getter comment line two
    @property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    # Getter comment line one
    # Getter comment line two
    @property
    def name(self):
        return self._name

    # Setter comment line one
    # Setter comment line two
    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected multiple leading comment lines to remain attached to the " "property accessor they describe."),
        )

    def test_preserves_inline_property_bodies(self) -> None:
        source = """\
class Example:
    def run(self): pass

    @name.setter
    def name(self, value): self._name = value

    @property
    def name(self): return self._name

    def __init__(self): self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self): self._name = "example"

    @property
    def name(self): return self._name

    @name.setter
    def name(self, value): self._name = value

    def run(self): pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected inline method bodies to be preserved while sorting property " "families and regular methods."),
        )

    def test_keeps_property_family_before_public_methods(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    @property
    def name(self):
        return self._name

    def build(self):
        pass
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    def run(self):
        pass

    def build(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property methods to be sorted before public methods " "according to method group order."),
        )

    def test_keeps_property_family_after_dunder_methods(self) -> None:
        source = """\
class Example:
    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected dunder methods to be sorted before property methods " "according to method group order."),
        )

    def test_keeps_property_family_before_protected_and_private_methods(self) -> None:
        source = """\
class Example:
    def _protected(self):
        pass

    def __private(self):
        pass

    @property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    def _protected(self):
        pass

    def __private(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property methods to be sorted before protected and private " "methods according to method group order."),
        )

    def test_does_not_move_property_family_across_class_attribute(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    value = create_value()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def run(self):
        pass

    value = create_value()

    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property family to sort only inside its contiguous method " "group and not move across class attributes."),
        )

    def test_does_not_merge_property_family_across_class_attribute(self) -> None:
        source = """\
class Example:
    @property
    def name(self):
        return self._name

    value = create_value()

    @name.setter
    def name(self, value):
        self._name = value
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    value = create_value()

    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected getter and setter not to be merged when a class attribute "
                "separates them because crossing class-body statements can change "
                "runtime semantics."
            ),
        )

    def test_keeps_property_family_with_staticmethod_boundary_when_decorated_sorting_is_disabled(self) -> None:
        source = """\
class Example:
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def name(self):
        return self._name

    @staticmethod
    def helper():
        pass

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @staticmethod
    def helper():
        pass

    def __init__(self):
        self._name = "example"
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected property family to sort internally before the decorated "
                "method boundary, while the staticmethod still prevents sorting "
                "across it when decorated sorting is disabled."
            ),
        )

    def test_sorts_property_family_with_staticmethod_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class Example:
    @staticmethod
    def helper():
        pass

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @staticmethod
    def helper():
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property family and staticmethod to participate in the " "same sortable group when decorated method sorting is enabled."),
        )

    def test_keeps_property_family_with_called_property_decorator(self) -> None:
        source = """\
class Example:
    @name.setter()
    def name(self, value):
        self._name = value

    @property()
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    @property()
    def name(self):
        return self._name

    @name.setter()
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected called property decorators to be recognized and sorted " "inside the same property family."),
        )

    def test_keeps_property_family_with_qualified_property_decorator(self) -> None:
        source = """\
class Example:
    @name.setter
    def name(self, value):
        self._name = value

    @builtins.property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    @builtins.property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected qualified property decorators to be recognized as property " "getters and kept with their setter."),
        )

    def test_preserves_additional_decorators_on_property_getter(self) -> None:
        source = """\
class Example:
    @name.setter
    def name(self, value):
        self._name = value

    @custom_decorator
    @property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    @custom_decorator
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property getter with additional decorators to keep those " "decorators while being grouped with its setter."),
        )

    def test_preserves_additional_decorators_on_property_setter(self) -> None:
        source = """\
class Example:
    @custom_decorator
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    @custom_decorator
    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property setter with additional decorators to keep those " "decorators while being grouped with its getter."),
        )

    def test_keeps_single_property_getter_as_property_family(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    @property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    @property
    def name(self):
        return self._name

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected a single property getter to behave as a property family " "and be sorted according to property group order."),
        )

    def test_keeps_single_property_setter_as_property_family(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    @name.setter
    def name(self, value):
        self._name = value

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    @name.setter
    def name(self, value):
        self._name = value

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected a standalone property setter to remain a property-family "
                "block even when the getter is not present in the same sortable group."
            ),
        )

    def test_preserves_property_family_inside_nested_class(self) -> None:
        source = """\
class Outer:
    class Inner:
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
"""

        expected = """\
class Outer:
    class Inner:
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
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property families inside nested classes to be grouped " "and sorted because nested class definitions are visited."),
        )

    def test_preserves_property_type_annotations(self) -> None:
        source = """\
class Example:
    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    @property
    def name(self) -> str:
        return self._name
"""

        expected = """\
class Example:
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected property accessor type annotations to be preserved while "
                "getter and setter are reordered inside the same property family."
            ),
        )

    def test_preserves_property_method_docstrings(self) -> None:
        source = '''\
class Example:
    @name.setter
    def name(self, value):
        """Set the display name."""
        self._name = value

    @property
    def name(self):
        """Return the display name."""
        return self._name
'''

        expected = '''\
class Example:
    @property
    def name(self):
        """Return the display name."""
        return self._name

    @name.setter
    def name(self, value):
        """Set the display name."""
        self._name = value
'''

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property method docstrings to move with their accessor " "bodies when property getter and setter are reordered."),
        )

    def test_keeps_abstract_property_getter_and_setter_together(self) -> None:
        source = """\
class Example:
    @name.setter
    @abc.abstractmethod
    def name(self, value):
        pass

    @property
    @abc.abstractmethod
    def name(self):
        pass
"""

        expected = """\
class Example:
    @property
    @abc.abstractmethod
    def name(self):
        pass

    @name.setter
    @abc.abstractmethod
    def name(self, value):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected abstract property getter and setter to stay together as " "one property family while preserving abstractmethod decorators."
            ),
        )

    def test_sorts_separated_property_accessors_before_unrelated_public_method(self) -> None:
        source = """\
class Example:
    @property
    def name(self):
        return self._name

    def helper(self):
        pass

    @name.setter
    def name(self, value):
        self._name = value
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    def helper(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected separated property accessors to be sorted before unrelated "
                "public methods because regular methods do not create class-body "
                "sorting boundaries."
            ),
        )

    def test_does_not_merge_interleaved_property_families(self) -> None:
        source = """\
class Example:
    @property
    def beta(self):
        return self._beta

    @property
    def alpha(self):
        return self._alpha

    @beta.setter
    def beta(self, value):
        self._beta = value
"""

        expected = """\
class Example:
    @property
    def beta(self):
        return self._beta

    @property
    def alpha(self):
        return self._alpha

    @beta.setter
    def beta(self, value):
        self._beta = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected interleaved property families not to be merged when a " "different property name appears between getter and setter."),
        )

    def test_preserves_additional_decorators_on_property_deleter(self) -> None:
        source = """\
class Example:
    @custom_decorator
    @name.deleter
    def name(self):
        del self._name

    @property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    @property
    def name(self):
        return self._name

    @custom_decorator
    @name.deleter
    def name(self):
        del self._name
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property deleter with additional decorators to keep those " "decorators while being grouped with its getter."),
        )

    def test_preserves_property_comments_when_blank_line_exists_before_comment(self) -> None:
        source = """\
class Example:
    @name.setter
    def name(self, value):
        self._name = value


    # Getter comment
    @property
    def name(self):
        return self._name
"""

        expected = """\
class Example:
    # Getter comment
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
"""

        sorted_source = self.source_sorter.sort_python_source(source)

        self.assertEqual(
            expected,
            sorted_source,
            msg=("Expected property comments to remain attached to their accessor " "when spacing is normalized during property family sorting."),
        )

    def test_cached_property_blocks_method_sorting_when_decorated_sorting_disabled(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    @cached_property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def run(self):
        pass

    @cached_property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=False,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected cached_property to remain a decorated-method boundary "
                "when decorated method sorting is disabled, so methods are not "
                "sorted across it or treated as a property family."
            ),
        )

    def test_sorts_cached_property_as_decorated_method_when_decorated_sorting_is_enabled(self) -> None:
        source = """\
class Example:
    def run(self):
        pass

    @cached_property
    def name(self):
        return self._name

    def __init__(self):
        self._name = "example"
"""

        expected = """\
class Example:
    def __init__(self):
        self._name = "example"

    @cached_property
    def name(self):
        return self._name

    def run(self):
        pass
"""

        sorted_source = self.source_sorter.sort_python_source(
            source,
            sort_decorated_methods=True,
        )

        self.assertEqual(
            expected,
            sorted_source,
            msg=(
                "Expected cached_property to be sorted as a decorated method, not " "as a property family, when decorated method sorting is enabled."
            ),
        )

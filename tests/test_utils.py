from __future__ import annotations

from pathlib import Path

import libcst as concrete_syntax_tree

from hook.configuration.sorting_options import SortWithinGroups
from hook.method_analysis.decorator_name_resolver import DecoratorNameResolver
from hook.method_analysis.method_classifier import MethodClassifier
from hook.method_analysis.property_accessor import PropertyAccessorResolver
from hook.method_ordering.method_block_builder import MethodBlockBuilder
from hook.method_ordering.method_group_spacing_normalizer import MethodGroupSpacingNormalizer
from hook.method_ordering.method_statement_sorter import MethodStatementSorter
from hook.source_processing.class_body_sorter import ClassBodySorter
from hook.source_processing.source_sorter import SourceSorter


class SourceSorterDouble:
    """Test double that returns fixed sorted source and records received input.

    This helper is used to isolate pre-commit runner tests from the real source
    sorter, allowing tests to verify file rewriting, skipped files, and exit-code
    behavior based on controlled sorting results.
    """

    def __init__(self, sorted_source: str) -> None:
        """Initialize the double with source text to return from sorting.

        Args:
            sorted_source: Source text returned whenever sort_python_source is called.
        """
        self.sorted_source = sorted_source
        self.received_sources: list[str] = []

    def sort_python_source(self, source: str, *, sort_decorated_methods: bool = False, sort_within_groups: str = "preserve") -> str:
        """Record received source text and return the configured sorted source.

        Args:
            source: Source text passed by the pre-commit runner.
            sort_decorated_methods: Whether decorated methods should be sorted.
            sort_within_groups: Strategy for ordering methods within groups.

        Returns:
            Configured sorted source text.
        """
        self.received_sources.append(source)
        sorted_source = self.sorted_source
        return sorted_source


class FakePreCommitRunner:
    """Test double that records pre-commit runner arguments and returns a fixed exit code.

    This helper is used to isolate command-line tests from the real pre-commit
    runner, allowing tests to verify parsed file paths, sorting options, and
    returned exit-code behavior.
    """

    def __init__(self, exit_code: int) -> None:
        """Initialize the fake runner with the exit code to return.

        Args:
            exit_code: Exit code returned whenever run is called.
        """
        self.exit_code = exit_code
        self.received_file_paths: list[Path] = []
        self.received_sort_decorated_methods: bool | None = None
        self.received_sort_within_groups: str | None = None

    def run(
        self,
        file_paths: list[Path],
        *,
        sort_decorated_methods: bool = False,
        sort_within_groups: str = "preserve",
    ) -> int:
        """Record received runner arguments and return the configured exit code.

        Args:
            file_paths: File paths passed by the command-line entry point.
            sort_decorated_methods: Whether decorated methods should be sorted.
            sort_within_groups: Strategy for ordering methods within groups.

        Returns:
            Configured exit code.
        """
        self.received_file_paths = list(file_paths)
        self.received_sort_decorated_methods = sort_decorated_methods
        self.received_sort_within_groups = sort_within_groups
        return self.exit_code


class PreCommitRunnerDouble:
    """Test double that records arguments passed to the pre-commit runner."""

    def __init__(self) -> None:
        self.received_files: list = []
        self.received_sort_decorated_methods = False
        self.received_sort_within_groups = "preserve"

    def run(self, file_paths, *, sort_decorated_methods: bool = False, sort_within_groups: str = "preserve") -> int:
        """Record received runner arguments and return a fixed exit code.

        Args:
            file_paths: File paths passed by the command-line entry point.
            sort_decorated_methods: Whether decorated methods should be sorted.
            sort_within_groups: Strategy for ordering methods within groups.

        Returns:
            Fixed exit code used by the test.
        """
        self.received_files = file_paths
        self.received_sort_decorated_methods = sort_decorated_methods
        self.received_sort_within_groups = sort_within_groups
        exit_code = 7
        return exit_code


class FakeSourceSorter:
    """Test double that records source-sorting calls and returns configured results.

    This helper is used to isolate pre-commit runner tests from the real source
    sorter, allowing tests to verify which source text and sorting options were
    passed while controlling whether each file is treated as changed.
    """

    def __init__(self) -> None:
        """Initialize the fake sorter with empty call history and result mappings."""
        self.received_sources: list[str] = []
        self.received_sort_decorated_methods: list[bool] = []
        self.received_sort_within_groups: list[SortWithinGroups] = []
        self.sorted_source_by_original_source: dict[str, str] = {}

    def sort_python_source(
        self,
        source: str,
        *,
        sort_decorated_methods: bool = False,
        sort_within_groups: SortWithinGroups = "preserve",
    ) -> str:
        """Record a source-sorting call and return the configured sorted source.

        Args:
            source: Source text passed by the pre-commit runner.
            sort_decorated_methods: Whether decorated methods should be sorted.
            sort_within_groups: Strategy for ordering methods within groups.

        Returns:
            Configured sorted source for the original source, or the original source
            when no replacement is configured.
        """
        self.received_sources.append(source)
        self.received_sort_decorated_methods.append(sort_decorated_methods)
        self.received_sort_within_groups.append(sort_within_groups)

        sorted_source = self.sorted_source_by_original_source.get(source, source)
        return sorted_source


class FakePythonFileRepository:
    """Test double that stores file contents in memory and records file operations.

    This helper is used to isolate pre-commit runner tests from the real file
    system repository, allowing tests to verify which paths were read or written
    and what source text was persisted.
    """

    def __init__(self) -> None:
        """Initialize the fake repository with empty storage and operation history."""
        self.source_by_file_path: dict[Path, str] = {}
        self.written_source_by_file_path: dict[Path, str] = {}
        self.read_file_paths: list[Path] = []
        self.written_file_paths: list[Path] = []

    def read_source(self, file_path: Path) -> str:
        """Record a read operation and return stored source for the path.

        Args:
            file_path: Path whose source should be read.

        Returns:
            Stored source text for the requested path.
        """
        self.read_file_paths.append(file_path)
        source = self.source_by_file_path[file_path]
        return source

    def write_source(self, file_path: Path, source: str) -> None:
        """Record a write operation and store source for the path.

        Args:
            file_path: Path whose source should be written.
            source: Source text written to the path.
        """
        self.written_file_paths.append(file_path)
        self.written_source_by_file_path[file_path] = source


def parse_first_class(source: str) -> concrete_syntax_tree.ClassDef:
    """Parse source code and return the first class definition.

    Args:
        source: Python source code to parse.

    Raises:
        TypeError: If the first statement is not a class definition.

    Returns:
        First class definition from the parsed source.
    """
    module = concrete_syntax_tree.parse_module(source)
    class_definition = module.body[0]

    if not isinstance(class_definition, concrete_syntax_tree.ClassDef):
        raise TypeError("Expected first statement to be a class definition")

    parsed_class_definition = class_definition
    return parsed_class_definition


def parse_first_function(source: str) -> concrete_syntax_tree.FunctionDef:
    """Parse source code and return the first function definition.

    Args:
        source: Python source code to parse.

    Raises:
        TypeError: If the first statement is not a function definition.

    Returns:
        First function definition from the parsed source.
    """
    module = concrete_syntax_tree.parse_module(source)
    function_definition = module.body[0]

    if not isinstance(function_definition, concrete_syntax_tree.FunctionDef):
        raise TypeError("Expected first statement to be a function definition")

    parsed_function_definition = function_definition
    return parsed_function_definition


def create_decorator_name_resolver() -> DecoratorNameResolver:
    """Create a decorator name resolver for tests.

    Returns:
        Decorator name resolver instance.
    """
    decorator_name_resolver = DecoratorNameResolver()
    return decorator_name_resolver


def create_method_classifier() -> MethodClassifier:
    """Create a method classifier with its test dependencies.

    Returns:
        Method classifier instance.
    """
    decorator_name_resolver = create_decorator_name_resolver()
    method_classifier = MethodClassifier(decorator_name_resolver)
    return method_classifier


def create_property_accessor_resolver() -> PropertyAccessorResolver:
    """Create a property accessor resolver with its test dependencies.

    Returns:
        Property accessor resolver instance.
    """
    decorator_name_resolver = create_decorator_name_resolver()
    property_accessor_resolver = PropertyAccessorResolver(decorator_name_resolver)
    return property_accessor_resolver


def create_method_block_builder() -> MethodBlockBuilder:
    """Create a method block builder with its test dependencies.

    Returns:
        Method block builder instance.
    """
    method_classifier = create_method_classifier()
    property_accessor_resolver = create_property_accessor_resolver()
    method_block_builder = MethodBlockBuilder(
        method_classifier,
        property_accessor_resolver,
    )
    return method_block_builder


def create_source_sorter() -> SourceSorter:
    """Create a source sorter with its test dependencies.

    Returns:
        Source sorter instance.
    """
    method_classifier = create_method_classifier()
    method_block_builder = create_method_block_builder()
    method_group_spacing_normalizer = MethodGroupSpacingNormalizer()
    method_statement_sorter = MethodStatementSorter(
        method_block_builder,
        method_group_spacing_normalizer,
    )
    class_body_sorter = ClassBodySorter(
        method_classifier,
        method_statement_sorter,
    )
    source_sorter = SourceSorter(class_body_sorter)
    return source_sorter

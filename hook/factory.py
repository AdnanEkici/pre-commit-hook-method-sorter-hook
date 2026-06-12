from __future__ import annotations

from hook.file_processing.pre_commit_runner import PreCommitRunner
from hook.file_processing.python_file_repository import PythonFileRepository
from hook.method_analysis.decorator_name_resolver import DecoratorNameResolver
from hook.method_analysis.method_classifier import MethodClassifier
from hook.method_analysis.property_accessor import PropertyAccessorResolver
from hook.method_ordering.method_block_builder import MethodBlockBuilder
from hook.method_ordering.method_group_spacing_normalizer import MethodGroupSpacingNormalizer
from hook.method_ordering.method_statement_sorter import MethodStatementSorter
from hook.source_processing.class_body_sorter import ClassBodySorter
from hook.source_processing.source_sorter import SourceSorter


def create_pre_commit_runner() -> PreCommitRunner:
    """Create a pre-commit runner with its required dependencies.

    Returns:
        Configured pre-commit runner instance.
    """
    decorator_name_resolver = DecoratorNameResolver()
    method_classifier = MethodClassifier(decorator_name_resolver)
    property_accessor_resolver = PropertyAccessorResolver(decorator_name_resolver)

    method_block_builder = MethodBlockBuilder(
        method_classifier,
        property_accessor_resolver,
    )
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
    python_file_repository = PythonFileRepository()

    pre_commit_runner = PreCommitRunner(
        source_sorter,
        python_file_repository,
    )
    return pre_commit_runner

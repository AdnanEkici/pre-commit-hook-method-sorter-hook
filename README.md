# method-sorter-hook

`method-sorter-hook` is a customizable Python pre-commit hook for enforcing a consistent method order inside Python classes.

It automatically reorders class methods into predictable groups such as:

* dunder methods
* properties
* abstract methods
* decorated methods
* public methods
* protected methods
* private methods

The goal is to make class structure easier to scan, easier to review, and more consistent across a codebase.


## Table of Contents

* [What is method-sorter-hook?](#what-is-method-sorter-hook)
* [Why is it important?](#why-is-it-important)
* [What can it do?](#what-can-it-do)
* [Default method order](#default-method-order)
* [Installation](#installation)
* [Usage with pre-commit](#usage-with-pre-commit)
* [Usage from the command line](#usage-from-the-command-line)
* [Options](#options)
* [Examples](#examples)
* [Skip sorting for a class](#skip-sorting-for-a-class)
* [How it works](#how-it-works)
* [Exit codes](#exit-codes)
* [Requirements](#requirements)
* [Recommended workflow](#recommended-workflow)
* [Limitations](#limitations)
* [Development](#development)
* [License](#license)


## What is method-sorter-hook?

`method-sorter-hook` is a Python code-organization tool designed to run as a [pre-commit](https://pre-commit.com/) hook.

It parses Python source code and sorts methods inside class bodies according to a defined method-group order.

Instead of manually deciding where each method should go, this hook applies a consistent structure automatically before code is committed.

For example, a class like this:

```python
class UserService:
    def _validate_user(self):
        pass

    def create_user(self):
        pass

    def __init__(self):
        pass

    @property
    def user_count(self):
        return 0
```

can be reordered into a more consistent structure:

```python
class UserService:
    def __init__(self):
        pass

    @property
    def user_count(self):
        return 0

    def create_user(self):
        pass

    def _validate_user(self):
        pass
```

This makes classes easier to read because related method types appear in a predictable order.


## Why is it important?

Large Python classes can become difficult to navigate when methods are added over time without a consistent order.

Different developers may place methods according to personal preference:

* constructors at the top
* public methods first
* private helpers near the methods that use them
* properties near dunder methods
* abstract methods before concrete methods
* decorated methods in custom sections

Without a rule, class layout becomes inconsistent.

`method-sorter-hook` helps solve that by making method order automatic.

### Benefits

#### 1. More consistent class structure

Every class follows the same method-ordering style.

This reduces style drift across the repository.

#### 2. Easier code review

Reviewers do not need to comment on method placement manually.

The hook handles ordering before code reaches review.

#### 3. Lower cognitive load

Developers can quickly find the type of method they are looking for.

For example:

* constructor and dunder behavior near the top
* properties near the top
* public API methods before internal helpers
* private implementation details near the bottom

#### 4. Cleaner diffs over time

Automated ordering prevents random method movement caused by subjective organization choices.

#### 5. Better team conventions

Teams can standardize class layout without relying on documentation alone.

The convention becomes executable.


## What can it do?

`method-sorter-hook` can:

* sort Python class methods by method group
* preserve or alphabetically sort methods inside each group
* detect dunder methods
* detect property methods
* detect property setters
* detect property deleters
* detect abstract methods
* detect overload methods
* optionally include decorated methods in sorting
* preserve unsupported or unknown statements
* skip non-Python files
* rewrite files automatically when ordering changes
* return a non-zero exit code when files are modified
* integrate directly with `pre-commit`


## Default method order

The hook uses the following group order:

| Order | Group                       | Example                              |
| ----: | --------------------------- | ------------------------------------ |
|     1 | Dunder methods              | `__init__`, `__str__`, `__repr__`    |
|     2 | Properties                  | `@property`, `.setter`, `.deleter`   |
|     3 | Abstract public methods     | `@abstractmethod def run(...)`       |
|     4 | Abstract protected methods  | `@abstractmethod def _run(...)`      |
|     5 | Abstract private methods    | `@abstractmethod def __run(...)`     |
|     6 | Decorated public methods    | `@decorator def run(...)`            |
|     7 | Decorated protected methods | `@decorator def _run(...)`           |
|     8 | Decorated private methods   | `@decorator def __run(...)`          |
|     9 | Public methods              | `def run(...)`                       |
|    10 | Protected methods           | `def _run(...)`                      |
|    11 | Private methods             | `def __run(...)`                     |
|  Last | Unknown statements          | statements that cannot be classified |


## Installation

### Install from GitHub

```bash
pip install git+https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook.git
```

### Install for local development

```bash
git clone https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook.git
cd pre-commit-hook-method-sorter-hook
pip install -e .
```


## Usage with pre-commit

Add the hook to your `.pre-commit-config.yaml`.

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
```

Then install pre-commit hooks:

```bash
pre-commit install
```

Run against all files:

```bash
pre-commit run method-sorter-hook --all-files
```

Run during commit:

```bash
git add .
git commit -m "Apply method ordering"
```

If the hook changes files, the commit will stop. Review and stage the changes, then commit again:

```bash
git status
git diff
git add .
git commit -m "Apply method ordering"
```


## Usage from the command line

You can also run the hook directly.

```bash
method-sorter-hook path/to/file.py
```

Run it on multiple files:

```bash
method-sorter-hook app/models.py app/services.py app/controllers.py
```

Run it on all Python files:

```bash
find . -name "*.py" -print0 | xargs -0 method-sorter-hook
```


## Coverage Report

The project uses Python's built-in `unittest` framework together with `coverage`.

Run coverage with:

```
coverage run -m unittest discover -s tests
coverage report -m
```

Current coverage output:

```
Name                                                    Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------------------
hook/__init__.py                                           3      0   100%
hook/command_line.py                                      15      0   100%
hook/configuration/__init__.py                             0      0   100%
hook/configuration/sorting_options.py                      3      0   100%
hook/factory.py                                           23      0   100%
hook/file_processing/__init__.py                           0      0   100%
hook/file_processing/pre_commit_runner.py                 25      0   100%
hook/file_processing/python_file_repository.py             8      0   100%
hook/method_analysis/__init__.py                           0      0   100%
hook/method_analysis/decorator_name_resolver.py           22      0   100%
hook/method_analysis/method_classifier.py                113      6    95%   83, 153-154
hook/method_analysis/method_information.py                 7      0   100%
hook/method_analysis/property_accessor.py                 29      0   100%
hook/method_ordering/__init__.py                           0      0   100%
hook/method_ordering/group_order.py                        2      0   100%
hook/method_ordering/method_block.py                       8      0   100%
hook/method_ordering/method_block_builder.py              85     10    88%   36-42, 80-88
hook/method_ordering/method_group_spacing_normalizer.py   19      1    94%   39
hook/method_ordering/method_statement_sorter.py           29      0   100%
hook/source_processing/__init__.py                         0      0   100%
hook/source_processing/class_body_sorter.py               26      0   100%
hook/source_processing/method_sorter_transformer.py       48      0   100%
hook/source_processing/source_sorter.py                   14      0   100%
tests/__init__.py                                          0      0   100%
tests/integration/__init__.py                              0      0   100%
tests/integration/test_command_line.py                    24      0   100%
tests/integration/test_method_sorter_transformer.py       32      0   100%
tests/integration/test_pre_commit_runner.py               42      0   100%
tests/integration/test_source_sorter.py                   74      0   100%
tests/scenarios/__init__.py                                0      0   100%
tests/scenarios/test_class_body_boundaries.py             42      1    98%   320
tests/scenarios/test_class_structure_scenarios.py         96      1    99%   683
tests/scenarios/test_cli_factory_scenarios.py             56      1    98%   147
tests/scenarios/test_decorated_method.py                  98      1    99%   758
tests/scenarios/test_dunder_method_scenarios.py          122      1    99%   812
tests/scenarios/test_functions_scenarios.py              166      1    99%   1246
tests/scenarios/test_method_visibility_scenarios.py      232      1    99%   1812
tests/scenarios/test_overload_scenarios.py                32      1    97%   388
tests/scenarios/test_pre_commit_runner_scenarios.py       88      1    99%   192
tests/scenarios/test_property_scenarios.py               163      5    97%   1192-1223
tests/scenarios/test_skip_comments.py                     38      1    97%   267
tests/scenarios/test_sorting_idempotency_scenarios.py     38      1    97%   186
tests/test_utils.py                                       48      2    96%   20, 31
tests/unit/__init__.py                                     0      0   100%
tests/unit/test_class_body_sorter.py                      27      0   100%
tests/unit/test_decorator_name_resolver.py                23      0   100%
tests/unit/test_method_block.py                           18      0   100%
tests/unit/test_method_block_builder.py                   45      0   100%
tests/unit/test_method_classifier.py                      48      0   100%
tests/unit/test_method_group_spacing_normalizer.py        23      0   100%
tests/unit/test_method_information.py                     13      0   100%
tests/unit/test_method_statement_sorter.py                29      0   100%
tests/unit/test_python_file_repository.py                 19      0   100%
```

### Coverage Summary

The project currently has very strong test coverage.

Most production modules are fully covered, including command-line handling, configuration, file processing, source processing, method ordering, decorator resolution, property accessor detection, and method statement sorting.

The remaining uncovered production lines are limited to a few edge cases in:

* `hook/method_analysis/method_classifier.py`
* `hook/method_ordering/method_block_builder.py`
* `hook/method_ordering/method_group_spacing_normalizer.py`

The lowest production coverage is currently in:

```
hook/method_ordering/method_block_builder.py
```

This file is the best next target for additional tests.

### What This Coverage Means

The coverage report shows that the hook is well protected by tests across multiple layers:

* unit tests
* integration tests
* scenario tests
* command-line tests
* pre-commit runner tests
* source transformation tests

This is important because `method-sorter-hook` automatically modifies Python source files. Strong test coverage helps reduce the risk of incorrect method ordering, broken formatting, invalid syntax, or unexpected file changes.

### Recommended Next Coverage Improvements

To improve the remaining coverage, focus on the production files first.

Recommended next targets:

1. Add tests for the uncovered branches in `method_classifier.py`
2. Add edge-case tests for `method_block_builder.py`
3. Add a direct test for the missing branch in `method_group_spacing_normalizer.py`
4. Review uncovered scenario-test lines after production coverage is improved
5. Review `tests/test_utils.py` only if the uncovered helper lines contain meaningful logic

### Coverage Commands

Run all tests with coverage:

```
coverage run -m unittest discover -s tests
```

Print the coverage report:

```
coverage report -m
```

Generate an HTML report:

```
coverage html
```

Open the HTML report:

```
htmlcov/index.html
```

One-line command:

```
coverage run -m unittest discover -s tests && coverage report -m
```


## Options

### `--sort-decorated-methods`

By default, decorated methods are handled conservatively.

Use this option to include decorated methods in the sorting process.

```bash
method-sorter-hook --sort-decorated-methods path/to/file.py
```

Example pre-commit configuration:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
        args:
          - --sort-decorated-methods
```

Use this when your project wants decorated methods to be grouped with other method types.

For example:

```python
class ReportService:
    @cached_property
    def report(self):
        pass

    @transactional
    def generate(self):
        pass

    def validate(self):
        pass
```

With decorated method sorting enabled, decorated methods can be moved according to the hook's decorated-method groups.


### `--sort-within-groups`

Controls how methods are ordered inside the same group.

Supported values:

* `preserve`
* `alphabetical`

Default:

```bash
--sort-within-groups preserve
```


### `--sort-within-groups preserve`

Keeps the original relative order of methods inside the same group.

```bash
method-sorter-hook --sort-within-groups preserve path/to/file.py
```

Example:

```python
class UserService:
    def create_user(self):
        pass

    def delete_user(self):
        pass

    def update_user(self):
        pass
```

The public methods stay in the same relative order because they are already in the same group.

Use this mode when you want the hook to organize groups but not rearrange methods inside each group.


### `--sort-within-groups alphabetical`

Sorts methods alphabetically inside each method group.

```bash
method-sorter-hook --sort-within-groups alphabetical path/to/file.py
```

Example before:

```python
class UserService:
    def update_user(self):
        pass

    def create_user(self):
        pass

    def delete_user(self):
        pass
```

Example after:

```python
class UserService:
    def create_user(self):
        pass

    def delete_user(self):
        pass

    def update_user(self):
        pass
```

Use this mode when your team wants fully deterministic method order.

Example pre-commit configuration:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
        args:
          - --sort-within-groups
          - alphabetical
```


## Examples

### Example 1: Basic sorting

Before:

```python
class PaymentProcessor:
    def _validate_payment(self):
        pass

    def process(self):
        pass

    def __init__(self, gateway):
        self.gateway = gateway

    @property
    def provider(self):
        return self.gateway.provider
```

After:

```python
class PaymentProcessor:
    def __init__(self, gateway):
        self.gateway = gateway

    @property
    def provider(self):
        return self.gateway.provider

    def process(self):
        pass

    def _validate_payment(self):
        pass
```


### Example 2: Dunder methods

Before:

```python
class Product:
    def calculate_price(self):
        pass

    def __repr__(self):
        return "Product()"

    def __init__(self, name):
        self.name = name
```

After:

```python
class Product:
    def __repr__(self):
        return "Product()"

    def __init__(self, name):
        self.name = name

    def calculate_price(self):
        pass
```

Dunder methods are grouped before normal public methods.


### Example 3: Properties

Before:

```python
class Account:
    def close(self):
        pass

    @balance.setter
    def balance(self, value):
        self._balance = value

    @property
    def balance(self):
        return self._balance
```

After:

```python
class Account:
    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        self._balance = value

    def close(self):
        pass
```

Property getters, setters, and deleters are handled as property blocks.


### Example 4: Public, protected, and private methods

Before:

```python
class ImportJob:
    def __parse_row(self):
        pass

    def _prepare_file(self):
        pass

    def run(self):
        pass
```

After:

```python
class ImportJob:
    def run(self):
        pass

    def _prepare_file(self):
        pass

    def __parse_row(self):
        pass
```

The visibility order is:

1. public
2. protected
3. private


### Example 5: Abstract methods

Before:

```python
from abc import ABC, abstractmethod

class BaseExporter(ABC):
    def helper(self):
        pass

    @abstractmethod
    def export(self):
        pass
```

After:

```python
from abc import ABC, abstractmethod

class BaseExporter(ABC):
    @abstractmethod
    def export(self):
        pass

    def helper(self):
        pass
```

Abstract methods are placed before concrete public methods.


### Example 6: Sorting within groups alphabetically

Before:

```python
class NotificationService:
    def send_sms(self):
        pass

    def send_email(self):
        pass

    def send_push(self):
        pass
```

Run:

```bash
method-sorter-hook --sort-within-groups alphabetical notification_service.py
```

After:

```python
class NotificationService:
    def send_email(self):
        pass

    def send_push(self):
        pass

    def send_sms(self):
        pass
```


## Skip sorting for a class

You can skip sorting by placing this comment before a class:

```python
# method-sorter: skip
class LegacyService:
    def _helper(self):
        pass

    def run(self):
        pass

    def __init__(self):
        pass
```

The hook will leave that class unchanged.

This is useful for:

* legacy code
* generated code
* classes with intentionally custom method order
* temporary migration periods


## How it works

`method-sorter-hook` uses `libcst` to parse Python source code into a concrete syntax tree.

Unlike simple text-based sorting, this allows the hook to work with Python syntax while preserving source formatting more safely.

At a high level, the process is:

1. Read Python files passed by pre-commit.
2. Parse the source code.
3. Visit class definitions.
4. Inspect each class body.
5. Classify methods into groups.
6. Sort method groups according to the configured order.
7. Optionally sort methods alphabetically within each group.
8. Write the updated source back to the file.
9. Return an exit code indicating whether files were changed.


## Exit codes

The hook uses standard pre-commit behavior.

| Exit code | Meaning                         |
| --------: | ------------------------------- |
|       `0` | No files were changed           |
|       `1` | One or more files were modified |

When files are modified, pre-commit stops the commit.

This is expected.

Review the changes, stage them, and commit again.


## Requirements

* Python `>=3.11`
* `libcst >= 1.0.0`
* `pre-commit`, when used as a pre-commit hook

Install pre-commit:

```bash
pip install pre-commit
```


## Recommended workflow

### 1. Add the hook

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
```

### 2. Install pre-commit

```bash
pre-commit install
```

### 3. Run once on the full project

```bash
pre-commit run method-sorter-hook --all-files
```

### 4. Review the generated diff

```bash
git diff
```

### 5. Commit the formatting baseline

```bash
git add .
git commit -m "Apply method sorter baseline"
```

After this, future commits will only touch changed files.


## Recommended configuration

For conservative usage:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
```

For deterministic ordering inside method groups:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
        args:
          - --sort-within-groups
          - alphabetical
```

For projects that want decorated methods sorted too:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
        args:
          - --sort-decorated-methods
```

For both decorated-method sorting and alphabetical sorting:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook
        args:
          - --sort-decorated-methods
          - --sort-within-groups
          - alphabetical
```


## Method classification rules

### Dunder methods

A method is treated as a dunder method when it starts and ends with double underscores.

Examples:

```python
def __init__(self):
    pass

def __repr__(self):
    pass

def __str__(self):
    pass
```


### Public methods

A method is public when it does not start with an underscore.

Example:

```python
def create_user(self):
    pass
```


### Protected methods

A method is protected when it starts with a single underscore.

Example:

```python
def _validate_user(self):
    pass
```


### Private methods

A method is private when it starts with double underscores but is not a dunder method.

Example:

```python
def __build_payload(self):
    pass
```


### Property methods

Property methods include:

```python
@property
def name(self):
    return self._name
```

```python
@name.setter
def name(self, value):
    self._name = value
```

```python
@name.deleter
def name(self):
    del self._name
```

The hook keeps related property accessors together and orders them as:

1. getter
2. setter
3. deleter


### Abstract methods

Abstract methods include decorators such as:

```python
@abstractmethod
def run(self):
    pass
```

or:

```python
@abc.abstractmethod
def run(self):
    pass
```


### Overload methods

Overload methods are grouped together.

Example:

```python
@overload
def get(self, value: int) -> int:
    ...

@overload
def get(self, value: str) -> str:
    ...

def get(self, value):
    return value
```


## Limitations

`method-sorter-hook` focuses on sorting methods inside Python classes.

It does not aim to replace:

* `black`
* `ruff`
* `isort`
* `flake8`
* `pylint`
* type checkers such as `mypy` or `pyright`

Use it together with those tools.

Recommended stack:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: main
    hooks:
      - id: method-sorter-hook

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.0.0
    hooks:
      - id: ruff
      - id: ruff-format
```

Replace `v0.0.0` with the version you use in your project.


## When should you use it?

Use `method-sorter-hook` when:

* your project has many Python classes
* class method order matters to your team
* code reviews often include method-placement comments
* you want deterministic class layout
* you want public APIs above private implementation details
* you want properties and dunder methods in predictable locations
* you want pre-commit to enforce structure automatically


## When should you avoid it?

Avoid or delay using it when:

* the project has no agreed method-ordering convention
* class layout is intentionally domain-specific
* the codebase has many generated files
* large one-time diffs would disrupt active development
* your team prefers manual organization

For gradual adoption, use `# method-sorter: skip` on classes that should not be changed yet.


## Development

Clone the repository:

```bash
git clone https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook.git
cd pre-commit-hook-method-sorter-hook
```

Install in editable mode:

```bash
pip install -e .
```

Install development dependencies if needed:

```bash
pip install -r requirments.txt
```

Run the hook locally:

```bash
method-sorter-hook path/to/file.py
```

Run pre-commit locally:

```bash
pre-commit run --all-files
```


## Project structure

```text
pre-commit-hook-method-sorter-hook/
├── hook/
│   ├── command_line.py
│   ├── factory.py
│   ├── configuration/
│   ├── file_processing/
│   ├── method_analysis/
│   ├── method_ordering/
│   └── source_processing/
├── tests/
├── .pre-commit-hooks.yaml
├── .pre-commit-config.yaml
├── pyproject.toml
├── README.md
└── LICENSE
```


## Troubleshooting

### The hook changed files and my commit failed

This is normal.

Run:

```bash
git diff
git add .
git commit -m "Your commit message"
```


### The hook is not running

Check that pre-commit is installed:

```bash
pre-commit --version
```

Then install the hook:

```bash
pre-commit install
```


### The hook does not touch a file

The hook only processes Python files.

Make sure the file ends with:

```text
.py
```


### I want decorated methods to be sorted

Enable:

```yaml
args:
  - --sort-decorated-methods
```


### I want deterministic sorting inside groups

Enable:

```yaml
args:
  - --sort-within-groups
  - alphabetical
```


## FAQ

### Does this format code like Black?

No.

It sorts class methods. It is not a general-purpose formatter.

Use it with Black, Ruff Format, or another formatter.


### Does this sort imports?

No.

Use `isort` or Ruff for import sorting.


### Does this modify non-Python files?

No.

The hook skips files that do not have a `.py` suffix.


### Can I skip a class?

Yes.

Add this comment directly before the class:

```python
# method-sorter: skip
class MyClass:
    ...
```


### Does it preserve code structure?

The hook uses `libcst`, which is designed to parse and emit concrete Python syntax while preserving code structure.


### Should I pin `rev`?

Yes.

For production usage, pin `rev` to a release tag or commit SHA.

Example:

```yaml
repos:
  - repo: https://github.com/AdnanEkici/pre-commit-hook-method-sorter-hook
    rev: <commit-sha-or-release-tag>
    hooks:
      - id: method-sorter-hook
```

Using `main` is convenient for testing, but a pinned revision is safer for stable projects.


## License

This project is licensed under the MIT License.

See [LICENSE](LICENSE) for details.

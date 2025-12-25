# Contributing Guide - typed-pytest

## 1. Development Environment Setup

### 1.1 Requirements

- Python 3.13+
- uv package manager

### 1.2 Initial Setup

```bash
# Clone repository
git clone https://github.com/tmdgusya/typed-pytest.git
cd typed-pytest

# Install dependencies
uv sync --all-extras

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### 1.3 Development Dependencies

```bash
# Install all development tools
uv sync --extra dev
```

---

## 2. Code Style Conventions

### 2.1 Python Style Guide

**Base Principles**: PEP 8 + Google Python Style Guide

#### Formatting

```bash
# Auto-format with ruff
uv run ruff format src/ tests/

# Lint check with ruff
uv run ruff check src/ tests/
```

#### Naming Conventions

| Item | Rule | Example |
|------|------|---------|
| Class | PascalCase | `TypedMock`, `MockedMethod` |
| Function/Method | snake_case | `typed_mock()`, `assert_called_once()` |
| Constant | UPPER_SNAKE_CASE | `DEFAULT_TIMEOUT` |
| Private | Underscore prefix | `_internal_method()`, `_cache` |
| TypeVar | Single letter or descriptive | `T`, `T_co`, `ReturnType` |
| Protocol | Adjective/Verb+able | `Callable`, `MockProtocol` |

#### Import Order

```python
# 1. Standard library
from typing import TYPE_CHECKING, Generic, TypeVar
from unittest.mock import MagicMock

# 2. Third-party
import pytest
from pytest_mock import MockerFixture

# 3. Local
from typed_pytest._mock import TypedMock
from typed_pytest._protocols import MockProtocol

if TYPE_CHECKING:
    # Type checking only imports
    from typing import ParamSpec
```

### 2.2 Type Hint Conventions

#### Required Type Hints

All public APIs **must** include type hints:

```python
# Good
def typed_mock(cls: type[T], /, **kwargs: Any) -> TypedMock[T]:
    """Creates a type-safe mock object."""
    ...

# Bad - missing type hints
def typed_mock(cls, **kwargs):
    ...
```

#### Generic Type Notation

```python
# Python 3.12+ new syntax recommended
class TypedMock[T](MagicMock):
    ...

# Or traditional style (when backward compatibility needed)
T = TypeVar('T')

class TypedMock(MagicMock, Generic[T]):
    ...
```

#### Union Types

```python
# Python 3.10+ syntax
def process(value: str | int | None) -> str:
    ...

# Use | operator (instead of Union)
from collections.abc import Callable
callback: Callable[[int], str] | None = None
```

### 2.3 Docstring Conventions

Use **Google Style Docstring**:

```python
def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    **kwargs: Any,
) -> TypedMock[T]:
    """Creates a type-safe mock object.

    Returns a TypedMock instance that provides Mock functionality
    while preserving the original class's type information.

    Args:
        cls: The original class to mock.
        spec_set: If True, raises AttributeError when accessing attributes not in spec.
        **kwargs: Additional arguments to pass to MagicMock.

    Returns:
        A TypedMock instance with the original class's type information.

    Raises:
        TypeError: If cls is not a class.

    Example:
        >>> mock_service = typed_mock(UserService)
        >>> mock_service.get_user.return_value = {"id": 1}
        >>> mock_service.get_user(1)
        {'id': 1}
    """
```

---

## 3. Testing Conventions

### 3.1 Test Structure

```
tests/
├── conftest.py              # Common fixtures
├── unit/                    # Unit tests
│   ├── test_typed_mock.py
│   ├── test_mocked_method.py
│   └── test_protocols.py
├── integration/             # Integration tests
│   ├── test_pytest_integration.py
│   └── test_type_checker.py
└── e2e/                     # E2E tests (real-world scenarios)
    └── test_real_world.py
```

### 3.2 Test Naming

```python
# Pattern: test_<target>_<condition>_<expected_result>
def test_typed_mock_with_class_returns_mock_with_spec():
    ...

def test_mocked_method_assert_called_once_raises_when_not_called():
    ...

# Class-based tests
class TestTypedMock:
    """TypedMock class tests"""

    def test_creates_mock_with_original_type_hints(self):
        ...

    def test_supports_mock_assertion_methods(self):
        ...
```

### 3.3 Test Writing Rules

#### AAA Pattern (Arrange-Act-Assert)

```python
def test_typed_mock_return_value():
    # Arrange
    mock_service = typed_mock(UserService)
    expected = {"id": 1, "name": "John"}
    mock_service.get_user.return_value = expected

    # Act
    result = mock_service.get_user(1)

    # Assert
    assert result == expected
    mock_service.get_user.assert_called_once_with(1)
```

#### Using Fixtures

```python
# conftest.py
import pytest
from typed_pytest import TypedMock, typed_mock

@pytest.fixture
def mock_user_service() -> TypedMock[UserService]:
    """TypedMock instance of UserService"""
    return typed_mock(UserService)

# test_*.py
def test_with_fixture(mock_user_service: TypedMock[UserService]):
    mock_user_service.get_user.return_value = {"id": 1}
    ...
```

#### Parameterized Tests

```python
import pytest

@pytest.mark.parametrize(
    "method_name,expected_type",
    [
        ("assert_called", type(None)),
        ("assert_called_once", type(None)),
        ("call_count", int),
    ],
)
def test_mocked_method_has_mock_attributes(method_name: str, expected_type: type):
    mock = typed_mock(UserService)
    attr = getattr(mock.get_user, method_name)
    if callable(attr):
        result = attr()
    else:
        result = attr
    assert isinstance(result, expected_type)
```

### 3.4 Coverage Requirements

**Minimum Coverage: 80%**

```bash
# Measure coverage
uv run pytest --cov=src/typed_pytest --cov-report=term-missing --cov-report=html

# Fail CI if coverage is below threshold
uv run pytest --cov=src/typed_pytest --cov-fail-under=80
```

#### Coverage Exclusions

```python
# Exclude with pragma: no cover comment (requires reasonable justification)
if TYPE_CHECKING:  # pragma: no cover
    from typing import ParamSpec
```

---

## 4. Git Workflow

### 4.1 Branch Strategy

```
main                 # Stable version, deployment target
├── develop          # Development integration branch
│   ├── feature/*    # Feature development
│   ├── fix/*        # Bug fixes
│   └── refactor/*   # Refactoring
└── release/*        # Release preparation
```

### 4.2 Branch Naming

```bash
# Pattern: <type>/<task-id>-<short-description>
feature/T001-typed-mock-core
fix/T003-assertion-type-hints
refactor/T005-protocol-cleanup
```

### 4.3 Commit Messages

Use **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type Categories

| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Add/modify tests |
| `docs` | Documentation changes |
| `refactor` | Refactoring |
| `style` | Code style (formatting, etc.) |
| `chore` | Build, configuration changes |

#### Examples

```bash
feat(mock): Implement TypedMock generic class

- Add Generic[T] based TypedMock class
- Inherit from MagicMock to maintain existing mock functionality
- Override __class_getitem__ to store runtime type information

Closes #12

---

test(mock): Add TypedMock unit tests

- Basic creation tests
- spec parameter tests
- Type hint validation tests

Coverage: 85%
```

### 4.4 Pull Request Rules

#### PR Template

```markdown
## Changes
- [ ] Feature implementation complete
- [ ] Tests added (coverage 80%+)
- [ ] Type checks pass (mypy, pyright)
- [ ] Documentation updated

## Related Task
- Closes #<task-number>

## How to Test
1. `uv run pytest tests/unit/test_xxx.py`
2. Expected result: ...

## Screenshots (if applicable)
```

#### Review Checklist

- [ ] Are type hints correct?
- [ ] Are tests sufficient?
- [ ] Is docstring written?
- [ ] Are there breaking changes?

---

## 5. Development-Test Regression Cycle

### 5.1 TDD Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    Development Cycle                        │
│                                                             │
│   ┌─────────┐    ┌─────────┐    ┌─────────┐                │
│   │  RED    │───▶│  GREEN  │───▶│ REFACTOR│                │
│   │ (Test)  │    │ (Code)  │    │         │                │
│   └─────────┘    └─────────┘    └─────────┘                │
│        │                              │                     │
│        └──────────────────────────────┘                     │
│                    Iterate                                  │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Development Order for Each Task

1. **Write tests first** (RED)
   ```bash
   # Write failing test
   uv run pytest tests/unit/test_new_feature.py -v
   # Expected: FAILED
   ```

2. **Implement** (GREEN)
   ```bash
   # Write minimal code to pass tests
   uv run pytest tests/unit/test_new_feature.py -v
   # Expected: PASSED
   ```

3. **Refactor** (REFACTOR)
   ```bash
   # Clean up code and re-run tests
   uv run pytest tests/unit/test_new_feature.py -v
   # Expected: PASSED
   ```

4. **Full Validation**
   ```bash
   # Type check
   uv run mypy src/
   uv run pyright src/

   # Full tests + coverage
   uv run pytest --cov=src/typed_pytest --cov-fail-under=80

   # Lint
   uv run ruff check src/ tests/
   ```

### 5.3 CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.13"]

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install dependencies
        run: uv sync --all-extras

      - name: Lint
        run: uv run ruff check src/ tests/

      - name: Type check (mypy)
        run: uv run mypy src/

      - name: Type check (pyright)
        run: uv run pyright src/

      - name: Test with coverage
        run: uv run pytest --cov=src/typed_pytest --cov-fail-under=80 --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

## 6. Release Process

### 6.1 Versioning Rules

Use **Semantic Versioning (SemVer)**:

```
MAJOR.MINOR.PATCH
  │     │     └── Bug fixes (backward compatible)
  │     └──────── New features (backward compatible)
  └────────────── Breaking changes
```

### 6.2 Changelog Format

```markdown
# Changelog

## [0.2.0] - 2024-12-XX

### Added
- TypedMocker pytest fixture
- AsyncMock support

### Changed
- Improved MockedMethod signature

### Fixed
- Fixed nested mock type inference error
```

---

## 7. Questions and Help

- **Issues**: Use GitHub Issues
- **Discussion**: GitHub Discussions
- **Code Review**: PR comments

---

*Document Version: 1.0*
*Last Updated: 2024-12*

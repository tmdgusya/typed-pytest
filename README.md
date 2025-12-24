# typed-pytest

Type-safe mocking for pytest - preserve original type hints while using mock features.

## Problem

When using pytest with `unittest.mock`, type inference becomes problematic:

```python
from unittest.mock import MagicMock
from typing import cast

class UserService:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "John"}

# Problem 1: MagicMock loses original type hints
mock_service = MagicMock(spec=UserService)
mock_service.get_user(1)  # No autocomplete for get_user parameters

# Problem 2: cast() loses mock method hints
service = cast(UserService, mock_service)
service.get_user.assert_called_once()  # assert_called_once has no type hint!
```

## Solution

`typed-pytest` provides type-safe mocking that preserves both:
- Original class method signatures
- Mock assertion method type hints

```python
from typed_pytest import TypedMock, typed_mock

mock_service: TypedMock[UserService] = typed_mock(UserService)

# Original method signatures preserved
mock_service.get_user(1)  # Autocomplete for parameters

# Mock methods have type hints
mock_service.get_user.assert_called_once_with(1)  # Type-checked!
mock_service.get_user.return_value = {"id": 1}    # Type-checked!
```

## Installation

```bash
# Using uv
uv add typed-pytest

# Using pip
pip install typed-pytest
```

## Requirements

- Python 3.13+
- pytest 8.0+
- pytest-mock 3.11+

## Quick Start

```python
from typed_pytest import typed_mock, TypedMock, TypedMocker

# Method 1: Direct mock creation
def test_user_service():
    mock_service: TypedMock[UserService] = typed_mock(UserService)
    mock_service.get_user.return_value = {"id": 1, "name": "Test"}

    result = mock_service.get_user(1)

    assert result == {"id": 1, "name": "Test"}
    mock_service.get_user.assert_called_once_with(1)

# Method 2: Using pytest fixture
def test_with_fixture(typed_mocker: TypedMocker):
    mock_service = typed_mocker.mock(UserService)
    mock_service.get_user.return_value = {"id": 1}

    mock_service.get_user(1)
    mock_service.get_user.assert_called_once_with(1)
```

## Development

```bash
# Clone repository
git clone https://github.com/your-org/typed-pytest.git
cd typed-pytest

# Install dependencies
uv sync --all-extras

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/typed_pytest --cov-report=term-missing

# Type check
uv run mypy src/
uv run pyright src/

# Lint
uv run ruff check src/ tests/
uv run ruff format src/ tests/
```

## Documentation

- [Technical Specification](docs/TECH_SPEC.md)
- [Contributing Guide](docs/CONTRIBUTING.md)
- [Task Breakdown](docs/TASKS.md)
- [References](docs/REFERENCES.md)

## License

MIT

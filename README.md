# typed-pytest

**MagicMock kills your IDE autocomplete. We fix that.**

Type-safe mocking for pytest with full IDE support - autocomplete for method names, parameters, and mock assertions.

https://github.com/user-attachments/assets/f542f815-731b-4398-a8b6-fefadef19d7b



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

`typed-pytest` provides type-safe mocking with:
- **Catch typos at lint time** - Misspelled method names are caught by mypy/pyright before running tests
- **Original class method signatures** - Full auto-completion for method names and parameters
- **Type-checked mock assertions** - `assert_called_once_with()` and other assertions have full type hints
- **Type-checked mock properties** - `return_value`, `side_effect`, `call_count` are properly typed
- **IDE auto-completion** for both original methods and mock methods

```python
from typed_pytest_stubs import typed_mock, UserService

mock = typed_mock(UserService)
mock.get_usr  # ❌ Caught by type checker: "get_usr" is not a known member
mock.get_user.assert_called_once_with(1)  # ✅ Type-checked!
```

```python
from typed_pytest import TypedMock, typed_mock

mock_service: TypedMock[UserService] = typed_mock(UserService)

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

- Python 3.10+
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

## Stub Generator

`typed-pytest-generator` generates stub files for IDE auto-completion support. This allows your IDE to provide method signatures and type hints when using `typed_mock()`.

### Important: Environment Requirements

The generator **must run in your project's virtual environment** because it imports your classes to inspect their method signatures. This means:

```bash
# ✅ Correct: Run in project environment (has access to your dependencies)
uv add typed-pytest --dev
uv run typed-pytest-generator

# ❌ Wrong: uvx runs in isolated environment (no access to your dependencies)
uvx typed-pytest-generator  # Will fail if your classes import sqlalchemy, etc.
```

**Why?** The generator uses Python's `inspect` module to extract method signatures, which requires actually importing your classes. If your classes depend on `sqlalchemy`, `pydantic`, or other packages, those must be installed in the environment where the generator runs.

**Common errors:**
- `No module named 'sqlalchemy'` - Your class imports a package not in the isolated environment
- `circular import` - Your codebase has circular imports (fix with `TYPE_CHECKING` blocks)

### Basic Usage

```bash
# Generate stubs for your classes
typed-pytest-generator -t myapp.services.UserService myapp.repos.ProductRepository

# Specify custom output directory
typed-pytest-generator -t myapp.services.UserService -o my_stubs

# Include private methods (starting with _)
typed-pytest-generator -t myapp.services.UserService --include-private

# Verbose output
typed-pytest-generator -t myapp.services.UserService -v
```

### Generated Files

The generator creates the following structure:

```
typed_pytest_stubs/
├── __init__.py      # Re-exports all stub classes
└── _runtime.py      # Runtime class definitions with method signatures
```

### Using Generated Stubs

```python
# Import typed_mock from stubs package for full auto-completion
from typed_pytest_stubs import typed_mock, UserService

def test_user_service():
    # typed_mock returns UserService_TypedMock with full IDE support
    mock = typed_mock(UserService)

    mock.get_user              # ✅ Auto-complete for method names
    mock.get_user.return_value # ✅ Auto-complete for mock properties
    mock.get_user.assert_called_once_with(1)  # ✅ Type-checked!

    mock.get_user.return_value = {"id": 1, "name": "Test"}
    result = mock.get_user(1)
```

### Backend Selection

The generator supports two backends for extracting type information:

| Backend | Speed | Return Types | Use Case |
|---------|-------|--------------|----------|
| `inspect` (default) | Fast (~10ms/class) | `typing.Any` | Quick iteration during development |
| `stubgen` | Slower (~500ms/class) | Preserved (`dict[str, Any]`, `bool`, etc.) | Production, CI, better type hints |

```bash
# Use default inspect backend (fast)
typed-pytest-generator -t myapp.services.UserService

# Use stubgen backend for better type information
typed-pytest-generator --backend stubgen -t myapp.services.UserService

# Short form
typed-pytest-generator -b stubgen -t myapp.services.UserService
```

**Example output difference:**

With `inspect` backend:
```python
class UserService_TypedMock:
    @property
    def get_user(self) -> MockedMethod[[int], typing.Any]: ...
```

With `stubgen` backend:
```python
class UserService_TypedMock:
    @property
    def get_user(self) -> MockedMethod[[int], dict[str, Any]]: ...
```

### Configuration

#### pyproject.toml Configuration

You can configure `typed-pytest-generator` in your `pyproject.toml` file. This allows you to define targets, output directory, and other options without passing them via CLI every time.

```toml
[tool.typed-pytest-generator]
# List of fully qualified class names to generate stubs for
# Supports wildcard patterns:
#   - "module.*"  matches all classes in the module (non-recursive)
#   - "module.**" matches all classes in the package recursively (includes submodules)
targets = [
    "myapp.services.*",                      # All classes in myapp.services module
    "myapp.repositories.**",                 # All classes in repositories and all submodules
    "myapp.models.User",                     # Specific class
]

# Output directory for generated stubs (default: "typed_pytest_stubs")
output-dir = "typed_pytest_stubs"

# Include private methods starting with _ (default: false)
include-private = false

# Exclude specific classes from stub generation
exclude-targets = [
    "myapp.internal.PrivateHelper",
    "myapp.legacy.DeprecatedService",
]

# Backend for type extraction (default: "inspect")
# - "inspect": Fast, uses Python's inspect module
# - "stubgen": Slower, uses mypy's stubgen for accurate return types
backend = "inspect"
```

Once configured, simply run:

```bash
# Uses configuration from pyproject.toml (auto-discovered)
typed-pytest-generator

# With verbose output
typed-pytest-generator -v
```

#### CLI Options

CLI arguments take precedence over `pyproject.toml` configuration:

```bash
# Override targets from config
typed-pytest-generator -t myapp.services.NewService

# Override output directory
typed-pytest-generator -o custom_stubs

# Add exclusions (merged with config exclusions)
typed-pytest-generator -e myapp.services.SkipThis

# Use a specific config file
typed-pytest-generator -c /path/to/pyproject.toml

# Use wildcard to match all classes in a module (non-recursive)
typed-pytest-generator -t "myapp.services.*"

# Use recursive wildcard to match all classes in a package and submodules
typed-pytest-generator -t "myapp.repositories.**"

# Combine options
typed-pytest-generator -t "myapp.repositories.**" -e myapp.repositories.Internal -o stubs -v
```

#### IDE and Type Checker Setup

Add `typed_pytest_stubs/` to your `.gitignore` since these files are generated:

```gitignore
# Generated stub files
typed_pytest_stubs/
```

For pyright/pylance users, add the stubs directory to your `pyproject.toml`:

```toml
[tool.pyright]
include = ["src", "tests", "typed_pytest_stubs"]
```

#### Type Checker Configuration for Generated Stubs

Since `typed_pytest_stubs/` is typically gitignored, some type checkers need extra configuration to find the generated stubs.

**pyrefly (Meta's type checker)**

Add the project root to `search-path`:

```toml
[tool.pyrefly]
project-includes = ["src", "tests"]
# Add project root so typed_pytest_stubs can be found
search-path = ["."]
```

**ty (Astral's type checker)**

Add the project root to `extra-paths`:

```toml
[tool.ty.environment]
# Add project root so typed_pytest_stubs can be found
extra-paths = ["."]
```

**mypy and pyright**

These work out of the box since they auto-discover packages in the project root.

#### Recommended Workflow

The generated stubs should **not** be committed to Git. Instead, generate them:

1. **Before running tests locally**
   ```bash
   typed-pytest-generator && pytest
   ```

2. **In your CI pipeline**
   ```yaml
   # GitHub Actions example
   - name: Generate test stubs
     run: uv run typed-pytest-generator

   - name: Run tests
     run: uv run pytest
   ```

3. **As a Makefile target** (recommended)
   ```makefile
   test:
       uv run typed-pytest-generator
       uv run pytest
   ```

**Why not pre-commit hook or Git?**
- Generated code causes unnecessary Git conflicts
- Stubs should always reflect the current source code
- Keeps PRs clean and focused on actual changes

## Development

```bash
# Clone repository
git clone https://github.com/tmdgusya/typed-pytest.git
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

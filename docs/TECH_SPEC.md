# Typed-Pytest Technical Specification

## 1. Overview

### 1.1 Problem Definition

When using pytest and unittest.mock, the following type inference issues occur:

```python
from unittest.mock import MagicMock, patch
from typing import cast

class UserService:
    def get_user(self, user_id: int) -> dict:
        return {"id": user_id, "name": "John"}

    def create_user(self, name: str) -> dict:
        return {"id": 1, "name": name}

# Problem 1: No type inference when mocking via fixture
@pytest.fixture
def mock_user_service(mocker: MockerFixture) -> MagicMock:
    return mocker.patch("app.UserService")

def test_user(mock_user_service):  # mock_user_service type is MagicMock
    mock_user_service.get_user(1)  # No autocomplete/type hints for get_user

# Problem 2: Missing mock method type hints when using cast
def test_user_with_cast(mock_user_service):
    service = cast(UserService, mock_user_service)
    service.get_user.assert_called_once()  # ❌ assert_called_once has no type hints
    # Because UserService.get_user doesn't have assert_called_once

# Problem 3: Missing original method type hints when casting to Mock
def test_user_with_mock_cast(mock_user_service):
    service = cast(MagicMock, mock_user_service)
    service.get_user(1)  # ❌ No parameter type hints for get_user
```

### 1.2 Goals

Develop a library that enables both **original class type support** and **Mock method type inference** like Java Mockito:

```python
# Target user experience
from typed_pytest import TypedMock

def test_user(mocker: MockerFixture):
    # Support both original type + Mock type simultaneously
    mock_service: TypedMock[UserService] = typed_mock(UserService)

    mock_service.get_user(1)  # ✅ Original method signature autocomplete
    mock_service.get_user.assert_called_once_with(1)  # ✅ Mock methods with type hints
    mock_service.get_user.return_value = {"id": 1}  # ✅ return_value type hints
```

---

## 2. Technical Background

### 2.1 Current State of Python Type System

#### Current Issues

| Approach | Original Type Support | Mock Method Support | Drawback |
|----------|----------------------|---------------------|----------|
| `MagicMock` | ❌ | ✅ | Cannot infer original class methods |
| `cast(OriginalClass, mock)` | ✅ | ❌ | Cannot infer Mock methods |
| `create_autospec()` | Partial | ❌ | Runtime only, no static analysis support |

#### Python 3.13 New Features

- **PEP 696**: Default values for TypeVar, ParamSpec, TypeVarTuple
- **PEP 705**: `typing.ReadOnly` - TypedDict read-only fields
- **PEP 742**: `typing.TypeIs` - More intuitive type narrowing
- **PEP 702**: `warnings.deprecated()` decorator

### 2.2 Core Python APIs

#### 2.2.1 Generic and TypeVar

```python
from typing import TypeVar, Generic

T = TypeVar('T')

class TypedMock(Generic[T]):
    """Generic class that wraps type T's interface as Mock"""
    pass
```

#### 2.2.2 Protocol (PEP 544)

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class MockProtocol(Protocol):
    """Defines methods that Mock objects should have"""
    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    def assert_called_with(self, *args, **kwargs) -> None: ...
    def assert_called_once_with(self, *args, **kwargs) -> None: ...
    @property
    def return_value(self) -> Any: ...
    @property
    def call_count(self) -> int: ...
```

#### 2.2.3 @overload Decorator

```python
from typing import overload, Callable

class TypedMocker:
    @overload
    def patch(self, target: type[T]) -> TypedMock[T]: ...

    @overload
    def patch(self, target: str) -> MagicMock: ...

    def patch(self, target):
        # Actual implementation
        pass
```

#### 2.2.4 __class_getitem__ (PEP 560)

```python
class TypedMock:
    def __class_getitem__(cls, item: type[T]) -> type["TypedMock[T]"]:
        """Support TypedMock[UserService] syntax"""
        # Access generic type info at runtime
        return super().__class_getitem__(item)
```

#### 2.2.5 ParamSpec (PEP 612)

```python
from typing import ParamSpec, Callable

P = ParamSpec('P')
R = TypeVar('R')

class MockedMethod(Generic[P, R]):
    """Mock method that preserves original method's signature"""
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...
    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
```

---

## 3. Design Approach

### 3.1 Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        typed_pytest                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │   TypedMock[T]   │    │  MockedMethod    │                  │
│  │  (Generic[T])    │◄───│  [P, R]          │                  │
│  │                  │    │                  │                  │
│  │ - All method     │    │ - Preserves      │                  │
│  │   signatures     │    │   original sig P │                  │
│  │   from T         │    │ - Mock method    │                  │
│  │ - Mock protocol  │    │   type hints     │                  │
│  │   methods        │    │                  │                  │
│  └──────────────────┘    └──────────────────┘                  │
│                                                                 │
│  ┌──────────────────┐    ┌──────────────────┐                  │
│  │  typed_mock()    │    │  TypedMocker     │                  │
│  │  Factory func    │    │  (pytest integ)  │                  │
│  └──────────────────┘    └──────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation Strategies

#### Strategy A: Protocol Intersection Approach

Python doesn't have official Intersection types, so combine Protocols using multiple inheritance:

```python
from typing import Protocol, Generic, TypeVar

T = TypeVar('T')

class MockMethods(Protocol):
    """Mock-specific methods"""
    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    # ...

# Problem: Difficult to dynamically combine T's methods with MockMethods
```

#### Strategy B: Type Stub (.pyi) Generation Approach

Analyze original classes at build time and auto-generate type stubs:

```python
# Auto-generated user_service.pyi
class MockedUserService(UserService, MockProtocol):
    def get_user(self, user_id: int) -> MockedMethod[..., dict]: ...
```

#### Strategy C: Generic + @overload Combination (Recommended)

```python
from typing import Generic, TypeVar, overload, TYPE_CHECKING
from unittest.mock import MagicMock

T = TypeVar('T')

class TypedMock(MagicMock, Generic[T]):
    """
    Class that provides Mock functionality while maintaining
    the interface of original type T

    Type checker recognizes all methods of T,
    each method is wrapped as MockedMethod for assert_* method access
    """

    if TYPE_CHECKING:
        # Only type checker sees this definition
        def __getattr__(self, name: str) -> MockedMethod: ...

@overload
def typed_mock(cls: type[T], /) -> TypedMock[T]: ...

@overload
def typed_mock(cls: type[T], /, **kwargs) -> TypedMock[T]: ...

def typed_mock(cls, /, **kwargs):
    """Create type-safe Mock object"""
    return TypedMock(spec=cls, **kwargs)
```

### 3.3 MockedMethod Design

```python
from typing import Generic, ParamSpec, TypeVar, Callable

P = ParamSpec('P')
R = TypeVar('R')

class MockedMethod(Generic[P, R]):
    """
    Provides Mock functionality while preserving original method's signature

    Example: UserService.get_user(user_id: int) -> dict
    → MockedMethod[[int], dict]
    """

    # Callable like original method
    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    # Mock assertion methods
    def assert_called(self) -> None: ...
    def assert_called_once(self) -> None: ...
    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None: ...
    def assert_not_called(self) -> None: ...

    # Mock properties
    @property
    def return_value(self) -> R: ...
    @return_value.setter
    def return_value(self, value: R) -> None: ...

    @property
    def side_effect(self) -> Callable[P, R] | Exception | None: ...
    @side_effect.setter
    def side_effect(self, value: Callable[P, R] | Exception | list) -> None: ...

    @property
    def call_count(self) -> int: ...

    @property
    def call_args(self) -> tuple[tuple, dict] | None: ...

    @property
    def call_args_list(self) -> list[tuple[tuple, dict]]: ...
```

---

## 4. pytest Integration

### 4.1 TypedMocker Fixture

```python
from pytest_mock import MockerFixture
from typing import TypeVar, overload
import pytest

T = TypeVar('T')

class TypedMocker:
    """Type-safe mocker extending pytest-mock's MockerFixture"""

    def __init__(self, mocker: MockerFixture):
        self._mocker = mocker

    @overload
    def mock(self, cls: type[T]) -> TypedMock[T]: ...

    @overload
    def patch(
        self,
        target: str,
        new: type[T] | None = None,
    ) -> TypedMock[T]: ...

    def patch(self, target, new=None, **kwargs):
        """Type-safe patch"""
        if new is not None:
            mock = TypedMock(spec=new)
            return self._mocker.patch(target, mock, **kwargs)
        return self._mocker.patch(target, **kwargs)

    def create_autospec(self, cls: type[T]) -> TypedMock[T]:
        """Type-safe autospec creation"""
        from unittest.mock import create_autospec
        mock = create_autospec(cls, instance=True)
        # Wrap with TypedMock
        return TypedMock(spec=cls, wraps=mock)

@pytest.fixture
def typed_mocker(mocker: MockerFixture) -> TypedMocker:
    """Type-safe mocker fixture"""
    return TypedMocker(mocker)
```

### 4.2 Usage Examples

```python
# tests/test_user_service.py
from typed_pytest import TypedMock, typed_mocker, TypedMocker
from app.services import UserService

def test_get_user(typed_mocker: TypedMocker):
    # Method 1: Create mock directly
    mock_service: TypedMock[UserService] = typed_mocker.mock(UserService)

    # Original type method signature support ✅
    mock_service.get_user.return_value = {"id": 1, "name": "John"}

    # Mock method type hints support ✅
    mock_service.get_user(1)
    mock_service.get_user.assert_called_once_with(1)  # Parameter types checked

def test_with_patch(typed_mocker: TypedMocker):
    # Method 2: Using patch
    with typed_mocker.patch("app.services.UserService", UserService) as mock_service:
        mock_service.create_user.return_value = {"id": 1, "name": "Test"}

        # Test logic
        result = some_function_using_user_service()

        mock_service.create_user.assert_called_once_with("Test")
```

---

## 5. Technical Challenges and Solutions

### 5.1 Dynamic Method Attribute Type Inference

**Problem**: Need to tell type checker that `mock_service.get_user` is `MockedMethod`

**Solution**: `__getattr__` type hints + type stubs

```python
# typed_pytest.pyi (type stub)
from typing import Generic, TypeVar, overload

T = TypeVar('T')

class TypedMock(Generic[T]):
    @overload
    def __getattr__(self, name: str) -> MockedMethod: ...

    # Or more precisely:
    # Dynamically return MockedMethod type for each method of T
```

### 5.2 Preserving Original Class Method Signatures

**Problem**: `TypedMock[UserService]` needs to know all methods of `UserService`

**Solutions**:
1. **TYPE_CHECKING branch**: Definitions visible only to type checker
2. **Plugin approach**: Inject type info via mypy/pyright plugin

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import _SpecialForm
    # Type checker only definition
    class TypedMock(Generic[T]):
        # Transform all attributes of T to MockedMethod
        pass
else:
    # Runtime definition
    class TypedMock(MagicMock):
        pass
```

### 5.3 Lack of Intersection Type

**Problem**: Python has no official Intersection type

**Solution Options**:

1. **Use typing-protocol-intersection library**
   ```python
   from typing_protocol_intersection import ProtocolIntersection as Has

   def typed_mock(cls: type[T]) -> Has[T, MockProtocol]:
       ...
   ```

2. **Multiple inheritance Protocol definition**
   ```python
   class TypedMock(Generic[T], MockProtocol):
       """Implements both T and MockProtocol"""
       pass
   ```

3. **Use Union in type stubs** (partial solution)

---

## 6. Dependencies and Compatibility

### 6.1 Required Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Python | ≥3.13 | Base language, latest typing features |
| pytest | ≥8.0 | Test framework |
| pytest-mock | ≥3.11 | MockerFixture base |

### 6.2 Optional Dependencies

| Package | Purpose |
|---------|---------|
| typing-extensions | Backward compatibility (if needed) |
| typing-protocol-intersection | Intersection type support |
| mypy | Type checking |
| pyright | Type checking (VS Code Pylance) |

### 6.3 Development Dependencies

```toml
[project.optional-dependencies]
dev = [
    "mypy>=1.8",
    "pyright>=1.1.350",
    "ruff>=0.1.0",
    "pytest>=8.0",
    "pytest-mock>=3.11",
]
```

---

## 7. Project Structure

```
typed-pytest/
├── src/
│   └── typed_pytest/
│       ├── __init__.py          # Public API
│       ├── _mock.py             # TypedMock implementation
│       ├── _method.py           # MockedMethod implementation
│       ├── _mocker.py           # TypedMocker (pytest integration)
│       ├── _protocols.py        # Protocol definitions
│       ├── py.typed             # PEP 561 marker
│       └── _version.py          # Version info
├── stubs/
│   └── typed_pytest/
│       └── __init__.pyi         # Type stubs (if needed)
├── tests/
│   ├── test_typed_mock.py
│   ├── test_mocked_method.py
│   └── test_integration.py
├── docs/
│   ├── TECH_SPEC.md             # This document
│   └── CONTRIBUTING.md          # Contribution guide
├── pyproject.toml
└── README.md
```

---

## 8. Implementation Roadmap

### Phase 1: Core Features
- [x] `TypedMock[T]` generic class implementation
- [x] `MockedMethod[P, R]` implementation
- [x] Basic factory function `typed_mock()` implementation
- [x] Unit tests

### Phase 2: pytest Integration
- [x] `TypedMocker` class implementation
- [x] `typed_mocker` fixture implementation
- [x] Type-safe `patch()` method implementation
- [x] Integration tests

### Phase 3: Type Checker Support
- [x] mypy compatibility verification
- [x] pyright compatibility verification
- [x] Type stubs (if needed)
- [ ] mypy plugin development (if needed)

### Phase 4: Advanced Features
- [x] Nested mock support
- [x] Async method support
- [x] Property mock support
- [x] Class method / Static method support

---

## 9. Risk Factors and Alternatives

### 9.1 Risk Factors

| Risk | Impact | Mitigation |
|------|--------|------------|
| Behavior differences between type checkers | High | Test both mypy/pyright |
| Python version typing differences | Medium | Limit scope to 3.13+ |
| Complex generic type support limitations | Medium | Document limitations |
| Performance overhead | Low | Type hints have no runtime impact |

### 9.2 Alternative Approaches

1. **Develop mypy plugin only**: Solve at type checker level without runtime changes
2. **IDE extension development**: VS Code/PyCharm specific extension
3. **Code generator**: Auto-generate Mock type stubs from original classes

---

## 10. References

- [PEP 544 - Protocols: Structural subtyping](https://peps.python.org/pep-0544/)
- [PEP 560 - Core support for typing module and generic types](https://peps.python.org/pep-0560/)
- [PEP 612 - Parameter Specification Variables](https://peps.python.org/pep-0612/)
- [PEP 696 - Type Defaults for Type Parameters](https://peps.python.org/pep-0696/)
- [Python typing documentation](https://docs.python.org/3/library/typing.html)
- [mypy Generics documentation](https://mypy.readthedocs.io/en/stable/generics.html)
- [pytest-mock documentation](https://pytest-mock.readthedocs.io/)
- [typing-protocol-intersection](https://pypi.org/project/typing-protocol-intersection/)

---

*Document Version: 1.0*
*Last Updated: 2024-12*

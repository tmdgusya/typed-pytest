# LSP Type Inference Issue: Root Cause Analysis

## Problem

When using `TypedMock[T]` with `spec=T`, the LSP (Language Server Protocol) shows `Any` type instead of `MockedMethod` for mock attribute access like `mock.get_user`.

## Root Cause

The issue was caused by **incorrect import statement**.

### Wrong Import (Causes `Any`)
```python
from typed_pytest._mock import TypedMock  # ❌
mock = TypedMock(spec=UserService)
mock.get_user  # LSP shows: Any
```

### Correct Import (Shows `MockedMethod`)
```python
from typed_pytest import TypedMock  # ✅
mock = TypedMock(spec=UserService)
mock.get_user  # LSP shows: MockedMethod
```

## Why Does This Happen?

### How TypedMock's Type Hints Work

`TypedMock` defines its `__getattr__` return type using `TYPE_CHECKING` guard:

```python
# src/typed_pytest/_mock.py
if TYPE_CHECKING:
    def __getattr__(self, name: str) -> MockedMethod[..., Any] | AsyncMockedMethod[..., Any]:
        ...
```

The `TYPE_CHECKING` constant is `False` at runtime but `True` for type checkers.

### The Problem with Direct Import

When you import directly from `typed_pytest._mock`:
```python
from typed_pytest._mock import TypedMock
```

The `if TYPE_CHECKING:` block is **still evaluated by LSP**, but the type hints are defined in the **local module context** of `_mock.py`. The LSP may not properly propagate these type hints when the import bypasses `__init__.py`.

### The Solution: Import from Package Root

```python
from typed_pytest import TypedMock
```

When importing from the package root, `typed_pytest/__init__.py` is executed first, which properly sets up the module context. The `TYPE_CHECKING` type hints are then correctly associated with `TypedMock` in a way that LSP can properly resolve.

## How This Issue Was Discovered

1. **Initial Observation**: `mock.get_user` showed `Any` in Zed IDE despite correct implementation
2. **Hypothesis Testing**: Created test files in different locations:
   - `/tmp/test.py` → showed `MockedMethod` ✅
   - `/home/roach/typed-pytest/src/test.py` → showed `MockedMethod` ✅
   - `/home/roach/typed-pytest/tests/unit/test.py` → showed `Any` ❌
3. **Comparison**: Found the difference in import statements:
   - Working files: `from typed_pytest import TypedMock`
   - Broken files: `from typed_pytest._mock import TypedMock`
4. **Verification**: Changed import in broken files to use package root import → LSP shows `MockedMethod` ✅

## Affected Files (Fixed)

- `tests/unit/test_typed_mock.py`
- `tests/unit/test_factory.py`
- `tests/unit/test_typed_mocker.py`
- `tests/integration/test_fixture.py`
- `tests/integration/test_patch_scenarios.py`
- `tests/integration/test_real_scenarios.py`

## Solution

Always import `TypedMock` from the package root:

```python
from typed_pytest import TypedMock  # ✅ CORRECT
```

Do NOT import from internal modules:

```python
from typed_pytest._mock import TypedMock  # ❌ WRONG - Causes Any type
from typed_pytest._factory import typed_mock  # Also wrong for typed_mock
```

## Lesson Learned

When working with libraries that use `TYPE_CHECKING` guards for LSP integration, always import from the package root (`from library import Class`) rather than internal modules (`from library._internal import Class`).

This ensures that the module context is properly set up and type hints are correctly propagated to the LSP.

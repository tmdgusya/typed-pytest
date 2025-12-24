# A Hitchhiker's Guide to `.pyi` Files for Contributors

> *"Don't Panic!" — This guide is here to help you understand `.pyi` files and contribute to typed-pytest with confidence.*

---

**[Korean Version](PYI_GUIDE.ko.md)**

---

## Table of Contents

1. [What is a `.pyi` File?](#what-is-a-pyi-file)
2. [Why Do We Need `.pyi` Files?](#why-do-we-need-pyi-files)
3. [How Do Type Checkers Use `.pyi` Files?](#how-do-type-checkers-use-pyi-files)
4. [The Difference Between Runtime and Static Types](#the-difference-between-runtime-and-static-types)
5. [Common Patterns in `.pyi` Files](#common-patterns-in-pyi-files)
6. [Key Limitations to Understand](#key-limitations-to-understand)
7. [Contributing to typed-pytest: A Practical Guide](#contributing-to-typed-pytest-a-practical-guide)
8. [Troubleshooting Common Issues](#troubleshooting-common-issues)

---

## What is a `.pyi` File?

A `.pyi` file is a **type stub file** for Python. Think of it as a "type hint dictionary" that tells IDEs and type checkers what types exist in a module, without containing any actual code.

### Analogy: A Restaurant Menu

Imagine a restaurant menu:
- The **actual kitchen** (your `.py` files) contains the real code that cooks food
- The **menu** (your `.pyi` files) tells customers what dishes are available and what ingredients they contain

The menu doesn't cook food—it just describes what's available. Similarly, `.pyi` files don't run code—they just describe types.

### Example

**`typed_pytest/__init__.py`** (Runtime code):
```python
class TypedMock:
    def __init__(self, spec=None, **kwargs):
        self._mock = ...  # Actual implementation

    def __getattr__(self, name):
        return MockedMethod()  # Magic happens here!
```

**`typed_pytest/__init__.pyi`** (Type stub):
```python
class TypedMock:
    _mock: Any

    def __init__(
        self,
        spec: type[_T] | None = None,
        *,
        wraps: _T | None = None,
        name: str | None = None,
        **kwargs: Any,
    ) -> None: ...

    def __getattr__(self, name: str) -> MockedMethod: ...
```

---

## Why Do We Need `.pyi` Files?

Python is a **dynamically typed language**, which means:

```python
# This is valid Python - but what type is result?
result = some_mock.some_method(123)
```

Type checkers (like mypy, pyright) can't automatically know what `some_method` returns or what parameters it accepts. This is where `.pyi` files help!

### The Problem Without `.pyi`

```python
from unittest.mock import MagicMock

mock = MagicMock()
mock.get_user(1)  # IDE has no idea what get_user returns!
mock.get_user.assert_called_once_with(1)  # No type checking!
```

### The Solution With `.pyi`

```python
from typed_pytest import TypedMock, typed_mock

mock_service: TypedMock[UserService] = typed_mock(UserService)
mock_service.get_user.assert_called_once_with(1)  # ✅ Fully type-checked!
```

---

## How Do Type Checkers Use `.pyi` Files?

When you run a type checker (mypy, pyright, etc.), here's what happens:

```
1. You write code
   ↓
2. Type checker reads your .py file
   ↓
3. Type checker looks for matching .pyi stub file
   ↓
4. Type checker uses .pyi to understand types
   ↓
5. Type checker reports errors or confirms correctness
```

### Example: How pyright Uses Stubs

```
user_code.py          user_code.pyi (if exists)
┌──────────────┐      ┌──────────────┐
│ typed_mock() │ ───▶ │ "I return    │
│      ↓       │      │  TypedMock   │
│ get_user.    │      │  [T]"        │
│ assert_...   │      └──────────────┘
└──────────────┘
```

**Important**: Type checkers prefer `.pyi` files over `.py` files when both exist. The `.pyi` file "shadows" the actual implementation for type-checking purposes.

---

## The Difference Between Runtime and Static Types

This is the **most important concept** to understand!

### Runtime: What Actually Happens

When Python runs your code, it executes statements line by line:

```python
# This actually runs and creates objects
mock = TypedMock[UserService]()
mock.get_user(1)  # Calls TypedMock.__getattr__("get_user")
```

At runtime:
- `__getattr__` is called with the actual attribute name
- A `MockedMethod` object is created
- Your code continues

### Static: What Type Checkers See

Type checkers analyze your code **without running it**:

```python
mock: TypedMock[UserService] = typed_mock(UserService)
mock.get_user(1)
```

Type checker sees:
- `mock` is of type `TypedMock[UserService]`
- `mock.get_user` returns `MockedMethod` (from `__getattr__`)

**The problem**: Type checkers can't predict what attribute names you'll access! They see `__getattr__` exists, but they don't know the specific names like `"get_user"`, `"create_user"`, etc.

---

## Common Patterns in `.pyi` Files

Here are patterns you'll see in typed-pytest's `.pyi` files:

### 1. The Ellipsis (`...`) for Method Bodies

```python
def __init__(self, spec: type[_T] | None = None) -> None: ...
```

The `...` (ellipsis) means "this method exists, but has no body in the stub". It's just a placeholder for type information.

### 2. Type Variables for Generics

```python
_T = TypeVar("_T")

class TypedMock(Generic[_T]):
    # _T will be replaced with the actual type (e.g., UserService)
    def get_typed_class(self) -> type[_T] | None: ...
```

### 3. Optional Types with `|`

```python
def __init__(self, name: str | None = None) -> None: ...
# Equivalent to: name: Optional[str] = None
```

### 4. Properties (Getters/Setters)

```python
@property
def return_value(self) -> Any: ...

@return_value.setter
def return_value(self, value: Any) -> None: ...
```

### 5. The `Any` Type

```python
def __call__(self, *args: Any, **kwargs: Any) -> Any: ...
```

`Any` means "any type is acceptable" — it tells the type checker "don't worry about this, just accept it."

---

## Key Limitations to Understand

Before contributing, you need to know what `.pyi` files **can't** do:

### ❌ `__getattr__` Doesn't Provide Autocomplete for Attribute Names

```python
class TypedMock:
    def __getattr__(self, name: str) -> MockedMethod: ...
```

**What this means:**
- ✅ Type checker knows `mock.get_user` returns `MockedMethod`
- ❌ Type checker can't suggest "get_user" as a completion option

**Why?** The type checker doesn't know what attribute names you'll use at runtime. It only knows the pattern (`__getattr__` returns `MockedMethod` for any name).

### ❌ Original Method Signatures Aren't Preserved

```python
# UserService.get_user signature:
# def get_user(self, user_id: int) -> dict

mock.get_user(1)  # Parameters aren't type-checked!
```

**What this means:**
- ❌ `mock.get_user(1)` won't tell you if `1` is the right type
- ✅ But `mock.get_user.assert_called_once_with(1)` IS type-checked!

### ❌ You Can't "Auto-Discover" Method Names

```python
# There's no way in .pyi to say:
# "Look at UserService and auto-generate get_user, create_user, etc."
```

The `.pyi` file must explicitly list all possible attributes, which is why we use `__getattr__` as a catch-all.

---

## Contributing to typed-pytest: A Practical Guide

Now that you understand the basics, here's how to contribute:

### Step 1: Understand What You're Adding

Ask yourself:
- Are you adding a **new feature** to the runtime code?
- Are you **updating type hints**?
- Are you **fixing a bug**?

### Step 2: Update Both `.py` and `.pyi`

**Always update both files together:**

| File | Purpose |
|------|---------|
| `.py` | Runtime implementation (actual behavior) |
| `.pyi` | Type stubs (for IDEs and type checkers) |

### Step 3: Example — Adding a New Method

**Original code:**
```python
# typed_pytest/__init__.py
class TypedMock:
    def reset_mock(self) -> None:
        """Reset the mock to initial state."""
        self._mock.reset_mock()
```

**Updated code with new feature:**
```python
# typed_pytest/__init__.py
class TypedMock:
    def reset_mock(self, return_value: bool = False) -> None:
        """Reset the mock to initial state."""
        self._mock.reset_mock(return_value=return_value)
```

**Must also update `.pyi`:**
```python
# typed_pytest/__init__.pyi
class TypedMock:
    def reset_mock(self, return_value: bool = False) -> None: ...
```

### Step 4: Testing Your Changes

Run these commands to verify your changes:

```bash
# Run all checks
uv run pytest tests/
uv run ruff check src/
uv run ruff format src/
uv run mypy src/
uv run pyright src/
```

### Step 5: Common Patterns to Follow

#### Adding a Property
```python
# In .pyi
@property
def my_property(self) -> ReturnType: ...

@my_property.setter
def my_property(self, value: ReturnType) -> None: ...
```

#### Adding a Method
```python
# In .pyi
def my_method(self, param: ParamType, /, *, optional: OptType = None) -> ReturnType: ...
```

#### Using TypeVars
```python
# At the top of .pyi
_T = TypeVar("_T")

# In class
class TypedMock(Generic[_T]):
    def get_typed(self) -> _T: ...
```

---

## Troubleshooting Common Issues

### Issue: "Type checker doesn't recognize my change"

**Solution:** Make sure you updated both `.py` and `.pyi` files. Also try restarting your type checker/IDE.

### Issue: "Autocomplete isn't working for mock methods"

**This is expected behavior!** Due to `__getattr__` limitations:
- You can access `mock.some_method.assert_called_once()`
- But IDE won't suggest `some_method` in autocomplete

### Issue: "Type checker says 'Unknown attribute'"

**Check:**
1. Did you add the method to both `.py` and `.pyi`?
2. Is the method signature correct?
3. Did you run the type checker after changes?

### Issue: "I want to add auto-completion for method names"

**Unfortunately, this is a fundamental limitation of Python's type system.** The `.pyi` format can't express "all methods of class X are available here." You'd need:
- IDE-specific plugins
- Or a completely different approach to mocking

---

## Quick Reference

| Concept | What It Means |
|---------|---------------|
| `.pyi` | Type stub file — describes types without code |
| Runtime | What happens when code actually executes |
| Static | What type checkers analyze (without running) |
| `__getattr__` | Magic method called for unknown attributes |
| `...` (ellipsis) | Placeholder meaning "no implementation here" |
| `Generic` | A class that can work with multiple types |
| `TypeVar` | A placeholder for a type that will be specified later |

---

## Further Reading

- [PEP 484 — Type Hints](https://peps.python.org/pep-0484/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [pyright documentation](https://microsoft.github.io/pyright/)
- [Python typing module](https://docs.python.org/3/library/typing.html)

---

## Summary

- **`.pyi` files are type stubs** that help IDEs and type checkers understand your code
- **Runtime and static types are different** — `.pyi` doesn't affect how code runs
- **`__getattr__` has limitations** — it provides type info but not autocomplete for attribute names
- **Contributing requires updating both files** — always keep `.py` and `.pyi` in sync
- **Don't panic!** If you're confused, you're asking the right questions

---

*Remember: Every expert was once a beginner. The fact that you're reading this guide means you're on the right track!*

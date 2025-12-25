"""Type stub package for typed-pytest.

This package provides stub classes for IDE auto-completion.
Import from here to get type-safe mocks.

Example:
    from typed_pytest_stubs import UserService
    mock = typed_mock(UserService)
    mock.get_user(1)  # Auto-complete works!
"""
from __future__ import annotations

# Re-export all stub classes from _runtime for runtime compatibility
from ._runtime import (
    UserService,
    UserService_TypedMock,
    UserServiceMock,
    ProductRepository,
    ProductRepository_TypedMock,
    ProductRepositoryMock
)

__all__ = [
    "UserService",
    "UserService_TypedMock",
    "UserServiceMock",
    "ProductRepository",
    "ProductRepository_TypedMock",
    "ProductRepositoryMock"
]

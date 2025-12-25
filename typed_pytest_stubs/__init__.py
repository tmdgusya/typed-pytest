"""Type stub package for typed-pytest.

This package provides stub classes for IDE auto-completion.
Import typed_mock from here to get type-safe mocks with full auto-completion.

Example:
    from typed_pytest_stubs import typed_mock, UserService

    mock = typed_mock(UserService)
    mock.get_user              # Auto-complete works!
    mock.get_user.return_value # Auto-complete works!
"""
from __future__ import annotations

# Re-export all stub classes from _runtime for runtime compatibility
from ._runtime import (
    GenericService,
    GenericService_TypedMock,
    GenericServiceMock,
    NestedService,
    NestedService_TypedMock,
    NestedServiceMock,
    Product,
    Product_TypedMock,
    ProductMock,
    ProductRepository,
    ProductRepository_TypedMock,
    ProductRepositoryMock,
    User,
    User_TypedMock,
    UserMock,
    UserRepository,
    UserRepository_TypedMock,
    UserRepositoryMock,
    UserService,
    UserService_TypedMock,
    UserServiceMock,
    typed_mock
)

__all__ = [
    "GenericService",
    "GenericService_TypedMock",
    "GenericServiceMock",
    "NestedService",
    "NestedService_TypedMock",
    "NestedServiceMock",
    "Product",
    "Product_TypedMock",
    "ProductMock",
    "ProductRepository",
    "ProductRepository_TypedMock",
    "ProductRepositoryMock",
    "User",
    "User_TypedMock",
    "UserMock",
    "UserRepository",
    "UserRepository_TypedMock",
    "UserRepositoryMock",
    "UserService",
    "UserService_TypedMock",
    "UserServiceMock",
    "typed_mock"
]

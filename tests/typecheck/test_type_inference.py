"""Type inference validation tests.

This file is checked by type checkers (mypy, pyright).
These are static type checks, not runtime tests."""

import contextlib
from typing import Any

from typed_pytest_stubs import ProductRepository, UserService, typed_mock

from tests.fixtures.sample_classes import UserService as RealUserService
from typed_pytest import TypedMock
from typed_pytest import typed_mock as original_typed_mock


def test_typed_mock_creation() -> None:
    """Type inference when creating typed_mock."""
    # typed_mock should return TypedMock[T]
    mock: TypedMock[UserService] = typed_mock(UserService)
    assert mock is not None


def test_typed_mock_class_annotation() -> None:
    """TypedMock class annotation."""
    mock: TypedMock[UserService] = TypedMock(spec=UserService)
    assert mock is not None


def test_method_access() -> None:
    """Type safety when accessing methods."""
    mock = typed_mock(UserService)

    # Should be able to access original class methods
    mock.get_user(1)  # int parameter
    mock.create_user("name", "email@example.com")  # str parameters
    mock.delete_user(1)  # int parameter


def test_return_value_type() -> None:
    """Setting return_value."""
    mock = typed_mock(UserService)

    # Can set return_value
    mock.get_user.return_value = {"id": 1, "name": "Test"}

    # Using return value (mock returns Any, so type as Any)
    result: Any = mock.get_user(1)
    assert result is not None


def test_assertion_methods() -> None:
    """Mock assertion methods."""
    mock = typed_mock(UserService)

    mock.get_user(1)

    # Call assertion methods
    mock.get_user.assert_called()
    mock.get_user.assert_called_once()
    mock.get_user.assert_called_with(1)
    mock.get_user.assert_called_once_with(1)


def test_mock_properties() -> None:
    """Mock property access."""
    mock = typed_mock(UserService)

    mock.get_user(1)
    mock.get_user(2)

    # Property access
    count: int = mock.get_user.call_count
    called: bool = mock.get_user.called
    assert count == 2
    assert called is True


def test_side_effect() -> None:
    """Setting side_effect."""
    mock = typed_mock(UserService)

    # Set side_effect as list
    mock.get_user.side_effect = [
        {"id": 1, "name": "First"},
        {"id": 2, "name": "Second"},
    ]

    # Sequential returns
    first = mock.get_user(1)
    second = mock.get_user(2)
    assert first is not None
    assert second is not None


def test_side_effect_exception() -> None:
    """Setting side_effect with exception."""
    mock = typed_mock(UserService)

    # Set side_effect as exception
    mock.get_user.side_effect = ValueError("Not found")

    with contextlib.suppress(ValueError):
        mock.get_user(999)


def test_multiple_mocks() -> None:
    """Using multiple mocks simultaneously."""
    mock_service: TypedMock[UserService] = typed_mock(UserService)
    mock_repo: TypedMock[ProductRepository] = typed_mock(ProductRepository)

    mock_service.get_user.return_value = {"id": 1}
    mock_repo.find_by_id.return_value = None

    # Types are independent
    user_result = mock_service.get_user(1)
    product_result = mock_repo.find_by_id("P001")

    assert user_result is not None
    assert product_result is None


def test_spec_set_option() -> None:
    """spec_set option."""
    mock = typed_mock(UserService, spec_set=True)

    # Existing methods are accessible
    mock.get_user(1)
    mock.get_user.assert_called_once()


def test_reset_mock() -> None:
    """Calling reset_mock."""
    mock = typed_mock(UserService)

    mock.get_user(1)
    mock.get_user.reset_mock()

    # Call count reset after reset
    count: int = mock.get_user.call_count
    assert count == 0


def test_call_args() -> None:
    """Accessing call_args, call_args_list."""
    mock = typed_mock(UserService)

    mock.get_user(1)
    mock.get_user(2)

    # Access call_args
    args = mock.get_user.call_args
    args_list = mock.get_user.call_args_list

    assert args is not None
    assert args_list is not None
    assert len(args_list) == 2


# =============================================================================
# Async Method Type Tests (T300, T301)
# =============================================================================


def test_async_method_access() -> None:
    """Type safety when accessing async methods."""
    mock = typed_mock(UserService)

    # Should be able to access async methods
    mock.async_get_user(1)  # int parameter
    mock.async_create_user("name", "email@example.com")  # str parameters


def test_async_return_value_type() -> None:
    """Setting return_value for async methods."""
    mock = typed_mock(UserService)

    # Can set return_value
    mock.async_get_user.return_value = {"id": 1, "name": "Test"}

    # Using return value (mock returns Any, so type as Any)
    result: Any = mock.async_get_user(1)
    assert result is not None


def test_async_assertion_methods() -> None:
    """Async Mock assertion methods."""
    mock = typed_mock(UserService)

    # Call async method (validate types without async context)
    mock.async_get_user(1)

    # Call assertion methods
    mock.async_get_user.assert_called()
    mock.async_get_user.assert_called_once()
    mock.async_get_user.assert_called_with(1)
    mock.async_get_user.assert_called_once_with(1)


def test_async_assert_awaited_methods() -> None:
    """Async Mock await assertion methods (type-only validation).

    Note: assert_awaited* methods should be called after actual await.
    We only verify method existence for type validation.
    Uses RealUserService which has async def methods.
    """
    mock = original_typed_mock(RealUserService)

    # Verify await assertion methods exist (type-only)
    # These would error at runtime, so use only for type checking
    _ = mock.async_get_user.assert_awaited
    _ = mock.async_get_user.assert_awaited_once
    _ = mock.async_get_user.assert_awaited_with


def test_async_mock_properties() -> None:
    """Async Mock property access.

    Uses RealUserService which has async def methods.
    """
    mock = original_typed_mock(RealUserService)

    # Property access
    count: int = mock.async_get_user.call_count
    called: bool = mock.async_get_user.called
    await_count: int = mock.async_get_user.await_count

    assert count == 0
    assert called is False
    assert await_count == 0


def test_async_side_effect() -> None:
    """Setting side_effect for async methods."""
    mock = typed_mock(UserService)

    # Set side_effect as list
    mock.async_get_user.side_effect = [
        {"id": 1, "name": "First"},
        {"id": 2, "name": "Second"},
    ]


def test_async_side_effect_exception() -> None:
    """Setting side_effect with exception for async methods."""
    mock = typed_mock(UserService)

    # Set side_effect as exception
    mock.async_get_user.side_effect = ValueError("Not found")


def test_sync_and_async_methods_separation() -> None:
    """Verify sync and async methods return different types."""
    mock = typed_mock(UserService)

    # Both sync and async methods are accessible
    mock.get_user(1)
    mock.async_get_user(1)

    # Call respective assertion methods
    mock.get_user.assert_called_once()
    mock.async_get_user.assert_called_once()

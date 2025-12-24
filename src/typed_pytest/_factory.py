"""
typed_mock factory function.

Factory function for creating type-safe Mock objects.
"""

from __future__ import annotations

from typing import Any, TypeVar, overload

from typed_pytest._mock import TypedMock


T = TypeVar("T")


@overload
def typed_mock(cls: type[T], /) -> TypedMock[T]: ...


@overload
def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    name: str | None = None,
    **kwargs: Any,
) -> TypedMock[T]: ...


def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    name: str | None = None,
    **kwargs: Any,
) -> TypedMock[T]:
    """Creates a type-safe Mock object.

    Returns a TypedMock instance that provides Mock functionality
    while preserving the original class's type information.

    This function provides a more concise API than `TypedMock(spec=cls)`.

    Args:
        cls: Original class to mock.
        spec_set: If True, accessing/setting attributes not in spec raises AttributeError.
            Default is False.
        name: Name of the Mock (for debugging). Default is None.
        **kwargs: Additional arguments to pass to MagicMock.

    Returns:
        TypedMock instance with the original class's type information.

    Raises:
        TypeError: If cls is not a class.

    Example:
        Basic usage:
            >>> from typed_pytest import typed_mock
            >>> mock_service = typed_mock(UserService)
            >>> mock_service.get_user.return_value = {"id": 1}
            >>> mock_service.get_user(1)
            {'id': 1}
            >>> mock_service.get_user.assert_called_once_with(1)

        Using spec_set:
            >>> mock = typed_mock(UserService, spec_set=True)
            >>> mock.nonexistent_method()  # AttributeError!

        Using name:
            >>> mock = typed_mock(UserService, name="test_mock")
            >>> print(mock)  # <TypedMock[UserService] name='test_mock'>

    Note:
        - Using `spec_set=True` raises AttributeError when accessing or setting
          attributes not in the original class. This is useful for preventing typos.
    """
    # Validate that cls is a class (runtime type check)
    # Note: pyright already knows it's type[T] from the type hint,
    # but we need to validate at runtime since users can pass incorrect values
    if not isinstance(cls, type):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = f"typed_mock() argument must be a class, not {type(cls).__name__!r}"
        raise TypeError(msg)

    # Create TypedMock
    if spec_set:
        return TypedMock(spec_set=cls, name=name, **kwargs)
    return TypedMock(spec=cls, name=name, **kwargs)

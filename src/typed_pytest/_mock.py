"""
TypedMock generic class.

Provides Mock functionality while preserving the interface of the original type T.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from unittest.mock import AsyncMock, MagicMock


if TYPE_CHECKING:
    from typed_pytest._method import AsyncMockedMethod, MockedMethod


T = TypeVar("T")


class TypedMock(MagicMock, Generic[T]):  # pyright: ignore[reportInconsistentConstructor]
    """Provides Mock functionality while preserving the interface of the original type T.

    TypedMock inherits from MagicMock to provide all Mock functionality,
    while maintaining the original class's type information through the generic type parameter T.

    Usage:
        >>> from typed_pytest import TypedMock
        >>> mock_service: TypedMock[UserService] = TypedMock(spec=UserService)
        >>> mock_service.get_user(1)  # Original signature autocomplete
        >>> mock_service.get_user.assert_called_once_with(1)  # Mock method type hints

    Example:
        >>> from unittest.mock import MagicMock
        >>> class UserService:
        ...     def get_user(self, user_id: int) -> dict: ...
        >>> mock: TypedMock[UserService] = TypedMock(spec=UserService)
        >>> mock.get_user.return_value = {"id": 1, "name": "Test"}
        >>> mock.get_user(1)
        {'id': 1, 'name': 'Test'}
        >>> mock.get_user.assert_called_once_with(1)

    Note:
        Using the `typed_mock()` factory function is typically more convenient.
    """

    # Declaring _typed_class as instance variable (conflict prevention with MagicMock)
    __slots__ = ()

    def __init__(
        self,
        spec: type[T] | None = None,
        *,
        wraps: T | None = None,
        name: str | None = None,
        spec_set: type[T] | None = None,
        **kwargs: Any,
    ) -> None:
        """Creates a TypedMock instance.

        Args:
            spec: Class to use as the Mock's spec. Only this class's attributes are accessible.
            wraps: Object to wrap if wrapping a real object.
            name: Name of the Mock (for debugging).
            spec_set: Same as spec, but also restricts attribute setting.
            **kwargs: Additional arguments to pass to MagicMock.
        """
        # Determine spec or spec_set
        actual_spec = spec_set or spec
        if spec_set is not None:
            kwargs["spec_set"] = spec_set
        elif spec is not None:
            kwargs["spec"] = spec

        if wraps is not None:
            kwargs["wraps"] = wraps
        if name is not None:
            kwargs["name"] = name

        super().__init__(**kwargs)

        # Store type information (bypass MagicMock's __setattr__)
        object.__setattr__(self, "_typed_class", actual_spec)

    if TYPE_CHECKING:
        # Only visible to type checkers
        def __getattr__(
            self, name: str
        ) -> MockedMethod[..., Any] | AsyncMockedMethod[..., Any]:
            """Informs the type checker to return MockedMethod or AsyncMockedMethod."""
            ...

    def _get_child_mock(self, **kwargs: Any) -> MagicMock:
        """Returns AsyncMock for async methods when creating child Mocks."""
        name = kwargs.get("name")
        if name and self.typed_class is not None:
            for cls in self.typed_class.__mro__:
                if name in cls.__dict__:
                    attr = cls.__dict__[name]
                    if inspect.iscoroutinefunction(attr):
                        return AsyncMock(**kwargs)
                    break
        return MagicMock(**kwargs)

    @property
    def typed_class(self) -> type[T] | None:
        """The original class passed as the generic parameter."""
        result: type[T] | None = object.__getattribute__(self, "_typed_class")
        return result

    def __repr__(self) -> str:
        """String representation of TypedMock."""
        typed_class = object.__getattribute__(self, "_typed_class")
        name = self._mock_name

        if typed_class is not None:
            if name:
                return f"<TypedMock[{typed_class.__name__}] name='{name}'>"
            return f"<TypedMock[{typed_class.__name__}] id='{id(self)}'>"

        if name:
            return f"<TypedMock name='{name}'>"
        return f"<TypedMock id='{id(self)}'>"

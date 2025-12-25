"""
Mock wrapper classes for properties, class methods, and static methods.

Provides type-safe mocking for:
- Properties (return value access)
- Class methods (cls as first argument)
- Static methods (no self/cls)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, ParamSpec, TypeVar, cast


if TYPE_CHECKING:
    from collections.abc import Callable
    from unittest.mock import MagicMock


P = ParamSpec("P")
R = TypeVar("R")


class MockedProperty(Generic[R]):
    """Mock wrapper for property return values.

    Provides type-safe access to property mock functionality while
    delegating to the underlying MagicMock.

    Usage:
        >>> from unittest.mock import MagicMock
        >>> mock = MagicMock()
        >>> prop: MockedProperty[SomeObject] = MockedProperty(mock)
        >>> prop.return_value = SomeObject()
        >>> result = prop.some_method()  # Type-checked!

    Note:
        This class is typically not used directly,
        but is automatically created through TypedMock[T].
    """

    __slots__ = ("_mock",)

    def __init__(self, mock: MagicMock) -> None:
        """Creates a MockedProperty instance.

        Args:
            mock: The MagicMock instance to wrap.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Property interface
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Value to return when the property is accessed.

        Type checkers recognize the original property's return type R.
        """
        return cast("R", self._mock.return_value)

    @return_value.setter
    def return_value(self, value: R) -> None:
        """Sets the value to return when the property is accessed.

        Type checkers validate against the original property's return type R.

        Args:
            value: The return value to set (type R).
        """
        self._mock.return_value = value

    @property
    def side_effect(
        self,
    ) -> Callable[..., R] | BaseException | list[Any] | None:
        """Side effect to raise when the property is accessed.

        - Callable: Function to execute when accessed.
        - Exception: Exception to raise when accessed.
        - list: List of values to return sequentially.
        - None: No side effect (use return_value).
        """
        return self._mock.side_effect  # type: ignore[no-any-return]

    @side_effect.setter
    def side_effect(
        self, value: Callable[..., R] | BaseException | list[Any] | None
    ) -> None:
        """Sets the side effect to raise when the property is accessed.

        Args:
            value: The side effect (function, exception, list of values, or None).
        """
        self._mock.side_effect = value

    # =========================================================================
    # Call tracking (for properties that are called as methods)
    # =========================================================================

    @property
    def call_count(self) -> int:
        """Number of times the property was accessed."""
        return cast("int", self._mock.call_count)

    @property
    def called(self) -> bool:
        """Whether the property was accessed at least once."""
        return cast("bool", self._mock.called)

    @property
    def call_args(self) -> Any:
        """Arguments of the last access. None if never accessed."""
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """List of arguments for all accesses."""
        result: list[Any] = list(self._mock.call_args_list)
        return result

    # =========================================================================
    # Assertion methods
    # =========================================================================

    def assert_called(self) -> None:
        """Verifies that the property was accessed at least once.

        Raises:
            AssertionError: If never accessed.
        """
        self._mock.assert_called()

    def assert_called_once(self) -> None:
        """Verifies that the property was accessed exactly once.

        Raises:
            AssertionError: If access count is not 1.
        """
        self._mock.assert_called_once()

    def assert_called_with(self, *args: Any, **kwargs: Any) -> None:
        """Verifies that the property was accessed with the specified arguments.

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If the last access's arguments don't match.
        """
        self._mock.assert_called_with(*args, **kwargs)

    def assert_called_once_with(self, *args: Any, **kwargs: Any) -> None:
        """Verifies that the property was accessed exactly once with specified arguments.

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If access count is not 1 or arguments don't match.
        """
        self._mock.assert_called_once_with(*args, **kwargs)

    def assert_any_call(self, *args: Any, **kwargs: Any) -> None:
        """Verifies that the property was accessed with specified arguments at least once.

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If never accessed with those arguments.
        """
        self._mock.assert_any_call(*args, **kwargs)

    def assert_not_called(self) -> None:
        """Verifies that the property was never accessed.

        Raises:
            AssertionError: If accessed at least once.
        """
        self._mock.assert_not_called()

    def reset_mock(
        self,
        *,
        return_value: bool = False,
        side_effect: bool = False,
    ) -> None:
        """Resets the property's access history.

        Args:
            return_value: If True, also resets return_value.
            side_effect: If True, also resets side_effect.
        """
        self._mock.reset_mock(return_value=return_value, side_effect=side_effect)

    # =========================================================================
    # Attribute access delegation
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """Delegates undefined attributes to the internal Mock.

        Args:
            name: Attribute name.

        Returns:
            The corresponding attribute from the internal Mock.
        """
        return getattr(self._mock, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Delegates attribute setting to the internal Mock or this instance.

        Args:
            name: Attribute name.
            value: Value to set.
        """
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)


class MockedClassMethod(Generic[P, R]):
    """Mock wrapper for class methods.

    Preserves the class method signature where cls is passed automatically.

    Usage:
        >>> from unittest.mock import MagicMock
        >>> mock = MagicMock()
        >>> method: MockedClassMethod[[dict], UserService] = MockedClassMethod(mock)
        >>> method.return_value = mock_instance
        >>> result = method({"key": "value"})  # Type-checked!

    Note:
        This class is typically not used directly,
        but is automatically created through TypedMock[T].
    """

    __slots__ = ("_mock",)

    def __init__(self, mock: MagicMock) -> None:
        """Creates a MockedClassMethod instance.

        Args:
            mock: The MagicMock instance to wrap.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Callable interface
    # =========================================================================

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls with the same signature as the original class method.

        Args:
            *args: Positional arguments of the original method.
            **kwargs: Keyword arguments of the original method.

        Returns:
            The Mock's return_value or side_effect result.
        """
        return self._mock(*args, **kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Assertion methods
    # =========================================================================

    def assert_called(self) -> None:
        """Verifies that the Mock was called at least once.

        Raises:
            AssertionError: If never called.
        """
        self._mock.assert_called()

    def assert_called_once(self) -> None:
        """Verifies that the Mock was called exactly once.

        Raises:
            AssertionError: If call count is not 1.
        """
        self._mock.assert_called_once()

    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called with the specified arguments (last call).

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments (original method signature).
            **kwargs: Expected keyword arguments (original method signature).

        Raises:
            AssertionError: If the last call's arguments don't match.
        """
        self._mock.assert_called_with(*args, **kwargs)

    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called exactly once with the specified arguments.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments (original method signature).
            **kwargs: Expected keyword arguments (original method signature).

        Raises:
            AssertionError: If call count is not 1 or arguments don't match.
        """
        self._mock.assert_called_once_with(*args, **kwargs)

    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called with the specified arguments at least once.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments (original method signature).
            **kwargs: Expected keyword arguments (original method signature).

        Raises:
            AssertionError: If never called with those arguments.
        """
        self._mock.assert_any_call(*args, **kwargs)

    def assert_not_called(self) -> None:
        """Verifies that the Mock was never called.

        Raises:
            AssertionError: If called at least once.
        """
        self._mock.assert_not_called()

    def assert_has_calls(
        self,
        calls: list[Any],
        any_order: bool = False,
    ) -> None:
        """Verifies that the Mock was called with the specified list of calls.

        Args:
            calls: Expected list of calls (unittest.mock.call objects).
            any_order: If True, order is ignored; if False, order must match.

        Raises:
            AssertionError: If the call list doesn't match.
        """
        self._mock.assert_has_calls(calls, any_order=any_order)

    def reset_mock(
        self,
        *,
        return_value: bool = False,
        side_effect: bool = False,
    ) -> None:
        """Resets the Mock's call history.

        Args:
            return_value: If True, also resets return_value.
            side_effect: If True, also resets side_effect.
        """
        self._mock.reset_mock(return_value=return_value, side_effect=side_effect)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Value to return when the Mock is called.

        Type checkers recognize the original method's return type R.
        """
        return cast("R", self._mock.return_value)

    @return_value.setter
    def return_value(self, value: R) -> None:
        """Sets the value to return when the Mock is called.

        Type checkers validate against the original method's return type R.

        Args:
            value: The return value to set (type R).
        """
        self._mock.return_value = value

    @property
    def side_effect(self) -> Callable[P, R] | BaseException | list[Any] | None:
        """Side effect to raise when the Mock is called.

        - Callable: Function to execute when called (original signature P -> R).
        - Exception: Exception to raise when called.
        - list: List of values to return sequentially.
        - None: No side effect (use return_value).
        """
        return self._mock.side_effect  # type: ignore[no-any-return]

    @side_effect.setter
    def side_effect(
        self, value: Callable[P, R] | BaseException | list[Any] | None
    ) -> None:
        """Sets the side effect to raise when the Mock is called.

        Args:
            value: The side effect (function, exception, list of values, or None).
        """
        self._mock.side_effect = value

    @property
    def call_count(self) -> int:
        """Number of times the Mock was called."""
        return cast("int", self._mock.call_count)

    @property
    def called(self) -> bool:
        """Whether the Mock was called at least once."""
        return cast("bool", self._mock.called)

    @property
    def call_args(self) -> Any:
        """Arguments of the last call. None if never called."""
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """List of arguments for all calls."""
        result: list[Any] = list(self._mock.call_args_list)
        return result

    # =========================================================================
    # Attribute access delegation
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """Delegates undefined attributes to the internal Mock.

        Args:
            name: Attribute name.

        Returns:
            The corresponding attribute from the internal Mock.
        """
        return getattr(self._mock, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Delegates attribute setting to the internal Mock or this instance.

        Args:
            name: Attribute name.
            value: Value to set.
        """
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)


class MockedStaticMethod(Generic[P, R]):
    """Mock wrapper for static methods.

    Preserves the static method signature (no self/cls).

    Usage:
        >>> from unittest.mock import MagicMock
        >>> mock = MagicMock()
        >>> method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)
        >>> method.return_value = True
        >>> result = method("test@example.com")  # Type-checked!

    Note:
        This class is typically not used directly,
        but is automatically created through TypedMock[T].
    """

    __slots__ = ("_mock",)

    def __init__(self, mock: MagicMock) -> None:
        """Creates a MockedStaticMethod instance.

        Args:
            mock: The MagicMock instance to wrap.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Callable interface
    # =========================================================================

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls with the same signature as the original static method.

        Args:
            *args: Positional arguments of the original method.
            **kwargs: Keyword arguments of the original method.

        Returns:
            The Mock's return_value or side_effect result.
        """
        return self._mock(*args, **kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Assertion methods
    # =========================================================================

    def assert_called(self) -> None:
        """Verifies that the Mock was called at least once.

        Raises:
            AssertionError: If never called.
        """
        self._mock.assert_called()

    def assert_called_once(self) -> None:
        """Verifies that the Mock was called exactly once.

        Raises:
            AssertionError: If call count is not 1.
        """
        self._mock.assert_called_once()

    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called with the specified arguments (last call).

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments (original method signature).
            **kwargs: Expected keyword arguments (original method signature).

        Raises:
            AssertionError: If the last call's arguments don't match.
        """
        self._mock.assert_called_with(*args, **kwargs)

    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called exactly once with the specified arguments.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments (original method signature).
            **kwargs: Expected keyword arguments (original method signature).

        Raises:
            AssertionError: If call count is not 1 or arguments don't match.
        """
        self._mock.assert_called_once_with(*args, **kwargs)

    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called with the specified arguments at least once.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments (original method signature).
            **kwargs: Expected keyword arguments (original method signature).

        Raises:
            AssertionError: If never called with those arguments.
        """
        self._mock.assert_any_call(*args, **kwargs)

    def assert_not_called(self) -> None:
        """Verifies that the Mock was never called.

        Raises:
            AssertionError: If called at least once.
        """
        self._mock.assert_not_called()

    def assert_has_calls(
        self,
        calls: list[Any],
        any_order: bool = False,
    ) -> None:
        """Verifies that the Mock was called with the specified list of calls.

        Args:
            calls: Expected list of calls (unittest.mock.call objects).
            any_order: If True, order is ignored; if False, order must match.

        Raises:
            AssertionError: If the call list doesn't match.
        """
        self._mock.assert_has_calls(calls, any_order=any_order)

    def reset_mock(
        self,
        *,
        return_value: bool = False,
        side_effect: bool = False,
    ) -> None:
        """Resets the Mock's call history.

        Args:
            return_value: If True, also resets return_value.
            side_effect: If True, also resets side_effect.
        """
        self._mock.reset_mock(return_value=return_value, side_effect=side_effect)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Value to return when the Mock is called.

        Type checkers recognize the original method's return type R.
        """
        return cast("R", self._mock.return_value)

    @return_value.setter
    def return_value(self, value: R) -> None:
        """Sets the value to return when the Mock is called.

        Type checkers validate against the original method's return type R.

        Args:
            value: The return value to set (type R).
        """
        self._mock.return_value = value

    @property
    def side_effect(self) -> Callable[P, R] | BaseException | list[Any] | None:
        """Side effect to raise when the Mock is called.

        - Callable: Function to execute when called (original signature P -> R).
        - Exception: Exception to raise when called.
        - list: List of values to return sequentially.
        - None: No side effect (use return_value).
        """
        return self._mock.side_effect  # type: ignore[no-any-return]

    @side_effect.setter
    def side_effect(
        self, value: Callable[P, R] | BaseException | list[Any] | None
    ) -> None:
        """Sets the side effect to raise when the Mock is called.

        Args:
            value: The side effect (function, exception, list of values, or None).
        """
        self._mock.side_effect = value

    @property
    def call_count(self) -> int:
        """Number of times the Mock was called."""
        return cast("int", self._mock.call_count)

    @property
    def called(self) -> bool:
        """Whether the Mock was called at least once."""
        return cast("bool", self._mock.called)

    @property
    def call_args(self) -> Any:
        """Arguments of the last call. None if never called."""
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """List of arguments for all calls."""
        result: list[Any] = list(self._mock.call_args_list)
        return result

    # =========================================================================
    # Attribute access delegation
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """Delegates undefined attributes to the internal Mock.

        Args:
            name: Attribute name.

        Returns:
            The corresponding attribute from the internal Mock.
        """
        return getattr(self._mock, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Delegates attribute setting to the internal Mock or this instance.

        Args:
            name: Attribute name.
            value: Value to set.
        """
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)

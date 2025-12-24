"""
MockedMethod generic class.

Provides Mock functionality while preserving the original method's signature
(ParamSpec P, return type R).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, ParamSpec, TypeVar, cast


if TYPE_CHECKING:
    from collections.abc import Callable
    from unittest.mock import MagicMock


P = ParamSpec("P")
R = TypeVar("R")


class MockedMethod(Generic[P, R]):
    """Provides Mock functionality while preserving the original method's signature.

    To type checkers:
    - __call__: Same signature as original method (P.args, P.kwargs) -> R
    - assert_*: Validates with original parameter types
    - return_value: Original return type R

    At runtime, wraps MagicMock to provide actual Mock functionality.

    Example:
        >>> from unittest.mock import MagicMock
        >>> mock = MagicMock()
        >>> method: MockedMethod[[int], dict] = MockedMethod(mock)
        >>> method.return_value = {"id": 1}
        >>> method(1)
        {'id': 1}
        >>> method.assert_called_once_with(1)

    Note:
        This class is typically not used directly,
        but is automatically created through TypedMock[T].
    """

    __slots__ = ("_mock",)

    def __init__(self, mock: MagicMock) -> None:
        """Creates a MockedMethod instance.

        Args:
            mock: The MagicMock instance to wrap.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Callable interface
    # =========================================================================

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls with the same signature as the original method.

        Args:
            *args: Positional arguments of the original method.
            **kwargs: Keyword arguments of the original method.

        Returns:
            The Mock's return_value or side_effect result.
        """
        return self._mock(*args, **kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Assertion methods - preserving original signature
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

    # =============================================================================
    # Async Assertion Methods - added for compatibility with async Mocks
    # =============================================================================

    def assert_awaited(self) -> None:
        """Verifies that the Mock was awaited (async Mock compatibility).

        Always passes for sync Mocks.
        """
        if hasattr(self._mock, "assert_awaited"):
            self._mock.assert_awaited()

    def assert_awaited_once(self) -> None:
        """Verifies that the Mock was awaited exactly once (async Mock compatibility).

        Always passes for sync Mocks.
        """
        if hasattr(self._mock, "assert_awaited_once"):
            self._mock.assert_awaited_once()

    def assert_awaited_with(self, *args: Any, **kwargs: Any) -> None:
        """Verifies that the Mock was awaited with the specified arguments (async Mock compatibility).

        Always passes for sync Mocks.
        """
        if hasattr(self._mock, "assert_awaited_with"):
            self._mock.assert_awaited_with(*args, **kwargs)

    def assert_awaited_once_with(self, *args: Any, **kwargs: Any) -> None:
        """Verifies that the Mock was awaited exactly once with specified args (async Mock compatibility).

        Always passes for sync Mocks.
        """
        if hasattr(self._mock, "assert_awaited_once_with"):
            self._mock.assert_awaited_once_with(*args, **kwargs)

    def assert_has_awaits(self, calls: list[Any], any_order: bool = False) -> None:
        """Verifies that the Mock was awaited with the specified call list (async Mock compatibility).

        Always passes for sync Mocks.
        """
        if hasattr(self._mock, "assert_has_awaits"):
            self._mock.assert_has_awaits(calls, any_order=any_order)

    @property
    def await_count(self) -> int:
        """Number of times the Mock was awaited (async Mock compatibility).

        Returns 0 for sync Mocks.
        """
        return getattr(self._mock, "await_count", 0)

    @property
    def await_args(self) -> None:
        """Last await arguments (async Mock compatibility).

        Returns None for sync Mocks.
        """
        return getattr(self._mock, "await_args", None)

    @property
    def await_args_list(self) -> list[Any]:
        """List of all await arguments (async Mock compatibility).

        Returns an empty list for sync Mocks.
        """
        return getattr(self._mock, "await_args_list", [])

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
    # Properties - preserving original return type
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Value to return when the Mock is called.

        Type checkers recognize the original method's return type R.
        """
        return self._mock.return_value  # type: ignore[no-any-return]

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
        self,
        value: Callable[P, R] | BaseException | list[Any] | None,
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
        """Arguments of the last call. None if never called.

        The return value is a unittest.mock.call object.
        """
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """List of arguments for all calls.

        Each item is a unittest.mock.call object.
        """
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
        """Delegates attribute setting to the internal Mock.

        Args:
            name: Attribute name.
            value: Value to set.
        """
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)

    # =========================================================================
    # Type checking helpers
    # =========================================================================

    if TYPE_CHECKING:
        # Only visible to type checkers
        # At runtime, handled by __getattr__
        @property
        def configure_mock(self) -> Callable[..., None]:
            """Mock configuration method."""
            ...

        @property
        def mock_calls(self) -> list[Any]:
            """List of all Mock calls."""
            ...

        @property
        def method_calls(self) -> list[Any]:
            """List of method calls."""
            ...


class AsyncMockedMethod(Generic[P, R]):
    """MockedMethod for async methods.

    Provides the same interface as MockedMethod,
    and includes additional async-specific assertion methods.

    Example:
        >>> from unittest.mock import AsyncMock
        >>> mock = AsyncMock()
        >>> method: AsyncMockedMethod[[int], dict] = AsyncMockedMethod(mock)
        >>> method.return_value = {"id": 1}
        >>> import asyncio
        >>> asyncio.run(method(1))
        {'id': 1}
        >>> method.assert_awaited_once_with(1)
    """

    __slots__ = ("_mock",)

    def __init__(self, mock: MagicMock) -> None:
        """Creates an AsyncMockedMethod instance.

        Args:
            mock: The AsyncMock instance to wrap.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Callable interface (async)
    # =========================================================================

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Calls with the same signature as the original async method.

        Args:
            *args: Positional arguments of the original method.
            **kwargs: Keyword arguments of the original method.

        Returns:
            The Mock's return_value or side_effect result.
        """
        return await self._mock(*args, **kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Standard assertion methods (inherited behavior)
    # =========================================================================

    def assert_called(self) -> None:
        """Verifies that the Mock was called at least once."""
        self._mock.assert_called()

    def assert_called_once(self) -> None:
        """Verifies that the Mock was called exactly once."""
        self._mock.assert_called_once()

    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called with the specified arguments."""
        self._mock.assert_called_with(*args, **kwargs)

    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called exactly once with the specified arguments."""
        self._mock.assert_called_once_with(*args, **kwargs)

    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was called with the specified arguments at least once."""
        self._mock.assert_any_call(*args, **kwargs)

    def assert_not_called(self) -> None:
        """Verifies that the Mock was never called."""
        self._mock.assert_not_called()

    def reset_mock(
        self,
        *,
        return_value: bool = False,
        side_effect: bool = False,
    ) -> None:
        """Resets the Mock's call history."""
        self._mock.reset_mock(return_value=return_value, side_effect=side_effect)

    # =========================================================================
    # Async-specific assertion methods
    # =========================================================================

    def assert_awaited(self) -> None:
        """Verifies that the Mock was awaited at least once.

        Raises:
            AssertionError: If never awaited.
        """
        self._mock.assert_awaited()

    def assert_awaited_once(self) -> None:
        """Verifies that the Mock was awaited exactly once.

        Raises:
            AssertionError: If await count is not 1.
        """
        self._mock.assert_awaited_once()

    def assert_awaited_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was awaited with the specified arguments.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If the last await arguments don't match.
        """
        self._mock.assert_awaited_with(*args, **kwargs)

    def assert_awaited_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was awaited exactly once with specified arguments.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If await count is not 1 or arguments don't match.
        """
        self._mock.assert_awaited_once_with(*args, **kwargs)

    def assert_any_await(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Verifies that the Mock was awaited with the specified arguments at least once.

        Type checkers validate against the original method's parameter types.

        Args:
            *args: Expected positional arguments.
            **kwargs: Expected keyword arguments.

        Raises:
            AssertionError: If never awaited with those arguments.
        """
        self._mock.assert_any_await(*args, **kwargs)

    def assert_not_awaited(self) -> None:
        """Verifies that the Mock was never awaited.

        Raises:
            AssertionError: If awaited at least once.
        """
        self._mock.assert_not_awaited()

    def assert_has_awaits(
        self,
        calls: list[Any],
        any_order: bool = False,
    ) -> None:
        """Verifies that the Mock was awaited with the specified await list.

        Args:
            calls: Expected await list.
            any_order: If True, order is ignored.

        Raises:
            AssertionError: If the await list doesn't match.
        """
        self._mock.assert_has_awaits(calls, any_order=any_order)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Value to return when the Mock is called."""
        return self._mock.return_value  # type: ignore[no-any-return]

    @return_value.setter
    def return_value(self, value: R) -> None:
        """Sets the value to return when the Mock is called."""
        self._mock.return_value = value

    @property
    def side_effect(self) -> Callable[P, R] | BaseException | list[Any] | None:
        """Side effect to raise when the Mock is called."""
        return self._mock.side_effect  # type: ignore[no-any-return]

    @side_effect.setter
    def side_effect(
        self,
        value: Callable[P, R] | BaseException | list[Any] | None,
    ) -> None:
        """Sets the side effect to raise when the Mock is called."""
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
        """Arguments of the last call."""
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """List of arguments for all calls."""
        return list(self._mock.call_args_list)

    @property
    def await_count(self) -> int:
        """Number of times the Mock was awaited."""
        return cast("int", self._mock.await_count)

    @property
    def await_args(self) -> Any:
        """Arguments of the last await."""
        return cast("Any", self._mock.await_args)

    @property
    def await_args_list(self) -> list[Any]:
        """List of arguments for all awaits."""
        result: list[Any] = list(self._mock.await_args_list)
        return result

    # =========================================================================
    # Attribute access delegation
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """Delegates undefined attributes to the internal Mock."""
        return getattr(self._mock, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Delegates attribute setting to the internal Mock."""
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)

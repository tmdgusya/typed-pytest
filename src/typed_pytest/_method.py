"""
MockedMethod 제네릭 클래스.

원본 메소드의 시그니처(ParamSpec P, 반환 타입 R)를 보존하면서
Mock 기능을 제공하는 클래스입니다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, ParamSpec, TypeVar, cast


if TYPE_CHECKING:
    from collections.abc import Callable
    from unittest.mock import MagicMock


P = ParamSpec("P")
R = TypeVar("R")


class MockedMethod(Generic[P, R]):
    """원본 메소드의 시그니처를 보존하면서 Mock 기능을 제공하는 클래스.

    타입 체커에게:
    - __call__: 원본 메소드와 동일한 시그니처 (P.args, P.kwargs) -> R
    - assert_*: 원본 파라미터 타입으로 검증
    - return_value: 원본 반환 타입 R

    런타임에서는 MagicMock을 래핑하여 실제 Mock 기능을 제공합니다.

    Example:
        >>> from unittest.mock import MagicMock
        >>> mock = MagicMock()
        >>> method: MockedMethod[[int], dict] = MockedMethod(mock)
        >>> method.return_value = {"id": 1}
        >>> method(1)
        {'id': 1}
        >>> method.assert_called_once_with(1)

    Note:
        이 클래스는 일반적으로 직접 사용하지 않고,
        TypedMock[T]를 통해 자동으로 생성됩니다.
    """

    __slots__ = ("_mock",)

    def __init__(self, mock: MagicMock) -> None:
        """MockedMethod 인스턴스를 생성합니다.

        Args:
            mock: 래핑할 MagicMock 인스턴스.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Callable interface
    # =========================================================================

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """원본 메소드와 동일한 시그니처로 호출합니다.

        Args:
            *args: 원본 메소드의 위치 인자.
            **kwargs: 원본 메소드의 키워드 인자.

        Returns:
            Mock의 return_value 또는 side_effect 결과.
        """
        return self._mock(*args, **kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Assertion methods - 원본 시그니처 보존
    # =========================================================================

    def assert_called(self) -> None:
        """Mock이 한 번 이상 호출되었는지 확인.

        Raises:
            AssertionError: 한 번도 호출되지 않은 경우.
        """
        self._mock.assert_called()

    def assert_called_once(self) -> None:
        """Mock이 정확히 한 번 호출되었는지 확인.

        Raises:
            AssertionError: 호출 횟수가 1이 아닌 경우.
        """
        self._mock.assert_called_once()

    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 지정된 인자로 호출되었는지 확인 (마지막 호출 기준).

        타입 체커는 원본 메소드의 파라미터 타입을 검사합니다.

        Args:
            *args: 예상되는 위치 인자 (원본 메소드 시그니처).
            **kwargs: 예상되는 키워드 인자 (원본 메소드 시그니처).

        Raises:
            AssertionError: 마지막 호출 인자가 일치하지 않는 경우.
        """
        self._mock.assert_called_with(*args, **kwargs)

    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 정확히 한 번, 지정된 인자로 호출되었는지 확인.

        타입 체커는 원본 메소드의 파라미터 타입을 검사합니다.

        Args:
            *args: 예상되는 위치 인자 (원본 메소드 시그니처).
            **kwargs: 예상되는 키워드 인자 (원본 메소드 시그니처).

        Raises:
            AssertionError: 호출 횟수가 1이 아니거나 인자가 일치하지 않는 경우.
        """
        self._mock.assert_called_once_with(*args, **kwargs)

    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 지정된 인자로 한 번이라도 호출되었는지 확인.

        타입 체커는 원본 메소드의 파라미터 타입을 검사합니다.

        Args:
            *args: 예상되는 위치 인자 (원본 메소드 시그니처).
            **kwargs: 예상되는 키워드 인자 (원본 메소드 시그니처).

        Raises:
            AssertionError: 해당 인자로 호출된 적이 없는 경우.
        """
        self._mock.assert_any_call(*args, **kwargs)

    def assert_not_called(self) -> None:
        """Mock이 호출되지 않았는지 확인.

        Raises:
            AssertionError: 한 번이라도 호출된 경우.
        """
        self._mock.assert_not_called()

    def assert_has_calls(
        self,
        calls: list[Any],
        any_order: bool = False,
    ) -> None:
        """Mock이 지정된 호출 목록대로 호출되었는지 확인.

        Args:
            calls: 예상되는 호출 목록 (unittest.mock.call 객체들).
            any_order: True면 순서 무시, False면 순서 일치 필요.

        Raises:
            AssertionError: 호출 목록이 일치하지 않는 경우.
        """
        self._mock.assert_has_calls(calls, any_order=any_order)

    def reset_mock(
        self,
        *,
        return_value: bool = False,
        side_effect: bool = False,
    ) -> None:
        """Mock의 호출 기록을 초기화.

        Args:
            return_value: True면 return_value도 초기화.
            side_effect: True면 side_effect도 초기화.
        """
        self._mock.reset_mock(return_value=return_value, side_effect=side_effect)

    # =========================================================================
    # Properties - 원본 반환 타입 보존
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Mock 호출 시 반환할 값.

        타입 체커는 원본 메소드의 반환 타입 R을 인식합니다.
        """
        return self._mock.return_value  # type: ignore[no-any-return]

    @return_value.setter
    def return_value(self, value: R) -> None:
        """Mock 호출 시 반환할 값 설정.

        타입 체커는 원본 메소드의 반환 타입 R을 검사합니다.

        Args:
            value: 설정할 반환 값 (타입 R).
        """
        self._mock.return_value = value

    @property
    def side_effect(self) -> Callable[P, R] | BaseException | list[Any] | None:
        """Mock 호출 시 발생시킬 부수 효과.

        - Callable: 호출 시 실행될 함수 (원본 시그니처 P -> R).
        - Exception: 호출 시 발생시킬 예외.
        - list: 순차적으로 반환할 값들의 리스트.
        - None: 부수 효과 없음 (return_value 사용).
        """
        return self._mock.side_effect  # type: ignore[no-any-return]

    @side_effect.setter
    def side_effect(
        self,
        value: Callable[P, R] | BaseException | list[Any] | None,
    ) -> None:
        """Mock 호출 시 발생시킬 부수 효과 설정.

        Args:
            value: 부수 효과 (함수, 예외, 값 리스트, 또는 None).
        """
        self._mock.side_effect = value

    @property
    def call_count(self) -> int:
        """Mock이 호출된 횟수."""
        return cast("int", self._mock.call_count)

    @property
    def called(self) -> bool:
        """Mock이 한 번 이상 호출되었는지 여부."""
        return cast("bool", self._mock.called)

    @property
    def call_args(self) -> Any:
        """마지막 호출의 인자. 호출된 적 없으면 None.

        반환값은 unittest.mock.call 객체입니다.
        """
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """모든 호출의 인자 목록.

        각 항목은 unittest.mock.call 객체입니다.
        """
        result: list[Any] = list(self._mock.call_args_list)
        return result

    # =========================================================================
    # Attribute access delegation
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """정의되지 않은 속성은 내부 Mock으로 위임합니다.

        Args:
            name: 속성 이름.

        Returns:
            내부 Mock의 해당 속성.
        """
        return getattr(self._mock, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """속성 설정을 내부 Mock으로 위임합니다.

        Args:
            name: 속성 이름.
            value: 설정할 값.
        """
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)

    # =========================================================================
    # Type checking helpers
    # =========================================================================

    if TYPE_CHECKING:
        # 타입 체커에게만 보이는 정의
        # 런타임에서는 __getattr__로 처리됨
        @property
        def configure_mock(self) -> Callable[..., None]:
            """Mock 설정 메소드."""
            ...

        @property
        def mock_calls(self) -> list[Any]:
            """모든 Mock 호출 목록."""
            ...

        @property
        def method_calls(self) -> list[Any]:
            """메소드 호출 목록."""
            ...


class AsyncMockedMethod(Generic[P, R]):
    """비동기 메소드를 위한 MockedMethod.

    MockedMethod와 동일한 인터페이스를 제공하며,
    추가로 비동기 전용 assertion 메소드를 포함합니다.

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
        """AsyncMockedMethod 인스턴스를 생성합니다.

        Args:
            mock: 래핑할 AsyncMock 인스턴스.
        """
        object.__setattr__(self, "_mock", mock)

    # =========================================================================
    # Callable interface (async)
    # =========================================================================

    async def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """원본 비동기 메소드와 동일한 시그니처로 호출합니다.

        Args:
            *args: 원본 메소드의 위치 인자.
            **kwargs: 원본 메소드의 키워드 인자.

        Returns:
            Mock의 return_value 또는 side_effect 결과.
        """
        return await self._mock(*args, **kwargs)  # type: ignore[no-any-return]

    # =========================================================================
    # Standard assertion methods (inherited behavior)
    # =========================================================================

    def assert_called(self) -> None:
        """Mock이 한 번 이상 호출되었는지 확인."""
        self._mock.assert_called()

    def assert_called_once(self) -> None:
        """Mock이 정확히 한 번 호출되었는지 확인."""
        self._mock.assert_called_once()

    def assert_called_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 지정된 인자로 호출되었는지 확인."""
        self._mock.assert_called_with(*args, **kwargs)

    def assert_called_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 정확히 한 번, 지정된 인자로 호출되었는지 확인."""
        self._mock.assert_called_once_with(*args, **kwargs)

    def assert_any_call(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 지정된 인자로 한 번이라도 호출되었는지 확인."""
        self._mock.assert_any_call(*args, **kwargs)

    def assert_not_called(self) -> None:
        """Mock이 호출되지 않았는지 확인."""
        self._mock.assert_not_called()

    def reset_mock(
        self,
        *,
        return_value: bool = False,
        side_effect: bool = False,
    ) -> None:
        """Mock의 호출 기록을 초기화."""
        self._mock.reset_mock(return_value=return_value, side_effect=side_effect)

    # =========================================================================
    # Async-specific assertion methods
    # =========================================================================

    def assert_awaited(self) -> None:
        """Mock이 한 번 이상 await되었는지 확인.

        Raises:
            AssertionError: 한 번도 await되지 않은 경우.
        """
        self._mock.assert_awaited()

    def assert_awaited_once(self) -> None:
        """Mock이 정확히 한 번 await되었는지 확인.

        Raises:
            AssertionError: await 횟수가 1이 아닌 경우.
        """
        self._mock.assert_awaited_once()

    def assert_awaited_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 지정된 인자로 await되었는지 확인.

        타입 체커는 원본 메소드의 파라미터 타입을 검사합니다.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 마지막 await 인자가 일치하지 않는 경우.
        """
        self._mock.assert_awaited_with(*args, **kwargs)

    def assert_awaited_once_with(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 정확히 한 번, 지정된 인자로 await되었는지 확인.

        타입 체커는 원본 메소드의 파라미터 타입을 검사합니다.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: await 횟수가 1이 아니거나 인자가 일치하지 않는 경우.
        """
        self._mock.assert_awaited_once_with(*args, **kwargs)

    def assert_any_await(self, *args: P.args, **kwargs: P.kwargs) -> None:
        """Mock이 지정된 인자로 한 번이라도 await되었는지 확인.

        타입 체커는 원본 메소드의 파라미터 타입을 검사합니다.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 해당 인자로 await된 적이 없는 경우.
        """
        self._mock.assert_any_await(*args, **kwargs)

    def assert_not_awaited(self) -> None:
        """Mock이 await되지 않았는지 확인.

        Raises:
            AssertionError: 한 번이라도 await된 경우.
        """
        self._mock.assert_not_awaited()

    def assert_has_awaits(
        self,
        calls: list[Any],
        any_order: bool = False,
    ) -> None:
        """Mock이 지정된 await 목록대로 await되었는지 확인.

        Args:
            calls: 예상되는 await 목록.
            any_order: True면 순서 무시.

        Raises:
            AssertionError: await 목록이 일치하지 않는 경우.
        """
        self._mock.assert_has_awaits(calls, any_order=any_order)

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def return_value(self) -> R:
        """Mock 호출 시 반환할 값."""
        return self._mock.return_value  # type: ignore[no-any-return]

    @return_value.setter
    def return_value(self, value: R) -> None:
        """Mock 호출 시 반환할 값 설정."""
        self._mock.return_value = value

    @property
    def side_effect(self) -> Callable[P, R] | BaseException | list[Any] | None:
        """Mock 호출 시 발생시킬 부수 효과."""
        return self._mock.side_effect  # type: ignore[no-any-return]

    @side_effect.setter
    def side_effect(
        self,
        value: Callable[P, R] | BaseException | list[Any] | None,
    ) -> None:
        """Mock 호출 시 발생시킬 부수 효과 설정."""
        self._mock.side_effect = value

    @property
    def call_count(self) -> int:
        """Mock이 호출된 횟수."""
        return cast("int", self._mock.call_count)

    @property
    def called(self) -> bool:
        """Mock이 한 번 이상 호출되었는지 여부."""
        return cast("bool", self._mock.called)

    @property
    def call_args(self) -> Any:
        """마지막 호출의 인자."""
        return cast("Any", self._mock.call_args)

    @property
    def call_args_list(self) -> list[Any]:
        """모든 호출의 인자 목록."""
        return list(self._mock.call_args_list)

    @property
    def await_count(self) -> int:
        """Mock이 await된 횟수."""
        return cast("int", self._mock.await_count)

    @property
    def await_args(self) -> Any:
        """마지막 await의 인자."""
        return cast("Any", self._mock.await_args)

    @property
    def await_args_list(self) -> list[Any]:
        """모든 await의 인자 목록."""
        result: list[Any] = list(self._mock.await_args_list)
        return result

    # =========================================================================
    # Attribute access delegation
    # =========================================================================

    def __getattr__(self, name: str) -> Any:
        """정의되지 않은 속성은 내부 Mock으로 위임합니다."""
        return getattr(self._mock, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """속성 설정을 내부 Mock으로 위임합니다."""
        if name == "_mock":
            object.__setattr__(self, name, value)
        else:
            setattr(self._mock, name, value)

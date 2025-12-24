"""
Mock 객체의 Protocol 정의.

이 모듈은 Mock 객체가 구현해야 하는 인터페이스를 Protocol로 정의합니다.
unittest.mock.MagicMock이 이 Protocol을 만족하도록 설계되었습니다.
"""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MockProtocol(Protocol):
    """Mock 객체가 구현해야 하는 프로토콜.

    unittest.mock.MagicMock과 AsyncMock이 이 Protocol을 만족합니다.
    이 Protocol은 타입 체커가 Mock 객체의 메소드와 속성을 인식하도록 합니다.

    Example:
        >>> from unittest.mock import MagicMock
        >>> mock = MagicMock()
        >>> isinstance(mock, MockProtocol)
        True
    """

    # =========================================================================
    # Assertion methods
    # =========================================================================

    def assert_called(self) -> None:
        """Mock이 한 번 이상 호출되었는지 확인.

        Raises:
            AssertionError: 한 번도 호출되지 않은 경우.
        """
        ...

    def assert_called_once(self) -> None:
        """Mock이 정확히 한 번 호출되었는지 확인.

        Raises:
            AssertionError: 호출 횟수가 1이 아닌 경우.
        """
        ...

    def assert_called_with(self, *args: Any, **kwargs: Any) -> None:
        """Mock이 지정된 인자로 호출되었는지 확인 (마지막 호출 기준).

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 마지막 호출 인자가 일치하지 않는 경우.
        """
        ...

    def assert_called_once_with(self, *args: Any, **kwargs: Any) -> None:
        """Mock이 정확히 한 번, 지정된 인자로 호출되었는지 확인.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 호출 횟수가 1이 아니거나 인자가 일치하지 않는 경우.
        """
        ...

    def assert_any_call(self, *args: Any, **kwargs: Any) -> None:
        """Mock이 지정된 인자로 한 번이라도 호출되었는지 확인.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 해당 인자로 호출된 적이 없는 경우.
        """
        ...

    def assert_not_called(self) -> None:
        """Mock이 호출되지 않았는지 확인.

        Raises:
            AssertionError: 한 번이라도 호출된 경우.
        """
        ...

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
        ...

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
        ...

    # =========================================================================
    # Properties
    # =========================================================================

    @property
    def return_value(self) -> Any:
        """Mock 호출 시 반환할 값."""
        ...

    @return_value.setter
    def return_value(self, value: Any) -> None:
        """Mock 호출 시 반환할 값 설정."""
        ...

    @property
    def side_effect(self) -> Any:
        """Mock 호출 시 발생시킬 부수 효과 (예외 또는 콜백)."""
        ...

    @side_effect.setter
    def side_effect(self, value: Any) -> None:
        """Mock 호출 시 발생시킬 부수 효과 설정."""
        ...

    @property
    def call_count(self) -> int:
        """Mock이 호출된 횟수."""
        ...

    @property
    def called(self) -> bool:
        """Mock이 한 번 이상 호출되었는지 여부."""
        ...

    @property
    def call_args(self) -> Any:
        """마지막 호출의 인자. 호출된 적 없으면 None."""
        ...

    @property
    def call_args_list(self) -> list[Any]:
        """모든 호출의 인자 목록."""
        ...

    @property
    def method_calls(self) -> list[Any]:
        """이 Mock의 메소드 호출 목록."""
        ...

    @property
    def mock_calls(self) -> list[Any]:
        """이 Mock과 자식 Mock의 모든 호출 목록."""
        ...


@runtime_checkable
class AsyncMockProtocol(MockProtocol, Protocol):
    """비동기 Mock 객체가 구현해야 하는 프로토콜.

    MockProtocol을 상속하며, 비동기 assertion 메소드를 추가합니다.

    Example:
        >>> from unittest.mock import AsyncMock
        >>> mock = AsyncMock()
        >>> isinstance(mock, AsyncMockProtocol)
        True
    """

    def assert_awaited(self) -> None:
        """Mock이 한 번 이상 await되었는지 확인.

        Raises:
            AssertionError: 한 번도 await되지 않은 경우.
        """
        ...

    def assert_awaited_once(self) -> None:
        """Mock이 정확히 한 번 await되었는지 확인.

        Raises:
            AssertionError: await 횟수가 1이 아닌 경우.
        """
        ...

    def assert_awaited_with(self, *args: Any, **kwargs: Any) -> None:
        """Mock이 지정된 인자로 await되었는지 확인 (마지막 await 기준).

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 마지막 await 인자가 일치하지 않는 경우.
        """
        ...

    def assert_awaited_once_with(self, *args: Any, **kwargs: Any) -> None:
        """Mock이 정확히 한 번, 지정된 인자로 await되었는지 확인.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: await 횟수가 1이 아니거나 인자가 일치하지 않는 경우.
        """
        ...

    def assert_any_await(self, *args: Any, **kwargs: Any) -> None:
        """Mock이 지정된 인자로 한 번이라도 await되었는지 확인.

        Args:
            *args: 예상되는 위치 인자.
            **kwargs: 예상되는 키워드 인자.

        Raises:
            AssertionError: 해당 인자로 await된 적이 없는 경우.
        """
        ...

    def assert_not_awaited(self) -> None:
        """Mock이 await되지 않았는지 확인.

        Raises:
            AssertionError: 한 번이라도 await된 경우.
        """
        ...

    def assert_has_awaits(
        self,
        calls: list[Any],
        any_order: bool = False,
    ) -> None:
        """Mock이 지정된 await 목록대로 await되었는지 확인.

        Args:
            calls: 예상되는 await 목록 (unittest.mock.call 객체들).
            any_order: True면 순서 무시, False면 순서 일치 필요.

        Raises:
            AssertionError: await 목록이 일치하지 않는 경우.
        """
        ...

    @property
    def await_count(self) -> int:
        """Mock이 await된 횟수."""
        ...

    @property
    def await_args(self) -> Any:
        """마지막 await의 인자. await된 적 없으면 None."""
        ...

    @property
    def await_args_list(self) -> list[Any]:
        """모든 await의 인자 목록."""
        ...

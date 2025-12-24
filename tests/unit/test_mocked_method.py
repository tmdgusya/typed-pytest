"""MockedMethod 및 AsyncMockedMethod 테스트."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock, call

import pytest

from typed_pytest._method import AsyncMockedMethod, MockedMethod


class TestMockedMethod:
    """MockedMethod 테스트."""

    def test_creation(self) -> None:
        """MockedMethod 인스턴스 생성."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)
        assert method is not None

    def test_call_preserves_signature(self) -> None:
        """MockedMethod 호출이 원본 시그니처를 따르는지."""
        mock = MagicMock()
        mock.return_value = {"id": 1, "name": "Test"}
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        result = method(1)

        assert result == {"id": 1, "name": "Test"}
        mock.assert_called_once_with(1)

    def test_call_with_kwargs(self) -> None:
        """키워드 인자로 호출."""
        mock = MagicMock()
        method: MockedMethod[..., dict[str, Any]] = MockedMethod(mock)

        method("John", email="john@example.com")

        mock.assert_called_once_with("John", email="john@example.com")

    def test_return_value_has_correct_type(self) -> None:
        """return_value가 원본 반환 타입을 가지는지."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method.return_value = {"id": 1}
        assert method.return_value == {"id": 1}

        result = method(1)
        assert result == {"id": 1}

    def test_side_effect_with_exception(self) -> None:
        """side_effect로 예외 설정."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method.side_effect = ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            method(1)

    def test_side_effect_with_values(self) -> None:
        """side_effect로 순차 값 설정."""
        mock = MagicMock()
        method: MockedMethod[[int], int] = MockedMethod(mock)

        method.side_effect = [1, 2, 3]

        assert method(1) == 1
        assert method(2) == 2
        assert method(3) == 3

    def test_side_effect_with_callable(self) -> None:
        """side_effect로 함수 설정."""
        mock = MagicMock()
        method: MockedMethod[[int], int] = MockedMethod(mock)

        method.side_effect = lambda x: x * 2

        assert method(5) == 10
        assert method(10) == 20

    def test_assert_called(self) -> None:
        """assert_called 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        with pytest.raises(AssertionError):
            method.assert_called()

        method(1)
        method.assert_called()

    def test_assert_called_once(self) -> None:
        """assert_called_once 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        with pytest.raises(AssertionError):
            method.assert_called_once()

        method(1)
        method.assert_called_once()

        method(2)
        with pytest.raises(AssertionError):
            method.assert_called_once()

    def test_assert_called_with_type_hints(self) -> None:
        """assert_called_with가 원본 파라미터 타입 힌트를 가지는지."""
        mock = MagicMock()
        method: MockedMethod[[int, str], dict[str, Any]] = MockedMethod(mock)

        method(1, "test")
        method.assert_called_with(1, "test")

        with pytest.raises(AssertionError):
            method.assert_called_with(2, "other")

    def test_assert_called_once_with(self) -> None:
        """assert_called_once_with 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method(1)
        method.assert_called_once_with(1)

    def test_assert_any_call(self) -> None:
        """assert_any_call 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method(1)
        method(2)
        method(3)

        method.assert_any_call(1)
        method.assert_any_call(2)
        method.assert_any_call(3)

        with pytest.raises(AssertionError):
            method.assert_any_call(4)

    def test_assert_not_called(self) -> None:
        """assert_not_called 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method.assert_not_called()

        method(1)
        with pytest.raises(AssertionError):
            method.assert_not_called()

    def test_assert_has_calls(self) -> None:
        """assert_has_calls 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method(1)
        method(2)

        method.assert_has_calls([call(1), call(2)])
        method.assert_has_calls([call(2), call(1)], any_order=True)

    def test_reset_mock(self) -> None:
        """reset_mock 메소드."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        method(1)
        assert method.call_count == 1

        method.reset_mock()
        assert method.call_count == 0

    def test_call_count_property(self) -> None:
        """call_count 속성."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        assert method.call_count == 0

        method(1)
        assert method.call_count == 1

        method(2)
        method(3)
        assert method.call_count == 3

    def test_called_property(self) -> None:
        """called 속성."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        assert method.called is False

        method(1)
        assert method.called is True

    def test_call_args_property(self) -> None:
        """call_args 속성."""
        mock = MagicMock()
        method: MockedMethod[[int, str], dict[str, Any]] = MockedMethod(mock)

        assert method.call_args is None

        method(1, "test")
        assert method.call_args == call(1, "test")

    def test_call_args_list_property(self) -> None:
        """call_args_list 속성."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        assert method.call_args_list == []

        method(1)
        method(2)
        assert method.call_args_list == [call(1), call(2)]

    def test_attribute_delegation(self) -> None:
        """속성 위임이 정상 동작하는지."""
        mock = MagicMock()
        method: MockedMethod[[int], dict[str, Any]] = MockedMethod(mock)

        # mock_calls는 MagicMock의 속성
        assert hasattr(method, "mock_calls")
        assert method.mock_calls == []


class TestAsyncMockedMethod:
    """AsyncMockedMethod 테스트."""

    def test_creation(self) -> None:
        """AsyncMockedMethod 인스턴스 생성."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)
        assert method is not None

    async def test_async_call(self) -> None:
        """비동기 호출."""
        mock = AsyncMock()
        mock.return_value = {"id": 1}
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        result = await method(1)

        assert result == {"id": 1}
        mock.assert_awaited_once_with(1)

    async def test_return_value(self) -> None:
        """return_value 속성."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        method.return_value = {"id": 42}
        result = await method(1)

        assert result == {"id": 42}

    async def test_side_effect_exception(self) -> None:
        """side_effect로 예외 설정."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        method.side_effect = ValueError("async error")

        with pytest.raises(ValueError, match="async error"):
            await method(1)

    async def test_side_effect_values(self) -> None:
        """side_effect로 순차 값 설정."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], int] = AsyncMockedMethod(mock)

        method.side_effect = [1, 2, 3]

        assert await method(1) == 1
        assert await method(2) == 2
        assert await method(3) == 3

    async def test_assert_awaited(self) -> None:
        """assert_awaited 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        with pytest.raises(AssertionError):
            method.assert_awaited()

        await method(1)
        method.assert_awaited()

    async def test_assert_awaited_once(self) -> None:
        """assert_awaited_once 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        with pytest.raises(AssertionError):
            method.assert_awaited_once()

        await method(1)
        method.assert_awaited_once()

        await method(2)
        with pytest.raises(AssertionError):
            method.assert_awaited_once()

    async def test_assert_awaited_with(self) -> None:
        """assert_awaited_with 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int, str], dict[str, Any]] = AsyncMockedMethod(mock)

        await method(1, "test")
        method.assert_awaited_with(1, "test")

        with pytest.raises(AssertionError):
            method.assert_awaited_with(2, "other")

    async def test_assert_awaited_once_with(self) -> None:
        """assert_awaited_once_with 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        await method(1)
        method.assert_awaited_once_with(1)

    async def test_assert_any_await(self) -> None:
        """assert_any_await 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        await method(1)
        await method(2)

        method.assert_any_await(1)
        method.assert_any_await(2)

        with pytest.raises(AssertionError):
            method.assert_any_await(3)

    async def test_assert_not_awaited(self) -> None:
        """assert_not_awaited 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        method.assert_not_awaited()

        await method(1)
        with pytest.raises(AssertionError):
            method.assert_not_awaited()

    async def test_assert_has_awaits(self) -> None:
        """assert_has_awaits 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        await method(1)
        await method(2)

        method.assert_has_awaits([call(1), call(2)])
        method.assert_has_awaits([call(2), call(1)], any_order=True)

    async def test_await_count_property(self) -> None:
        """await_count 속성."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        assert method.await_count == 0

        await method(1)
        assert method.await_count == 1

        await method(2)
        await method(3)
        assert method.await_count == 3

    async def test_await_args_property(self) -> None:
        """await_args 속성."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int, str], dict[str, Any]] = AsyncMockedMethod(mock)

        assert method.await_args is None

        await method(1, "test")
        assert method.await_args == call(1, "test")

    async def test_await_args_list_property(self) -> None:
        """await_args_list 속성."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        assert method.await_args_list == []

        await method(1)
        await method(2)
        assert method.await_args_list == [call(1), call(2)]

    async def test_standard_assertions_also_work(self) -> None:
        """일반 assertion 메소드도 동작하는지."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        method.assert_not_called()

        await method(1)
        method.assert_called()
        method.assert_called_once()
        method.assert_called_with(1)

    async def test_reset_mock(self) -> None:
        """reset_mock 메소드."""
        mock = AsyncMock()
        method: AsyncMockedMethod[[int], dict[str, Any]] = AsyncMockedMethod(mock)

        await method(1)
        assert method.call_count == 1

        method.reset_mock()
        assert method.call_count == 0

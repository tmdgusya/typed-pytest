"""MockProtocol 및 AsyncMockProtocol 테스트."""

from unittest.mock import AsyncMock, MagicMock, call

import pytest

from typed_pytest._protocols import AsyncMockProtocol, MockProtocol


class TestMockProtocol:
    """MockProtocol 테스트."""

    def test_magicmock_satisfies_protocol(self) -> None:
        """MagicMock이 MockProtocol을 만족하는지 확인."""
        mock = MagicMock()
        assert isinstance(mock, MockProtocol)

    def test_protocol_has_assertion_methods(self) -> None:
        """Protocol에 모든 assertion 메소드가 정의되어 있는지 확인."""
        assertion_methods = [
            "assert_called",
            "assert_called_once",
            "assert_called_with",
            "assert_called_once_with",
            "assert_any_call",
            "assert_not_called",
            "assert_has_calls",
            "reset_mock",
        ]
        mock = MagicMock()
        for method_name in assertion_methods:
            assert hasattr(mock, method_name), f"Missing method: {method_name}"

    def test_protocol_has_properties(self) -> None:
        """Protocol에 모든 속성이 정의되어 있는지 확인."""
        properties = [
            "return_value",
            "side_effect",
            "call_count",
            "called",
            "call_args",
            "call_args_list",
            "method_calls",
            "mock_calls",
        ]
        mock = MagicMock()
        for prop_name in properties:
            assert hasattr(mock, prop_name), f"Missing property: {prop_name}"

    def test_assert_called_works(self) -> None:
        """assert_called 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()

        with pytest.raises(AssertionError):
            mock.assert_called()

        mock()
        mock.assert_called()

    def test_assert_called_once_works(self) -> None:
        """assert_called_once 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()

        with pytest.raises(AssertionError):
            mock.assert_called_once()

        mock()
        mock.assert_called_once()

        mock()
        with pytest.raises(AssertionError):
            mock.assert_called_once()

    def test_assert_called_with_works(self) -> None:
        """assert_called_with 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()
        mock(1, 2, key="value")

        mock.assert_called_with(1, 2, key="value")

        with pytest.raises(AssertionError):
            mock.assert_called_with(3, 4)

    def test_assert_called_once_with_works(self) -> None:
        """assert_called_once_with 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()
        mock(1, 2)

        mock.assert_called_once_with(1, 2)

        mock(1, 2)
        with pytest.raises(AssertionError):
            mock.assert_called_once_with(1, 2)

    def test_assert_any_call_works(self) -> None:
        """assert_any_call 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()
        mock(1)
        mock(2)
        mock(3)

        mock.assert_any_call(1)
        mock.assert_any_call(2)
        mock.assert_any_call(3)

        with pytest.raises(AssertionError):
            mock.assert_any_call(4)

    def test_assert_not_called_works(self) -> None:
        """assert_not_called 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()
        mock.assert_not_called()

        mock()
        with pytest.raises(AssertionError):
            mock.assert_not_called()

    def test_assert_has_calls_works(self) -> None:
        """assert_has_calls 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()
        mock(1)
        mock(2)

        mock.assert_has_calls([call(1), call(2)])
        mock.assert_has_calls([call(2), call(1)], any_order=True)

        with pytest.raises(AssertionError):
            mock.assert_has_calls([call(3)])

    def test_reset_mock_works(self) -> None:
        """reset_mock 메소드가 정상 동작하는지 확인."""
        mock = MagicMock()
        mock(1)
        assert mock.call_count == 1

        mock.reset_mock()
        assert mock.call_count == 0

    def test_return_value_property(self) -> None:
        """return_value 속성이 정상 동작하는지 확인."""
        mock = MagicMock()
        mock.return_value = 42

        assert mock() == 42

    def test_side_effect_property_with_exception(self) -> None:
        """side_effect 속성으로 예외를 설정할 수 있는지 확인."""
        mock = MagicMock()
        mock.side_effect = ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            mock()

    def test_side_effect_property_with_values(self) -> None:
        """side_effect 속성으로 순차 값을 설정할 수 있는지 확인."""
        mock = MagicMock()
        mock.side_effect = [1, 2, 3]

        assert mock() == 1
        assert mock() == 2
        assert mock() == 3

    def test_call_count_property(self) -> None:
        """call_count 속성이 정상 동작하는지 확인."""
        mock = MagicMock()
        assert mock.call_count == 0

        mock()
        assert mock.call_count == 1

        mock()
        mock()
        assert mock.call_count == 3

    def test_called_property(self) -> None:
        """called 속성이 정상 동작하는지 확인."""
        mock = MagicMock()
        assert mock.called is False

        mock()
        assert mock.called is True

    def test_call_args_property(self) -> None:
        """call_args 속성이 정상 동작하는지 확인."""
        mock = MagicMock()
        assert mock.call_args is None

        mock(1, 2, key="value")
        assert mock.call_args == call(1, 2, key="value")

    def test_call_args_list_property(self) -> None:
        """call_args_list 속성이 정상 동작하는지 확인."""
        mock = MagicMock()
        assert mock.call_args_list == []

        mock(1)
        mock(2)
        assert mock.call_args_list == [call(1), call(2)]


class TestAsyncMockProtocol:
    """AsyncMockProtocol 테스트."""

    def test_asyncmock_satisfies_protocol(self) -> None:
        """AsyncMock이 AsyncMockProtocol을 만족하는지 확인."""
        mock = AsyncMock()
        assert isinstance(mock, AsyncMockProtocol)

    def test_asyncmock_also_satisfies_mock_protocol(self) -> None:
        """AsyncMock이 MockProtocol도 만족하는지 확인."""
        mock = AsyncMock()
        assert isinstance(mock, MockProtocol)

    def test_protocol_has_async_assertion_methods(self) -> None:
        """Protocol에 모든 비동기 assertion 메소드가 정의되어 있는지 확인."""
        async_assertion_methods = [
            "assert_awaited",
            "assert_awaited_once",
            "assert_awaited_with",
            "assert_awaited_once_with",
            "assert_any_await",
            "assert_not_awaited",
            "assert_has_awaits",
        ]
        mock = AsyncMock()
        for method_name in async_assertion_methods:
            assert hasattr(mock, method_name), f"Missing method: {method_name}"

    def test_protocol_has_async_properties(self) -> None:
        """Protocol에 모든 비동기 속성이 정의되어 있는지 확인."""
        async_properties = [
            "await_count",
            "await_args",
            "await_args_list",
        ]
        mock = AsyncMock()
        for prop_name in async_properties:
            assert hasattr(mock, prop_name), f"Missing property: {prop_name}"

    async def test_assert_awaited_works(self) -> None:
        """assert_awaited 메소드가 정상 동작하는지 확인."""
        mock = AsyncMock()

        with pytest.raises(AssertionError):
            mock.assert_awaited()

        await mock()
        mock.assert_awaited()

    async def test_assert_awaited_once_works(self) -> None:
        """assert_awaited_once 메소드가 정상 동작하는지 확인."""
        mock = AsyncMock()

        with pytest.raises(AssertionError):
            mock.assert_awaited_once()

        await mock()
        mock.assert_awaited_once()

        await mock()
        with pytest.raises(AssertionError):
            mock.assert_awaited_once()

    async def test_assert_awaited_with_works(self) -> None:
        """assert_awaited_with 메소드가 정상 동작하는지 확인."""
        mock = AsyncMock()
        await mock(1, 2, key="value")

        mock.assert_awaited_with(1, 2, key="value")

        with pytest.raises(AssertionError):
            mock.assert_awaited_with(3, 4)

    async def test_assert_awaited_once_with_works(self) -> None:
        """assert_awaited_once_with 메소드가 정상 동작하는지 확인."""
        mock = AsyncMock()
        await mock(1, 2)

        mock.assert_awaited_once_with(1, 2)

        await mock(1, 2)
        with pytest.raises(AssertionError):
            mock.assert_awaited_once_with(1, 2)

    async def test_assert_any_await_works(self) -> None:
        """assert_any_await 메소드가 정상 동작하는지 확인."""
        mock = AsyncMock()
        await mock(1)
        await mock(2)

        mock.assert_any_await(1)
        mock.assert_any_await(2)

        with pytest.raises(AssertionError):
            mock.assert_any_await(3)

    async def test_assert_not_awaited_works(self) -> None:
        """assert_not_awaited 메소드가 정상 동작하는지 확인."""
        mock = AsyncMock()
        mock.assert_not_awaited()

        await mock()
        with pytest.raises(AssertionError):
            mock.assert_not_awaited()

    async def test_await_count_property(self) -> None:
        """await_count 속성이 정상 동작하는지 확인."""
        mock = AsyncMock()
        assert mock.await_count == 0

        await mock()
        assert mock.await_count == 1

        await mock()
        await mock()
        assert mock.await_count == 3

    async def test_await_args_property(self) -> None:
        """await_args 속성이 정상 동작하는지 확인."""
        mock = AsyncMock()
        assert mock.await_args is None

        await mock(1, key="value")
        assert mock.await_args == call(1, key="value")

    async def test_await_args_list_property(self) -> None:
        """await_args_list 속성이 정상 동작하는지 확인."""
        mock = AsyncMock()
        assert mock.await_args_list == []

        await mock(1)
        await mock(2)
        assert mock.await_args_list == [call(1), call(2)]

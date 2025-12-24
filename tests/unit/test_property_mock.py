"""MockedProperty, MockedClassMethod, and MockedStaticMethod tests."""

from unittest.mock import MagicMock

import pytest

from typed_pytest._property import (
    MockedClassMethod,
    MockedProperty,
    MockedStaticMethod,
)


class TestMockedProperty:
    """MockedProperty tests."""

    def test_creation(self) -> None:
        """MockedProperty instance creation."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)
        assert prop is not None

    def test_return_value_access(self) -> None:
        """Access return_value property."""
        mock = MagicMock()
        mock.return_value = "test_value"
        prop: MockedProperty[str] = MockedProperty(mock)

        assert prop.return_value == "test_value"

    def test_return_value_setter(self) -> None:
        """Set return_value property."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)
        prop.return_value = "new_value"

        assert mock.return_value == "new_value"

    def test_call_count(self) -> None:
        """Access call_count property."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        assert prop.call_count == 0

        mock()
        assert prop.call_count == 1

    def test_called_property(self) -> None:
        """Access called property."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        assert prop.called is False

        mock()
        assert prop.called is True

    def test_assert_called(self) -> None:
        """assert_called method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        with pytest.raises(AssertionError):
            prop.assert_called()

        mock()
        prop.assert_called()

    def test_assert_called_once(self) -> None:
        """assert_called_once method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        with pytest.raises(AssertionError):
            prop.assert_called_once()

        mock()
        prop.assert_called_once()

        mock()
        with pytest.raises(AssertionError):
            prop.assert_called_once()

    def test_assert_called_with(self) -> None:
        """assert_called_with method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        # Properties can be "called" when accessed like methods
        mock("arg1", kwarg1="value")

        prop.assert_called_with("arg1", kwarg1="value")

        with pytest.raises(AssertionError):
            prop.assert_called_with("other")

    def test_assert_not_called(self) -> None:
        """assert_not_called method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        prop.assert_not_called()

        mock()
        with pytest.raises(AssertionError):
            prop.assert_not_called()

    def test_reset_mock(self) -> None:
        """reset_mock method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        mock()
        assert prop.call_count == 1

        prop.reset_mock()
        assert prop.call_count == 0

    def test_attribute_delegation(self) -> None:
        """Attribute delegation to internal mock."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        # mock_calls is a MagicMock attribute
        assert hasattr(prop, "mock_calls")
        assert prop.mock_calls == []


class TestMockedClassMethod:
    """MockedClassMethod tests."""

    def test_creation(self) -> None:
        """MockedClassMethod instance creation."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)
        assert method is not None

    def test_call_works(self) -> None:
        """Method call works."""
        mock = MagicMock()
        mock.return_value = "result"
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        result = method(42)

        assert result == "result"
        mock.assert_called_once_with(42)

    def test_call_with_kwargs(self) -> None:
        """Method call with keyword arguments."""
        mock = MagicMock()
        method: MockedClassMethod[[str, int], str] = MockedClassMethod(mock)

        method("arg", value=10)

        mock.assert_called_once_with("arg", value=10)

    def test_return_value(self) -> None:
        """return_value property."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        method.return_value = "test"

        assert method.return_value == "test"
        assert mock.return_value == "test"

    def test_side_effect_exception(self) -> None:
        """side_effect with exception."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        method.side_effect = ValueError("error")

        with pytest.raises(ValueError, match="error"):
            method(1)

    def test_side_effect_values(self) -> None:
        """side_effect with sequence."""
        mock = MagicMock()
        method: MockedClassMethod[[int], int] = MockedClassMethod(mock)

        method.side_effect = [1, 2, 3]

        assert method(1) == 1
        assert method(2) == 2
        assert method(3) == 3

    def test_call_count(self) -> None:
        """call_count property."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        assert method.call_count == 0

        method(1)
        assert method.call_count == 1

        method(2)
        assert method.call_count == 2

    def test_assert_called(self) -> None:
        """assert_called method."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        with pytest.raises(AssertionError):
            method.assert_called()

        method(1)
        method.assert_called()

    def test_assert_called_once_with(self) -> None:
        """assert_called_once_with method."""
        mock = MagicMock()
        method: MockedClassMethod[[int, str], dict] = MockedClassMethod(mock)

        method(1, "test")
        method.assert_called_once_with(1, "test")

    def test_reset_mock(self) -> None:
        """reset_mock method."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        method(1)
        assert method.call_count == 1

        method.reset_mock()
        assert method.call_count == 0


class TestMockedStaticMethod:
    """MockedStaticMethod tests."""

    def test_creation(self) -> None:
        """MockedStaticMethod instance creation."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)
        assert method is not None

    def test_call_works(self) -> None:
        """Method call works."""
        mock = MagicMock()
        mock.return_value = True
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        result = method("test@example.com")

        assert result is True
        mock.assert_called_once_with("test@example.com")

    def test_call_with_multiple_args(self) -> None:
        """Method call with multiple arguments."""
        mock = MagicMock()
        mock.return_value = 42
        method: MockedStaticMethod[[int, int, str], int] = MockedStaticMethod(mock)

        result = method(1, 2, "operation")

        assert result == 42
        mock.assert_called_once_with(1, 2, "operation")

    def test_return_value(self) -> None:
        """return_value property."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        method.return_value = False

        assert method.return_value is False
        assert mock.return_value is False

    def test_side_effect_exception(self) -> None:
        """side_effect with exception."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        method.side_effect = ValueError("invalid")

        with pytest.raises(ValueError, match="invalid"):
            method("test")

    def test_call_count(self) -> None:
        """call_count property."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        assert method.call_count == 0

        method("test1")
        assert method.call_count == 1

        method("test2")
        assert method.call_count == 2

    def test_assert_called_with(self) -> None:
        """assert_called_with method."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        method("test@example.com")

        method.assert_called_with("test@example.com")

    def test_assert_any_call(self) -> None:
        """assert_any_call method."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        method("first")
        method("second")

        method.assert_any_call("first")
        method.assert_any_call("second")

    def test_reset_mock(self) -> None:
        """reset_mock method."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        method("test")
        assert method.call_count == 1

        method.reset_mock()
        assert method.call_count == 0

    def test_attribute_delegation(self) -> None:
        """Attribute delegation to internal mock."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        assert hasattr(method, "mock_calls")
        assert method.mock_calls == []

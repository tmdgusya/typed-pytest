"""MockedProperty, MockedClassMethod, and MockedStaticMethod tests."""

from unittest.mock import MagicMock, call

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

    def test_side_effect_callable(self) -> None:
        """side_effect with callable."""
        mock = MagicMock()
        prop: MockedProperty[int] = MockedProperty(mock)

        def side_effect_fn(x: int) -> int:
            return x * 2

        prop.side_effect = side_effect_fn

        assert prop.side_effect is side_effect_fn
        # Properties are accessed, not called
        assert prop.side_effect(5) == 10

    def test_side_effect_none(self) -> None:
        """side_effect with None."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        prop.side_effect = None
        assert prop.side_effect is None

    def test_side_effect_mixed_list(self) -> None:
        """side_effect with mixed types in list (now supported by list[Any])."""
        mock = MagicMock()
        prop: MockedProperty[int] = MockedProperty(mock)

        # Mix of values and exceptions
        prop.side_effect = [1, ValueError("error"), 2]

        # Properties are typically accessed, but here we test the mock's side_effect behavior
        # When accessed as a method (common in some mock patterns)
        assert mock() == 1
        with pytest.raises(ValueError, match="error"):
            mock()
        assert mock() == 2

    def test_call_args(self) -> None:
        """call_args property."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        assert prop.call_args is None

        mock("arg1", kwarg1="value")
        assert prop.call_args is not None

    def test_call_args_list(self) -> None:
        """call_args_list property."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        assert prop.call_args_list == []

        mock("first")
        mock("second")

        assert len(prop.call_args_list) == 2

    def test_assert_any_call(self) -> None:
        """assert_any_call method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        mock("a")
        mock("b")

        prop.assert_any_call("a")
        prop.assert_any_call("b")

    def test_assert_has_calls(self) -> None:
        """assert_has_calls method."""
        mock = MagicMock()
        prop: MockedProperty[str] = MockedProperty(mock)

        mock("first")
        mock("second")

        prop.assert_has_calls([call("first"), call("second")])


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

    def test_call_args(self) -> None:
        """call_args property."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        method(1)
        assert method.call_args is not None

    def test_call_args_list(self) -> None:
        """call_args_list property."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        method(1)
        method(2)

        assert len(method.call_args_list) == 2

    def test_assert_has_calls(self) -> None:
        """assert_has_calls method."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        method(1)
        method(2)

        method.assert_has_calls([call(1), call(2)])

    def test_side_effect_callable(self) -> None:
        """side_effect with callable."""
        mock = MagicMock()
        method: MockedClassMethod[[int], int] = MockedClassMethod(mock)

        def side_effect_fn(x: int) -> int:
            return x * 10

        method.side_effect = side_effect_fn

        assert method(5) == 50

    def test_side_effect_list(self) -> None:
        """side_effect with list."""
        mock = MagicMock()
        method: MockedClassMethod[[], int] = MockedClassMethod(mock)

        method.side_effect = [100, 200, 300]

        assert method() == 100
        assert method() == 200
        assert method() == 300

    def test_called_property(self) -> None:
        """called property."""
        mock = MagicMock()
        method: MockedClassMethod[[int], str] = MockedClassMethod(mock)

        assert method.called is False

        method(1)
        assert method.called is True


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

    def test_side_effect_callable(self) -> None:
        """side_effect with callable."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], int] = MockedStaticMethod(mock)

        def side_effect_fn(x: int) -> int:
            return x + 100

        method.side_effect = side_effect_fn

        assert method(50) == 150

    def test_side_effect_list(self) -> None:
        """side_effect with list."""
        mock = MagicMock()
        method: MockedStaticMethod[[], str] = MockedStaticMethod(mock)

        method.side_effect = ["a", "b", "c"]

        assert method() == "a"
        assert method() == "b"
        assert method() == "c"

    def test_call_args(self) -> None:
        """call_args property."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        method(42)
        assert method.call_args is not None

    def test_call_args_list(self) -> None:
        """call_args_list property."""
        mock = MagicMock()
        method: MockedStaticMethod[[str], bool] = MockedStaticMethod(mock)

        method("a")
        method("b")

        assert len(method.call_args_list) == 2

    def test_called_property(self) -> None:
        """called property."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        assert method.called is False

        method(1)
        assert method.called is True

    def test_assert_called(self) -> None:
        """assert_called method."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        with pytest.raises(AssertionError):
            method.assert_called()

        method(1)
        method.assert_called()

    def test_assert_called_once(self) -> None:
        """assert_called_once method."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        method(1)
        method.assert_called_once()

        method(2)
        with pytest.raises(AssertionError):
            method.assert_called_once()

    def test_assert_has_calls(self) -> None:
        """assert_has_calls method."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        method(1)
        method(2)

        method.assert_has_calls([call(1), call(2)])

    def test_assert_not_called(self) -> None:
        """assert_not_called method."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        method.assert_not_called()

        method(1)
        with pytest.raises(AssertionError):
            method.assert_not_called()

    def test_reset_mock(self) -> None:
        """reset_mock method."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        method(1)
        assert method.call_count == 1

        method.reset_mock()
        assert method.call_count == 0

    def test_attribute_delegation(self) -> None:
        """Attribute delegation to internal mock."""
        mock = MagicMock()
        method: MockedStaticMethod[[int], str] = MockedStaticMethod(mock)

        assert hasattr(method, "mock_calls")
        assert method.mock_calls == []

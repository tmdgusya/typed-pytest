"""_get_method_type_info utility function tests."""

from unittest.mock import AsyncMock

from typed_pytest._mock import TypedMock, _get_method_type_info


class SampleClass:
    """Sample class for testing _get_method_type_info."""

    def regular_method(self, x: int) -> str:
        """Regular instance method."""
        return "result"

    async def async_method(self, x: int) -> str:
        """Async method."""
        return "async_result"

    @property
    def sample_property(self) -> str:
        """Property."""
        return "property_value"

    @classmethod
    def class_method(cls, x: int) -> str:
        """Class method."""
        return "classmethod_result"

    @staticmethod
    def static_method(x: int) -> str:
        """Static method."""
        return "staticmethod_result"


class TestGetMethodTypeInfo:
    """_get_method_type_info tests."""

    def test_regular_method(self) -> None:
        """Regular method returns 'method' type."""
        result = _get_method_type_info(SampleClass, "regular_method")

        assert result["type"] == "method"
        assert result["is_static"] is False

    def test_async_method(self) -> None:
        """Async method returns 'async' type."""
        result = _get_method_type_info(SampleClass, "async_method")

        assert result["type"] == "async"

    def test_property(self) -> None:
        """Property returns 'property' type."""
        result = _get_method_type_info(SampleClass, "sample_property")

        assert result["type"] == "property"

    def test_classmethod(self) -> None:
        """Classmethod returns 'classmethod' type."""
        result = _get_method_type_info(SampleClass, "class_method")

        assert result["type"] == "classmethod"

    def test_staticmethod(self) -> None:
        """Staticmethod returns 'staticmethod' type."""
        result = _get_method_type_info(SampleClass, "static_method")

        assert result["type"] == "staticmethod"
        assert result["is_static"] is True

    def test_nonexistent_method(self) -> None:
        """Nonexistent method returns default."""
        result = _get_method_type_info(SampleClass, "nonexistent")

        assert result["type"] == "method"
        assert result["is_static"] is False
        assert result["return_type"] is None

    def test_inherited_method(self) -> None:
        """Inherited method is found in MRO."""
        class ChildClass(SampleClass):
            pass

        result = _get_method_type_info(ChildClass, "regular_method")

        assert result["type"] == "method"


class TestTypedMockWithMethods:
    """TypedMock with various method types."""

    def test_mock_regular_method(self) -> None:
        """Mock regular method."""
        mock = TypedMock(spec=SampleClass)

        mock.regular_method.return_value = "mocked"
        result = mock.regular_method(1)

        assert result == "mocked"

    def test_mock_async_method(self) -> None:
        """Mock async method returns AsyncMock."""
        mock = TypedMock(spec=SampleClass)

        assert isinstance(mock.async_method, AsyncMock)

    def test_mock_property(self) -> None:
        """Mock property access."""
        mock = TypedMock(spec=SampleClass)

        mock.sample_property.return_value = "mocked_property"

        assert mock.sample_property.return_value == "mocked_property"

    def test_mock_classmethod(self) -> None:
        """Mock classmethod."""
        mock = TypedMock(spec=SampleClass)

        mock.class_method.return_value = "mocked_class"

        result = mock.class_method(1)

        assert result == "mocked_class"

    def test_mock_staticmethod(self) -> None:
        """Mock staticmethod."""
        mock = TypedMock(spec=SampleClass)

        mock.static_method.return_value = "mocked_static"

        result = mock.static_method(1)

        assert result == "mocked_static"

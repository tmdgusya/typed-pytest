"""typed_mock factory function tests."""

import pytest

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest import TypedMock, typed_mock


class TestTypedMockFactory:
    """typed_mock factory function tests."""

    def test_basic_creation(self) -> None:
        """Basic typed_mock call."""
        mock = typed_mock(UserService)
        assert isinstance(mock, TypedMock)

    def test_returns_typed_mock(self) -> None:
        """Verify it returns TypedMock instance."""
        mock = typed_mock(UserService)
        assert mock.typed_class is UserService

    def test_has_original_methods(self) -> None:
        """Verify it has original class methods."""
        mock = typed_mock(UserService)
        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")
        assert hasattr(mock, "delete_user")

    def test_method_call_works(self) -> None:
        """Verify method call works."""
        mock = typed_mock(UserService)
        mock.get_user.return_value = {"id": 1, "name": "Test"}

        result = mock.get_user(1)

        assert result == {"id": 1, "name": "Test"}
        mock.get_user.assert_called_once_with(1)


class TestTypedMockFactorySpecSet:
    """typed_mock spec_set option tests."""

    def test_spec_set_true(self) -> None:
        """Error when accessing non-existent attribute with spec_set=True."""
        mock = typed_mock(UserService, spec_set=True)

        # Accessing non-existent attribute raises AttributeError
        with pytest.raises(AttributeError):
            _ = mock.nonexistent_method

    def test_spec_set_true_prevents_setting(self) -> None:
        """Error when setting non-existent attribute with spec_set=True."""
        mock = typed_mock(UserService, spec_set=True)

        with pytest.raises(AttributeError):
            mock.nonexistent_attr = "value"  # type: ignore[attr-defined]

    def test_spec_set_false_allows_setting(self) -> None:
        """Can set non-existent attribute with spec_set=False."""
        mock = typed_mock(UserService, spec_set=False)

        # With spec only, setting attribute is allowed
        mock.custom_attr = "value"  # type: ignore[attr-defined]
        assert mock.custom_attr == "value"


class TestTypedMockFactoryName:
    """typed_mock name option tests."""

    def test_with_name(self) -> None:
        """Verify name is set."""
        mock = typed_mock(UserService, name="test_mock")
        assert "test_mock" in repr(mock)

    def test_without_name(self) -> None:
        """Verify creation without name is possible."""
        mock = typed_mock(UserService)
        assert mock is not None


class TestTypedMockFactoryKwargs:
    """typed_mock additional kwargs tests."""

    def test_return_value_passed(self) -> None:
        """Verify return_value is passed."""
        mock = typed_mock(UserService, return_value="custom")
        assert mock() == "custom"

    def test_side_effect_passed(self) -> None:
        """Verify side_effect is passed."""
        mock = typed_mock(UserService, side_effect=ValueError("error"))

        with pytest.raises(ValueError, match="error"):
            mock()


class TestTypedMockFactoryErrors:
    """typed_mock error case tests."""

    def test_non_class_raises_type_error(self) -> None:
        """TypeError when passing non-class."""
        with pytest.raises(TypeError, match="must be a class"):
            typed_mock("not a class")  # type: ignore[arg-type]

    def test_instance_raises_type_error(self) -> None:
        """TypeError when passing instance."""
        instance = UserService()
        with pytest.raises(TypeError, match="must be a class"):
            typed_mock(instance)  # type: ignore[arg-type]

    def test_none_raises_type_error(self) -> None:
        """TypeError when passing None."""
        with pytest.raises(TypeError, match="must be a class"):
            typed_mock(None)  # type: ignore[arg-type]


class TestTypedMockFactoryStrict:
    """typed_mock strict option tests (future implementation)."""

    def test_strict_option_accepted(self) -> None:
        """Verify strict option is accepted."""
        # strict=True has no effect yet
        mock = typed_mock(UserService, strict=True)
        assert mock is not None


class TestTypedMockFactoryRealScenarios:
    """typed_mock real usage scenario tests."""

    def test_service_with_repository(self) -> None:
        """Service-repository pattern."""
        mock_repo = typed_mock(ProductRepository)
        mock_repo.find_by_id.return_value = None

        result = mock_repo.find_by_id("P001")

        assert result is None
        mock_repo.find_by_id.assert_called_once_with("P001")

    def test_multiple_mocks(self) -> None:
        """Using multiple mocks simultaneously."""
        mock_service = typed_mock(UserService)
        mock_repo = typed_mock(ProductRepository)

        mock_service.get_user.return_value = {"id": 1}
        mock_repo.find_all.return_value = []

        assert mock_service.get_user(1) == {"id": 1}
        assert mock_repo.find_all() == []

    def test_side_effect_sequence(self) -> None:
        """side_effect sequence."""
        mock = typed_mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
        ]

        assert mock.get_user(1) == {"id": 1, "name": "First"}
        assert mock.get_user(2) == {"id": 2, "name": "Second"}

    def test_side_effect_exception(self) -> None:
        """side_effect exception."""
        mock = typed_mock(UserService)
        mock.get_user.side_effect = ValueError("User not found")

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(999)

    def test_assertion_methods(self) -> None:
        """assertion method chaining."""
        mock = typed_mock(UserService)

        mock.get_user(1)
        mock.get_user(2)
        mock.create_user("John", "john@example.com")

        mock.get_user.assert_called()
        assert mock.get_user.call_count == 2
        mock.create_user.assert_called_once_with("John", "john@example.com")

"""TypedMock 테스트."""

from unittest.mock import MagicMock

import pytest
from typed_pytest_stubs import ProductRepository, UserService, typed_mock

from typed_pytest import TypedMock


class TestTypedMockCreation:
    """TypedMock 생성 테스트."""

    def test_creation_without_spec(self) -> None:
        """spec 없이 TypedMock 생성."""
        mock: TypedMock[UserService] = TypedMock()
        assert mock is not None
        assert isinstance(mock, MagicMock)

    def test_creation_with_spec(self) -> None:
        """spec으로 TypedMock 생성."""
        mock = typed_mock(UserService)
        assert mock is not None
        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")

    def test_creation_with_spec_set(self) -> None:
        """Create TypedMock with spec_set."""
        mock = typed_mock(UserService, spec_set=True)
        assert hasattr(mock, "get_user")

        # spec_set prevents setting non-existent attributes
        with pytest.raises(AttributeError):
            mock.nonexistent_method = "value"  # type: ignore[attr-defined]

    def test_creation_with_name(self) -> None:
        """Create TypedMock with name."""
        mock = TypedMock(spec=UserService, name="test_mock")
        assert "test_mock" in str(mock)

    def test_typed_class_stored(self) -> None:
        """Verify typed_class is stored."""
        mock = typed_mock(UserService)
        assert mock.typed_class is UserService

    def test_typed_class_none_without_spec(self) -> None:
        """Verify typed_class is None when created without spec."""
        mock: TypedMock[UserService] = TypedMock()
        assert mock.typed_class is None


class TestTypedMockGenericSyntax:
    """TypedMock generic syntax tests."""

    def test_class_getitem(self) -> None:
        """Verify __class_getitem__ works."""
        MockType = TypedMock[UserService]
        assert MockType is not None

    def test_generic_type_annotation(self) -> None:
        """Verify generic type annotation works."""
        mock = typed_mock(UserService)
        assert isinstance(mock, TypedMock)


class TestTypedMockMethodAccess:
    """TypedMock 메소드 접근 테스트."""

    def test_method_returns_mock(self) -> None:
        """메소드 접근 시 Mock 반환."""
        mock = typed_mock(UserService)
        method = mock.get_user
        assert method is not None

    def test_method_has_mock_attributes(self) -> None:
        """메소드가 Mock 속성을 가지는지 확인."""
        mock = typed_mock(UserService)
        method = mock.get_user

        assert hasattr(method, "return_value")
        assert hasattr(method, "side_effect")
        assert hasattr(method, "assert_called")
        assert hasattr(method, "assert_called_once")
        assert hasattr(method, "call_count")

    def test_method_call_works(self) -> None:
        """메소드 호출이 동작하는지 확인."""
        mock = typed_mock(UserService)
        mock.get_user.return_value = {"id": 1, "name": "Test"}

        result = mock.get_user(1)

        assert result == {"id": 1, "name": "Test"}

    def test_method_assertion_works(self) -> None:
        """메소드 assertion이 동작하는지 확인."""
        mock = typed_mock(UserService)

        mock.get_user(1)

        mock.get_user.assert_called_once_with(1)

    def test_method_side_effect_works(self) -> None:
        """side_effect가 동작하는지 확인."""
        mock = typed_mock(UserService)
        mock.get_user.side_effect = ValueError("User not found")

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(999)


class TestTypedMockProperties:
    """TypedMock 속성 테스트."""

    def test_call_count(self) -> None:
        """call_count가 동작하는지 확인."""
        mock = typed_mock(UserService)

        assert mock.get_user.call_count == 0

        mock.get_user(1)
        assert mock.get_user.call_count == 1

        mock.get_user(2)
        mock.get_user(3)
        assert mock.get_user.call_count == 3

    def test_called(self) -> None:
        """called가 동작하는지 확인."""
        mock = typed_mock(UserService)

        assert mock.get_user.called is False

        mock.get_user(1)
        assert mock.get_user.called is True

    def test_call_args(self) -> None:
        """Verify call_args works."""
        mock = typed_mock(UserService)

        mock.get_user(1)
        mock.get_user(2, extra="value")

        # Verify last call arguments
        assert mock.get_user.call_args[0] == (2,)
        assert mock.get_user.call_args[1] == {"extra": "value"}

    def test_call_args_list(self) -> None:
        """Verify call_args_list works."""
        mock = typed_mock(UserService)

        mock.get_user(1)
        mock.get_user(2)
        mock.get_user(3)

        assert len(mock.get_user.call_args_list) == 3


class TestTypedMockRepr:
    """TypedMock repr tests."""

    def test_repr_with_spec(self) -> None:
        """Verify repr when spec is present."""
        mock = typed_mock(UserService)
        repr_str = repr(mock)

        assert "TypedMock" in repr_str
        assert "UserService" in repr_str

    def test_repr_without_spec(self) -> None:
        """Verify repr when spec is absent."""
        mock: TypedMock[UserService] = TypedMock()
        repr_str = repr(mock)

        assert "TypedMock" in repr_str


class TestTypedMockChildMock:
    """TypedMock child Mock tests."""

    def test_child_mock_is_magicmock(self) -> None:
        """Verify child mock is MagicMock."""
        mock = typed_mock(UserService)
        child = mock.get_user

        # Child is MagicMock but not TypedMock
        assert isinstance(child, MagicMock)


class TestTypedMockRealScenarios:
    """TypedMock 실제 사용 시나리오 테스트."""

    def test_service_with_repository(self) -> None:
        """서비스-리포지토리 패턴 테스트."""
        mock_repo = typed_mock(ProductRepository)
        mock_repo.find_by_id.return_value = None

        result = mock_repo.find_by_id("P001")

        assert result is None
        mock_repo.find_by_id.assert_called_once_with("P001")

    def test_multiple_method_calls(self) -> None:
        """여러 메소드 호출 테스트."""
        mock = typed_mock(UserService)

        mock.get_user.return_value = {"id": 1, "name": "John"}
        mock.create_user.return_value = {"id": 2, "name": "Jane"}

        user1 = mock.get_user(1)
        user2 = mock.create_user("Jane", "jane@example.com")

        assert user1 == {"id": 1, "name": "John"}
        assert user2 == {"id": 2, "name": "Jane"}

        mock.get_user.assert_called_once_with(1)
        mock.create_user.assert_called_once_with("Jane", "jane@example.com")

    def test_side_effect_sequence(self) -> None:
        """side_effect 시퀀스 테스트."""
        mock = typed_mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            ValueError("No more users"),
        ]

        assert mock.get_user(1) == {"id": 1, "name": "First"}
        assert mock.get_user(2) == {"id": 2, "name": "Second"}

        with pytest.raises(ValueError, match="No more users"):
            mock.get_user(3)

    def test_reset_mock(self) -> None:
        """reset_mock 테스트."""
        mock = typed_mock(UserService)

        mock.get_user(1)
        mock.get_user(2)

        assert mock.get_user.call_count == 2

        mock.get_user.reset_mock()

        assert mock.get_user.call_count == 0
        mock.get_user.assert_not_called()


class TestTypedMockClassMethod:
    """TypedMock class method tests."""

    def test_has_classmethod(self) -> None:
        """Verify classmethod is accessible."""
        mock = typed_mock(UserService)

        assert hasattr(mock, "from_config")

    def test_classmethod_call_works(self) -> None:
        """Classmethod call works through TypedMock."""
        mock = typed_mock(UserService)
        mock.from_config.return_value = mock

        result = mock.from_config({"key": "value"})

        assert result is mock
        mock.from_config.assert_called_once_with({"key": "value"})

    def test_classmethod_return_value(self) -> None:
        """Classmethod return_value works."""
        mock = typed_mock(UserService)
        mock.from_config.return_value = UserService()

        result = mock.from_config({})

        assert isinstance(result, UserService)

    def test_classmethod_assertions(self) -> None:
        """Classmethod assertion methods work."""
        mock = typed_mock(UserService)

        mock.from_config({"test": True})

        mock.from_config.assert_called()
        mock.from_config.assert_called_once_with({"test": True})
        assert mock.from_config.call_count == 1


class TestTypedMockStaticMethod:
    """TypedMock static method tests."""

    def test_has_staticmethod(self) -> None:
        """Verify staticmethod is accessible."""
        mock = typed_mock(UserService)

        assert hasattr(mock, "validate_email")

    def test_staticmethod_call_works(self) -> None:
        """Staticmethod call works through TypedMock."""
        mock = typed_mock(UserService)
        mock.validate_email.return_value = True

        result = mock.validate_email("test@example.com")

        assert result is True
        mock.validate_email.assert_called_once_with("test@example.com")

    def test_staticmethod_return_value(self) -> None:
        """Staticmethod return_value works."""
        mock = typed_mock(UserService)
        mock.validate_email.return_value = False

        result = mock.validate_email("invalid")

        assert result is False

    def test_staticmethod_assertions(self) -> None:
        """Staticmethod assertion methods work."""
        mock = typed_mock(UserService)

        mock.validate_email("user@test.com")

        mock.validate_email.assert_called()
        mock.validate_email.assert_called_once_with("user@test.com")
        assert mock.validate_email.call_count == 1


class TestTypedMockProperty:
    """TypedMock property tests."""

    def test_has_property(self) -> None:
        """Verify property is accessible."""
        mock = typed_mock(UserService)

        assert hasattr(mock, "connection_status")
        assert hasattr(mock, "is_connected")

    def test_property_mock_access(self) -> None:
        """Property access returns a mock."""
        mock = typed_mock(UserService)

        result = mock.connection_status

        # Property access returns a MagicMock
        assert result is not None
        assert hasattr(result, "return_value")

    def test_property_with_side_effect(self) -> None:
        """Property with side_effect works."""
        mock = typed_mock(UserService)
        # Store the property mock to ensure we use the same instance
        prop = mock.connection_status
        prop.side_effect = ValueError("not connected")

        with pytest.raises(ValueError, match="not connected"):
            _ = prop()

    def test_property_nested_mock(self) -> None:
        """Property returns typed mock for nested access."""
        mock = typed_mock(UserService)

        # Accessing a property returns a child mock
        prop = mock.connection_status
        prop.return_value = "custom_status"

        # Re-accessing should return same mock (cached by MagicMock)
        result = mock.connection_status
        assert result.return_value == "custom_status"

"""TypedMock 테스트."""

from unittest.mock import MagicMock

import pytest

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest._mock import TypedMock


class TestTypedMockCreation:
    """TypedMock 생성 테스트."""

    def test_creation_without_spec(self) -> None:
        """spec 없이 TypedMock 생성."""
        mock: TypedMock[UserService] = TypedMock()
        assert mock is not None
        assert isinstance(mock, MagicMock)

    def test_creation_with_spec(self) -> None:
        """spec으로 TypedMock 생성."""
        mock = TypedMock(spec=UserService)
        assert mock is not None
        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")

    def test_creation_with_spec_set(self) -> None:
        """spec_set으로 TypedMock 생성."""
        mock = TypedMock(spec_set=UserService)
        assert hasattr(mock, "get_user")

        # spec_set은 없는 속성 설정을 막음
        with pytest.raises(AttributeError):
            mock.nonexistent_method = "value"

    def test_creation_with_name(self) -> None:
        """name으로 TypedMock 생성."""
        mock = TypedMock(spec=UserService, name="test_mock")
        assert "test_mock" in str(mock)

    def test_typed_class_stored(self) -> None:
        """typed_class가 저장되는지 확인."""
        mock = TypedMock(spec=UserService)
        assert mock.typed_class is UserService

    def test_typed_class_none_without_spec(self) -> None:
        """spec 없이 생성 시 typed_class가 None인지 확인."""
        mock: TypedMock[UserService] = TypedMock()
        assert mock.typed_class is None


class TestTypedMockGenericSyntax:
    """TypedMock 제네릭 문법 테스트."""

    def test_class_getitem(self) -> None:
        """__class_getitem__이 동작하는지 확인."""
        MockType = TypedMock[UserService]
        assert MockType is not None

    def test_generic_type_annotation(self) -> None:
        """제네릭 타입 어노테이션이 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        assert isinstance(mock, TypedMock)


class TestTypedMockMethodAccess:
    """TypedMock 메소드 접근 테스트."""

    def test_method_returns_mock(self) -> None:
        """메소드 접근 시 Mock 반환."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        method = mock.get_user
        assert method is not None

    def test_method_has_mock_attributes(self) -> None:
        """메소드가 Mock 속성을 가지는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        method = mock.get_user

        assert hasattr(method, "return_value")
        assert hasattr(method, "side_effect")
        assert hasattr(method, "assert_called")
        assert hasattr(method, "assert_called_once")
        assert hasattr(method, "call_count")

    def test_method_call_works(self) -> None:
        """메소드 호출이 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        mock.get_user.return_value = {"id": 1, "name": "Test"}

        result = mock.get_user(1)

        assert result == {"id": 1, "name": "Test"}

    def test_method_assertion_works(self) -> None:
        """메소드 assertion이 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

        mock.get_user(1)

        mock.get_user.assert_called_once_with(1)

    def test_method_side_effect_works(self) -> None:
        """side_effect가 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        mock.get_user.side_effect = ValueError("User not found")

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(999)


class TestTypedMockProperties:
    """TypedMock 속성 테스트."""

    def test_call_count(self) -> None:
        """call_count가 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

        assert mock.get_user.call_count == 0

        mock.get_user(1)
        assert mock.get_user.call_count == 1

        mock.get_user(2)
        mock.get_user(3)
        assert mock.get_user.call_count == 3

    def test_called(self) -> None:
        """called가 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

        assert mock.get_user.called is False

        mock.get_user(1)
        assert mock.get_user.called is True

    def test_call_args(self) -> None:
        """call_args가 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

        mock.get_user(1)
        mock.get_user(2, extra="value")

        # 마지막 호출 인자 확인
        assert mock.get_user.call_args[0] == (2,)
        assert mock.get_user.call_args[1] == {"extra": "value"}

    def test_call_args_list(self) -> None:
        """call_args_list가 동작하는지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

        mock.get_user(1)
        mock.get_user(2)
        mock.get_user(3)

        assert len(mock.get_user.call_args_list) == 3


class TestTypedMockRepr:
    """TypedMock repr 테스트."""

    def test_repr_with_spec(self) -> None:
        """spec이 있을 때 repr 확인."""
        mock = TypedMock(spec=UserService)
        repr_str = repr(mock)

        assert "TypedMock" in repr_str
        assert "UserService" in repr_str

    def test_repr_without_spec(self) -> None:
        """spec이 없을 때 repr 확인."""
        mock: TypedMock[UserService] = TypedMock()
        repr_str = repr(mock)

        assert "TypedMock" in repr_str


class TestTypedMockChildMock:
    """TypedMock 자식 Mock 테스트."""

    def test_child_mock_is_magicmock(self) -> None:
        """자식 Mock이 MagicMock인지 확인."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        child = mock.get_user

        # 자식은 MagicMock이지만 TypedMock이 아님
        assert isinstance(child, MagicMock)


class TestTypedMockRealScenarios:
    """TypedMock 실제 사용 시나리오 테스트."""

    def test_service_with_repository(self) -> None:
        """서비스-리포지토리 패턴 테스트."""
        mock_repo: TypedMock[ProductRepository] = TypedMock(spec=ProductRepository)
        mock_repo.find_by_id.return_value = None

        result = mock_repo.find_by_id("P001")

        assert result is None
        mock_repo.find_by_id.assert_called_once_with("P001")

    def test_multiple_method_calls(self) -> None:
        """여러 메소드 호출 테스트."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

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
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
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
        mock: TypedMock[UserService] = TypedMock(spec=UserService)

        mock.get_user(1)
        mock.get_user(2)

        assert mock.get_user.call_count == 2

        mock.get_user.reset_mock()

        assert mock.get_user.call_count == 0
        mock.get_user.assert_not_called()

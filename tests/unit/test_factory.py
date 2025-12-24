"""typed_mock 팩토리 함수 테스트."""

import pytest

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest._factory import typed_mock
from typed_pytest._mock import TypedMock


class TestTypedMockFactory:
    """typed_mock 팩토리 함수 테스트."""

    def test_basic_creation(self) -> None:
        """기본 typed_mock 호출."""
        mock = typed_mock(UserService)
        assert isinstance(mock, TypedMock)

    def test_returns_typed_mock(self) -> None:
        """TypedMock 인스턴스를 반환하는지 확인."""
        mock = typed_mock(UserService)
        assert mock.typed_class is UserService

    def test_has_original_methods(self) -> None:
        """원본 클래스의 메소드를 가지는지 확인."""
        mock = typed_mock(UserService)
        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")
        assert hasattr(mock, "delete_user")

    def test_method_call_works(self) -> None:
        """메소드 호출이 동작하는지 확인."""
        mock = typed_mock(UserService)
        mock.get_user.return_value = {"id": 1, "name": "Test"}

        result = mock.get_user(1)

        assert result == {"id": 1, "name": "Test"}
        mock.get_user.assert_called_once_with(1)


class TestTypedMockFactorySpecSet:
    """typed_mock spec_set 옵션 테스트."""

    def test_spec_set_true(self) -> None:
        """spec_set=True일 때 없는 속성 접근 시 에러."""
        mock = typed_mock(UserService, spec_set=True)

        # 없는 속성에 접근하면 AttributeError
        with pytest.raises(AttributeError):
            _ = mock.nonexistent_method

    def test_spec_set_true_prevents_setting(self) -> None:
        """spec_set=True일 때 없는 속성 설정 시 에러."""
        mock = typed_mock(UserService, spec_set=True)

        with pytest.raises(AttributeError):
            mock.nonexistent_attr = "value"  # type: ignore[attr-defined]

    def test_spec_set_false_allows_setting(self) -> None:
        """spec_set=False일 때 없는 속성 설정 가능."""
        mock = typed_mock(UserService, spec_set=False)

        # spec만 사용하면 속성 설정은 가능
        mock.custom_attr = "value"  # type: ignore[attr-defined]
        assert mock.custom_attr == "value"


class TestTypedMockFactoryName:
    """typed_mock name 옵션 테스트."""

    def test_with_name(self) -> None:
        """이름이 지정되는지 확인."""
        mock = typed_mock(UserService, name="test_mock")
        assert "test_mock" in repr(mock)

    def test_without_name(self) -> None:
        """이름 없이 생성 가능한지 확인."""
        mock = typed_mock(UserService)
        assert mock is not None


class TestTypedMockFactoryKwargs:
    """typed_mock 추가 kwargs 테스트."""

    def test_return_value_passed(self) -> None:
        """return_value가 전달되는지 확인."""
        mock = typed_mock(UserService, return_value="custom")
        assert mock() == "custom"

    def test_side_effect_passed(self) -> None:
        """side_effect가 전달되는지 확인."""
        mock = typed_mock(UserService, side_effect=ValueError("error"))

        with pytest.raises(ValueError, match="error"):
            mock()


class TestTypedMockFactoryErrors:
    """typed_mock 에러 케이스 테스트."""

    def test_non_class_raises_type_error(self) -> None:
        """클래스가 아닌 값 전달 시 TypeError."""
        with pytest.raises(TypeError, match="must be a class"):
            typed_mock("not a class")  # type: ignore[arg-type]

    def test_instance_raises_type_error(self) -> None:
        """인스턴스 전달 시 TypeError."""
        instance = UserService()
        with pytest.raises(TypeError, match="must be a class"):
            typed_mock(instance)  # type: ignore[arg-type]

    def test_none_raises_type_error(self) -> None:
        """None 전달 시 TypeError."""
        with pytest.raises(TypeError, match="must be a class"):
            typed_mock(None)  # type: ignore[arg-type]


class TestTypedMockFactoryStrict:
    """typed_mock strict 옵션 테스트 (향후 구현)."""

    def test_strict_option_accepted(self) -> None:
        """strict 옵션이 수용되는지 확인."""
        # strict=True여도 현재는 동작 변화 없음
        mock = typed_mock(UserService, strict=True)
        assert mock is not None


class TestTypedMockFactoryRealScenarios:
    """typed_mock 실제 사용 시나리오 테스트."""

    def test_service_with_repository(self) -> None:
        """서비스-리포지토리 패턴."""
        mock_repo = typed_mock(ProductRepository)
        mock_repo.find_by_id.return_value = None

        result = mock_repo.find_by_id("P001")

        assert result is None
        mock_repo.find_by_id.assert_called_once_with("P001")

    def test_multiple_mocks(self) -> None:
        """여러 mock 동시 사용."""
        mock_service = typed_mock(UserService)
        mock_repo = typed_mock(ProductRepository)

        mock_service.get_user.return_value = {"id": 1}
        mock_repo.find_all.return_value = []

        assert mock_service.get_user(1) == {"id": 1}
        assert mock_repo.find_all() == []

    def test_side_effect_sequence(self) -> None:
        """side_effect 시퀀스."""
        mock = typed_mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
        ]

        assert mock.get_user(1) == {"id": 1, "name": "First"}
        assert mock.get_user(2) == {"id": 2, "name": "Second"}

    def test_side_effect_exception(self) -> None:
        """side_effect 예외."""
        mock = typed_mock(UserService)
        mock.get_user.side_effect = ValueError("User not found")

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(999)

    def test_assertion_methods(self) -> None:
        """assertion 메소드 체이닝."""
        mock = typed_mock(UserService)

        mock.get_user(1)
        mock.get_user(2)
        mock.create_user("John", "john@example.com")

        mock.get_user.assert_called()
        assert mock.get_user.call_count == 2
        mock.create_user.assert_called_once_with("John", "john@example.com")

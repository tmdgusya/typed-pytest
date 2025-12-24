"""TypedMocker 클래스 테스트."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest._method import MockedMethod
from typed_pytest._mock import TypedMock
from typed_pytest._mocker import TypedMocker


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


class TestTypedMockerCreation:
    """TypedMocker 생성 테스트."""

    def test_creation_with_mocker(self, mocker: MockerFixture) -> None:
        """MockerFixture로 TypedMocker 생성."""
        typed_mocker = TypedMocker(mocker)

        assert typed_mocker is not None

    def test_mocker_property_returns_original(self, mocker: MockerFixture) -> None:
        """mocker 속성이 원본 MockerFixture를 반환하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        assert typed_mocker.mocker is mocker


class TestTypedMockerMock:
    """TypedMocker.mock() 메소드 테스트."""

    def test_mock_returns_typed_mock(self, mocker: MockerFixture) -> None:
        """mock()이 TypedMock을 반환하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.mock(UserService)

        assert isinstance(mock, TypedMock)

    def test_mock_preserves_type_info(self, mocker: MockerFixture) -> None:
        """mock()이 타입 정보를 보존하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.mock(UserService)

        assert mock.typed_class is UserService

    def test_mock_has_original_methods(self, mocker: MockerFixture) -> None:
        """mock이 원본 클래스의 메소드를 가지는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.mock(UserService)

        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")
        assert hasattr(mock, "delete_user")

    def test_mock_with_spec_set(self, mocker: MockerFixture) -> None:
        """mock()이 spec_set 옵션을 전달하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.mock(UserService, spec_set=True)

        with pytest.raises(AttributeError):
            _ = mock.nonexistent_method

    def test_mock_with_name(self, mocker: MockerFixture) -> None:
        """mock()이 name 옵션을 전달하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.mock(UserService, name="test_mock")

        assert "test_mock" in repr(mock)

    def test_mock_method_call_works(self, mocker: MockerFixture) -> None:
        """mock된 메소드 호출이 동작하는지 확인."""
        typed_mocker = TypedMocker(mocker)
        mock = typed_mocker.mock(UserService)
        mock.get_user.return_value = {"id": 1, "name": "Test"}

        result = mock.get_user(1)

        assert result == {"id": 1, "name": "Test"}
        mock.get_user.assert_called_once_with(1)


class TestTypedMockerPatch:
    """TypedMocker.patch() 메소드 테스트."""

    def test_patch_with_type_returns_typed_mock(self, mocker: MockerFixture) -> None:
        """new 타입 지정 시 TypedMock을 반환하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )

        assert isinstance(mock, TypedMock)

    def test_patch_with_type_preserves_type_info(self, mocker: MockerFixture) -> None:
        """patch가 타입 정보를 보존하는지 확인."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )

        assert mock.typed_class is UserService

    def test_patch_without_type_returns_magicmock(self, mocker: MockerFixture) -> None:
        """Verify MagicMock is returned when new is not specified."""
        typed_mocker = TypedMocker(mocker)

        mock = typed_mocker.patch("tests.fixtures.sample_classes.UserService")

        # It's a MagicMock but not a TypedMock
        assert hasattr(mock, "return_value")
        assert not isinstance(mock, TypedMock)

    def test_patch_replaces_target(self, mocker: MockerFixture) -> None:
        """Verify patch actually replaces target."""
        typed_mocker = TypedMocker(mocker)
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 999}

        # Get UserService from patched module
        from tests.fixtures import sample_classes  # noqa: PLC0415

        # Verify patched class is a mock
        result = sample_classes.UserService.get_user(1)
        assert result == {"id": 999}


class TestTypedMockerSpy:
    """TypedMocker.spy() method tests."""

    def test_spy_returns_mocked_method(self, mocker: MockerFixture) -> None:
        """Verify spy() returns MockedMethod."""
        typed_mocker = TypedMocker(mocker)
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        assert isinstance(spy, MockedMethod)

    def test_spy_tracks_calls(self, mocker: MockerFixture) -> None:
        """Verify spy tracks calls."""
        typed_mocker = TypedMocker(mocker)
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        # Call real method
        result = service.validate_email("test@example.com")

        # Verify original behavior
        assert result is True

        # Verify call tracking
        spy.assert_called_once_with("test@example.com")

    def test_spy_has_mock_attributes(self, mocker: MockerFixture) -> None:
        """spy가 Mock 속성을 가지는지 확인."""
        typed_mocker = TypedMocker(mocker)
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        assert hasattr(spy, "call_count")
        assert hasattr(spy, "called")
        assert hasattr(spy, "call_args")

    def test_spy_call_count(self, mocker: MockerFixture) -> None:
        """spy가 호출 횟수를 추적하는지 확인."""
        typed_mocker = TypedMocker(mocker)
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        service.validate_email("a@b.com")
        service.validate_email("c@d.com")

        assert spy.call_count == 2


class TestTypedMockerRealScenarios:
    """TypedMocker 실제 사용 시나리오 테스트."""

    def test_service_with_mocked_repository(self, mocker: MockerFixture) -> None:
        """서비스-리포지토리 패턴 테스트."""
        typed_mocker = TypedMocker(mocker)
        mock_repo = typed_mocker.mock(ProductRepository)
        mock_repo.find_by_id.return_value = None

        result = mock_repo.find_by_id("P001")

        assert result is None
        mock_repo.find_by_id.assert_called_once_with("P001")

    def test_multiple_mocks(self, mocker: MockerFixture) -> None:
        """여러 mock 동시 사용."""
        typed_mocker = TypedMocker(mocker)
        mock_service = typed_mocker.mock(UserService)
        mock_repo = typed_mocker.mock(ProductRepository)

        mock_service.get_user.return_value = {"id": 1}
        mock_repo.find_all.return_value = []

        assert mock_service.get_user(1) == {"id": 1}
        assert mock_repo.find_all() == []

    def test_access_original_mocker_stub(self, mocker: MockerFixture) -> None:
        """Test accessing original mocker's stub() function."""
        typed_mocker = TypedMocker(mocker)

        # Use original mocker's functionality
        stub = typed_mocker.mocker.stub(name="test_stub")
        stub.return_value = "stubbed"

        assert stub() == "stubbed"

    def test_access_original_mocker_resetall(self, mocker: MockerFixture) -> None:
        """Test accessing original mocker's resetall() function."""
        typed_mocker = TypedMocker(mocker)

        # Mocks created with mocker.patch() are reset with resetall()
        mock = typed_mocker.mocker.patch("tests.fixtures.sample_classes.UserService")
        mock.get_user(1)
        assert mock.get_user.call_count == 1

        # Use original mocker's resetall
        typed_mocker.mocker.resetall()

        # Verify call count after reset
        assert mock.get_user.call_count == 0

    def test_side_effect_sequence(self, mocker: MockerFixture) -> None:
        """side_effect 시퀀스 테스트."""
        typed_mocker = TypedMocker(mocker)
        mock = typed_mocker.mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
        ]

        assert mock.get_user(1) == {"id": 1, "name": "First"}
        assert mock.get_user(2) == {"id": 2, "name": "Second"}

    def test_side_effect_exception(self, mocker: MockerFixture) -> None:
        """side_effect 예외 테스트."""
        typed_mocker = TypedMocker(mocker)
        mock = typed_mocker.mock(UserService)
        mock.get_user.side_effect = ValueError("User not found")

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(999)


class TestTypedMockerPublicAPI:
    """TypedMocker 공개 API 테스트."""

    def test_import_from_package(self) -> None:
        """패키지에서 TypedMocker를 임포트할 수 있는지 확인."""
        from typed_pytest import TypedMocker as ImportedTypedMocker  # noqa: PLC0415

        assert ImportedTypedMocker is TypedMocker

    def test_in_all(self) -> None:
        """TypedMocker가 __all__에 포함되어 있는지 확인."""
        import typed_pytest  # noqa: PLC0415

        assert "TypedMocker" in typed_pytest.__all__

"""typed_mocker fixture 통합 테스트.

pytest entry-point로 등록된 typed_mocker fixture가 올바르게 동작하는지 테스트합니다.
"""

from __future__ import annotations

import pytest

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest._method import MockedMethod
from typed_pytest._mock import TypedMock
from typed_pytest._mocker import TypedMocker


class TestTypedMockerFixtureAvailability:
    """typed_mocker fixture가 사용 가능한지 테스트."""

    def test_fixture_is_available(self, typed_mocker: TypedMocker) -> None:
        """typed_mocker fixture가 주입되는지 확인."""
        assert typed_mocker is not None

    def test_fixture_returns_typed_mocker(self, typed_mocker: TypedMocker) -> None:
        """typed_mocker fixture가 TypedMocker 인스턴스를 반환하는지 확인."""
        assert isinstance(typed_mocker, TypedMocker)


class TestTypedMockerFixtureMock:
    """typed_mocker.mock() 사용 테스트."""

    def test_mock_creates_typed_mock(self, typed_mocker: TypedMocker) -> None:
        """mock()이 TypedMock을 생성하는지 확인."""
        mock = typed_mocker.mock(UserService)

        assert isinstance(mock, TypedMock)

    def test_mock_preserves_type_info(self, typed_mocker: TypedMocker) -> None:
        """mock이 타입 정보를 보존하는지 확인."""
        mock = typed_mocker.mock(UserService)

        assert mock.typed_class is UserService

    def test_mock_method_callable(self, typed_mocker: TypedMocker) -> None:
        """mock된 메소드가 호출 가능한지 확인."""
        mock = typed_mocker.mock(UserService)
        mock.get_user.return_value = {"id": 1, "name": "Test User"}

        result = mock.get_user(1)

        assert result == {"id": 1, "name": "Test User"}

    def test_mock_assertion_works(self, typed_mocker: TypedMocker) -> None:
        """mock assertion이 동작하는지 확인."""
        mock = typed_mocker.mock(UserService)

        mock.get_user(1)

        mock.get_user.assert_called_once_with(1)


class TestTypedMockerFixturePatch:
    """typed_mocker.patch() 사용 테스트."""

    def test_patch_with_type_returns_typed_mock(
        self, typed_mocker: TypedMocker
    ) -> None:
        """patch(new=type)이 TypedMock을 반환하는지 확인."""
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )

        assert isinstance(mock, TypedMock)

    def test_patch_replaces_target_module(self, typed_mocker: TypedMocker) -> None:
        """patch가 실제로 모듈의 대상을 교체하는지 확인."""
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 999, "name": "Patched"}

        from tests.fixtures import sample_classes  # noqa: PLC0415

        result = sample_classes.UserService.get_user(1)

        assert result == {"id": 999, "name": "Patched"}


class TestTypedMockerFixtureSpy:
    """typed_mocker.spy() 사용 테스트."""

    def test_spy_returns_mocked_method(self, typed_mocker: TypedMocker) -> None:
        """spy()가 MockedMethod를 반환하는지 확인."""
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        assert isinstance(spy, MockedMethod)

    def test_spy_tracks_calls_while_preserving_behavior(
        self, typed_mocker: TypedMocker
    ) -> None:
        """spy가 원본 동작을 유지하면서 호출을 추적하는지 확인."""
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")
        result = service.validate_email("test@example.com")

        assert result is True
        spy.assert_called_once_with("test@example.com")


class TestTypedMockerFixtureOriginalMocker:
    """원본 mocker 접근 테스트."""

    def test_mocker_property_available(self, typed_mocker: TypedMocker) -> None:
        """mocker 속성이 사용 가능한지 확인."""
        assert typed_mocker.mocker is not None

    def test_mocker_stub_works(self, typed_mocker: TypedMocker) -> None:
        """원본 mocker의 stub()이 동작하는지 확인."""
        stub = typed_mocker.mocker.stub(name="test_stub")
        stub.return_value = "stubbed"

        assert stub() == "stubbed"


class TestTypedMockerFixtureRealWorld:
    """실제 사용 시나리오 테스트."""

    def test_service_repository_pattern(self, typed_mocker: TypedMocker) -> None:
        """서비스-리포지토리 패턴 테스트."""
        mock_repo = typed_mocker.mock(ProductRepository)
        mock_repo.find_by_id.return_value = {
            "id": "P001",
            "name": "Test Product",
            "price": 100,
        }

        result = mock_repo.find_by_id("P001")

        assert result["name"] == "Test Product"
        mock_repo.find_by_id.assert_called_once_with("P001")

    def test_multiple_mocks_in_single_test(self, typed_mocker: TypedMocker) -> None:
        """하나의 테스트에서 여러 mock 사용."""
        mock_service = typed_mocker.mock(UserService)
        mock_repo = typed_mocker.mock(ProductRepository)

        mock_service.get_user.return_value = {"id": 1}
        mock_repo.find_all.return_value = []

        assert mock_service.get_user(1) == {"id": 1}
        assert mock_repo.find_all() == []

    def test_side_effect_with_exception(self, typed_mocker: TypedMocker) -> None:
        """side_effect를 사용한 예외 발생 테스트."""
        mock = typed_mocker.mock(UserService)
        mock.get_user.side_effect = ValueError("User not found")

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(999)

    def test_side_effect_with_list(self, typed_mocker: TypedMocker) -> None:
        """side_effect를 사용한 순차적 반환값 테스트."""
        mock = typed_mocker.mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
        ]

        assert mock.get_user(1) == {"id": 1, "name": "First"}
        assert mock.get_user(2) == {"id": 2, "name": "Second"}


class TestTypedMockerFixtureCleanup:
    """fixture 정리(cleanup) 테스트."""

    def test_patch_cleanup_between_tests_part1(self, typed_mocker: TypedMocker) -> None:
        """패치가 테스트 간에 정리되는지 확인 (Part 1)."""
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 111}

        from tests.fixtures import sample_classes  # noqa: PLC0415

        assert sample_classes.UserService.get_user(1) == {"id": 111}

    def test_patch_cleanup_between_tests_part2(self, typed_mocker: TypedMocker) -> None:
        """패치가 테스트 간에 정리되는지 확인 (Part 2).

        Part 1에서 설정한 패치가 이 테스트에 영향을 주지 않아야 함.
        """
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 222}

        from tests.fixtures import sample_classes  # noqa: PLC0415

        # Part 1의 값(111)이 아닌 이 테스트의 값(222)이어야 함
        assert sample_classes.UserService.get_user(1) == {"id": 222}

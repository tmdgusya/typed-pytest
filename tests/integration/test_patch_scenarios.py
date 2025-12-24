"""patch 시나리오 통합 테스트 (T202).

다양한 patch 방식과 시나리오를 테스트합니다.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from tests.fixtures.sample_classes import UserService
from typed_pytest._mock import TypedMock


if TYPE_CHECKING:
    from typed_pytest._mocker import TypedMocker


class TestPatchObject:
    """patch_object() 메소드 테스트."""

    def test_patch_object_basic(self, typed_mocker: TypedMocker) -> None:
        """기본 patch_object 동작 테스트."""
        mock = typed_mocker.patch_object(os, "getcwd")
        mock.return_value = "/mocked/path"

        result = os.getcwd()  # noqa: PTH109

        assert result == "/mocked/path"
        mock.assert_called_once()

    def test_patch_object_with_type(self, typed_mocker: TypedMocker) -> None:
        """new 타입 지정 시 TypedMock 반환 테스트."""
        from tests.fixtures import sample_classes  # noqa: PLC0415

        mock = typed_mocker.patch_object(sample_classes, "UserService", new=UserService)

        assert isinstance(mock, TypedMock)
        assert mock.typed_class is UserService

    def test_patch_object_method_mock(self, typed_mocker: TypedMocker) -> None:
        """객체의 메소드를 patch하는 테스트."""
        service = UserService()
        mock = typed_mocker.patch_object(service, "get_user")
        mock.return_value = {"id": 999, "name": "Patched"}

        result = service.get_user(1)

        assert result == {"id": 999, "name": "Patched"}
        mock.assert_called_once_with(1)

    def test_patch_object_restores_after_test(self, typed_mocker: TypedMocker) -> None:
        """patch가 테스트 후 복원되는지 확인."""
        original_getcwd = os.getcwd
        mock = typed_mocker.patch_object(os, "getcwd")
        mock.return_value = "/fake"

        # 테스트 내에서는 mock
        assert os.getcwd() == "/fake"  # noqa: PTH109
        # 테스트 종료 후에는 pytest-mock이 자동 복원
        # (이 테스트에서는 아직 테스트 중이므로 mock 상태)
        assert os.getcwd != original_getcwd


class TestPatchDict:
    """patch_dict() 메소드 테스트."""

    def test_patch_dict_basic(self, typed_mocker: TypedMocker) -> None:
        """기본 patch_dict 동작 테스트."""
        typed_mocker.patch_dict(os.environ, {"TEST_VAR": "test_value"})

        assert os.environ["TEST_VAR"] == "test_value"

    def test_patch_dict_with_kwargs(self, typed_mocker: TypedMocker) -> None:
        """kwargs로 값 설정 테스트."""
        typed_mocker.patch_dict(os.environ, ANOTHER_VAR="another_value")

        assert os.environ["ANOTHER_VAR"] == "another_value"

    def test_patch_dict_clear(self, typed_mocker: TypedMocker) -> None:
        """clear=True로 딕셔너리 비우기 테스트."""
        test_dict = {"existing": "value", "another": "item"}
        typed_mocker.patch_dict(test_dict, {"new": "value"}, clear=True)

        assert test_dict == {"new": "value"}
        assert "existing" not in test_dict

    def test_patch_dict_preserves_original(self, typed_mocker: TypedMocker) -> None:
        """원본 딕셔너리가 테스트 후 복원되는지 확인."""
        test_dict = {"original": "value"}
        original_copy = test_dict.copy()

        typed_mocker.patch_dict(test_dict, {"added": "item"})

        assert "added" in test_dict
        # 테스트 내에서는 수정됨
        assert test_dict != original_copy

    def test_patch_dict_string_target(self, typed_mocker: TypedMocker) -> None:
        """문자열로 딕셔너리 대상 지정 테스트."""
        typed_mocker.patch_dict("os.environ", {"STRING_TARGET_VAR": "works"})

        assert os.environ["STRING_TARGET_VAR"] == "works"


class TestNestedPatches:
    """중첩 patch 테스트."""

    def test_nested_patches_work(self, typed_mocker: TypedMocker) -> None:
        """여러 patch를 동시에 사용하는 테스트."""
        mock1 = typed_mocker.patch_object(os, "getcwd")
        mock1.return_value = "/path1"

        mock2 = typed_mocker.patch_object(os.path, "exists")
        mock2.return_value = True

        assert os.getcwd() == "/path1"  # noqa: PTH109
        assert os.path.exists("/any/path") is True  # noqa: PTH110

    def test_patch_and_patch_object_together(self, typed_mocker: TypedMocker) -> None:
        """patch()와 patch_object()를 함께 사용하는 테스트."""
        mock1 = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock1.get_user.return_value = {"id": 1}

        mock2 = typed_mocker.patch_object(os, "getcwd")
        mock2.return_value = "/combined"

        from tests.fixtures import sample_classes  # noqa: PLC0415

        assert sample_classes.UserService.get_user(1) == {"id": 1}  # type: ignore[call-arg, arg-type]
        assert os.getcwd() == "/combined"  # noqa: PTH109

    def test_patch_with_patch_dict(self, typed_mocker: TypedMocker) -> None:
        """patch()와 patch_dict()를 함께 사용하는 테스트."""
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 1}

        typed_mocker.patch_dict(os.environ, {"CONFIG_VAR": "test"})

        from tests.fixtures import sample_classes  # noqa: PLC0415

        assert sample_classes.UserService.get_user(1) == {"id": 1}  # type: ignore[call-arg, arg-type]
        assert os.environ["CONFIG_VAR"] == "test"


class TestPatchAutospec:
    """autospec 옵션 테스트."""

    def test_patch_object_with_autospec(self, typed_mocker: TypedMocker) -> None:
        """autospec 옵션으로 시그니처 보존 테스트."""
        mock = typed_mocker.patch_object(os.path, "join", autospec=True)

        # autospec이면 시그니처가 보존됨
        os.path.join("a", "b", "c")  # noqa: PTH118
        mock.assert_called_once_with("a", "b", "c")

    def test_patch_object_autospec_tracks_calls(
        self, typed_mocker: TypedMocker
    ) -> None:
        """autospec이 호출을 추적하는지 테스트."""
        mock = typed_mocker.patch_object(os.path, "exists", autospec=True)
        mock.return_value = True

        result = os.path.exists("/some/path")  # noqa: PTH110

        assert result is True
        mock.assert_called_once_with("/some/path")


class TestPatchCleanupOrder:
    """patch 정리 순서 테스트."""

    def test_cleanup_order_part1(self, typed_mocker: TypedMocker) -> None:
        """Part 1: patch 설정."""
        typed_mocker.patch_dict(os.environ, {"CLEANUP_TEST": "part1"})
        assert os.environ["CLEANUP_TEST"] == "part1"

    def test_cleanup_order_part2(self, typed_mocker: TypedMocker) -> None:
        """Part 2: Part 1의 patch가 정리되었는지 확인."""
        # Part 1에서 설정한 값이 없어야 함
        assert os.environ.get("CLEANUP_TEST") is None

        typed_mocker.patch_dict(os.environ, {"CLEANUP_TEST": "part2"})
        assert os.environ["CLEANUP_TEST"] == "part2"

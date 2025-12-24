"""
mypy 타입 추론 테스트.

이 파일은 mypy 타입 체커에 의해 검사됩니다.
런타임 테스트가 아닌 정적 타입 검사용입니다.

Usage:
    uv run mypy tests/typecheck/mypy/ --strict
"""

# ruff: noqa: B018, TC001

from typing import Any
from unittest.mock import MagicMock

from pytest_mock import MockerFixture

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest import TypedMock, typed_mock
from typed_pytest._method import MockedMethod
from typed_pytest._mocker import TypedMocker


def test_typed_mock_infers_return_type() -> None:
    """typed_mock이 올바른 반환 타입을 추론하는지 검증."""
    mock = typed_mock(UserService)

    # TypedMock[UserService] 타입이어야 함
    mock_typed: TypedMock[UserService] = mock

    # 원본 메소드 접근 가능
    mock_typed.get_user(1)
    mock_typed.create_user("John", "john@example.com")

    # Mock assertion 메소드 접근 가능
    mock_typed.get_user.assert_called()
    mock_typed.get_user.assert_called_once_with(1)


def test_typed_mock_generic_annotation() -> None:
    """TypedMock 제네릭 타입 어노테이션 검증."""
    mock: TypedMock[UserService] = TypedMock(spec=UserService)

    # 원본 메소드 시그니처가 유지됨
    mock.get_user.return_value = {"id": 1, "name": "Test"}
    result = mock.get_user(1)

    # result는 Any 타입 (런타임에서 dict[str, Any])
    _: Any = result


def test_typed_mock_with_product_repository() -> None:
    """ProductRepository 타입으로 TypedMock 검증."""
    mock: TypedMock[ProductRepository] = typed_mock(ProductRepository)

    mock.find_by_id.return_value = None
    mock.find_all.return_value = []

    # 메소드 호출
    mock.find_by_id("P001")
    mock.find_all(limit=5)

    # Mock assertion
    mock.find_by_id.assert_called_once_with("P001")
    mock.find_all.assert_called_once_with(limit=5)


def test_mocked_method_type() -> None:
    """MockedMethod 타입 검증."""
    mock = typed_mock(UserService)

    # 메소드 접근 - MagicMock 기반
    method = mock.get_user

    # Mock 속성 접근
    _ = method.return_value
    _ = method.side_effect
    _ = method.call_count
    _ = method.called


def test_typed_mock_options() -> None:
    """typed_mock 옵션 파라미터 타입 검증."""
    # spec_set 옵션
    mock1 = typed_mock(UserService, spec_set=True)
    _m1: TypedMock[UserService] = mock1

    # name 옵션
    mock2 = typed_mock(UserService, name="test_mock")
    _m2: TypedMock[UserService] = mock2

    # 복합 옵션
    mock3 = typed_mock(UserService, spec_set=True, strict=True, name="combined")
    _m3: TypedMock[UserService] = mock3


def test_typed_mocker_mock_method() -> None:
    """TypedMocker.mock() 메소드 타입 검증."""
    # MockerFixture 모킹 (테스트용)
    mocker = MagicMock(spec=MockerFixture)
    typed_mocker = TypedMocker(mocker)

    # mock() 호출
    mock = typed_mocker.mock(UserService)
    _m4: TypedMock[UserService] = mock


def test_typed_mocker_spy_method() -> None:
    """TypedMocker.spy() 메소드 타입 검증."""
    mocker = MagicMock(spec=MockerFixture)
    mocker.spy = MagicMock()
    typed_mocker = TypedMocker(mocker)

    service = UserService()
    spy = typed_mocker.spy(service, "validate_email")

    # spy는 MockedMethod 타입
    _spy: MockedMethod[..., Any] = spy


def test_method_assertions_type_safety() -> None:
    """Mock assertion 메소드의 타입 안전성 검증."""
    mock = typed_mock(UserService)

    # 모든 assertion 메소드가 존재하고 호출 가능
    mock.get_user.assert_called
    mock.get_user.assert_called_once
    mock.get_user.assert_called_with
    mock.get_user.assert_called_once_with
    mock.get_user.assert_any_call
    mock.get_user.assert_not_called
    mock.get_user.reset_mock


def test_mock_properties_type_safety() -> None:
    """Mock 속성의 타입 안전성 검증."""
    mock = typed_mock(UserService)

    # Mock 속성 타입 검증
    count: int = mock.get_user.call_count
    called: bool = mock.get_user.called

    # call_args는 tuple 또는 None
    args = mock.get_user.call_args

    # call_args_list는 list
    args_list = mock.get_user.call_args_list

    # 미사용 경고 방지
    _ = count
    _ = called
    _ = args
    _ = args_list

"""타입 추론 검증 테스트.

이 파일은 타입 체커(mypy, pyright)에 의해 검사됩니다.
런타임 테스트가 아닌 정적 타입 검사용입니다.
"""

import contextlib
from typing import Any

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest import TypedMock, typed_mock


def test_typed_mock_creation() -> None:
    """typed_mock 생성 시 타입 추론."""
    # typed_mock은 TypedMock[T]를 반환해야 함
    mock: TypedMock[UserService] = typed_mock(UserService)
    assert mock is not None


def test_typed_mock_class_annotation() -> None:
    """TypedMock 클래스 어노테이션."""
    mock: TypedMock[UserService] = TypedMock(spec=UserService)
    assert mock is not None


def test_method_access() -> None:
    """메소드 접근 시 타입 안전성."""
    mock = typed_mock(UserService)

    # 원본 클래스의 메소드에 접근 가능해야 함
    mock.get_user(1)  # int 파라미터
    mock.create_user("name", "email@example.com")  # str 파라미터
    mock.delete_user(1)  # int 파라미터


def test_return_value_type() -> None:
    """return_value 설정."""
    mock = typed_mock(UserService)

    # return_value 설정 가능
    mock.get_user.return_value = {"id": 1, "name": "Test"}

    # 반환값 사용
    result: dict[str, Any] = mock.get_user(1)
    assert result is not None


def test_assertion_methods() -> None:
    """Mock assertion 메소드."""
    mock = typed_mock(UserService)

    mock.get_user(1)

    # assertion 메소드 호출
    mock.get_user.assert_called()
    mock.get_user.assert_called_once()
    mock.get_user.assert_called_with(1)
    mock.get_user.assert_called_once_with(1)


def test_mock_properties() -> None:
    """Mock 속성 접근."""
    mock = typed_mock(UserService)

    mock.get_user(1)
    mock.get_user(2)

    # 속성 접근
    count: int = mock.get_user.call_count
    called: bool = mock.get_user.called
    assert count == 2
    assert called is True


def test_side_effect() -> None:
    """side_effect 설정."""
    mock = typed_mock(UserService)

    # 리스트로 side_effect 설정
    mock.get_user.side_effect = [
        {"id": 1, "name": "First"},
        {"id": 2, "name": "Second"},
    ]

    # 순차적 반환
    first = mock.get_user(1)
    second = mock.get_user(2)
    assert first is not None
    assert second is not None


def test_side_effect_exception() -> None:
    """side_effect로 예외 설정."""
    mock = typed_mock(UserService)

    # 예외로 side_effect 설정
    mock.get_user.side_effect = ValueError("Not found")

    with contextlib.suppress(ValueError):
        mock.get_user(999)


def test_multiple_mocks() -> None:
    """여러 mock 동시 사용."""
    mock_service: TypedMock[UserService] = typed_mock(UserService)
    mock_repo: TypedMock[ProductRepository] = typed_mock(ProductRepository)

    mock_service.get_user.return_value = {"id": 1}
    mock_repo.find_by_id.return_value = None

    # 타입이 서로 독립적
    user_result = mock_service.get_user(1)
    product_result = mock_repo.find_by_id("P001")

    assert user_result is not None
    assert product_result is None


def test_spec_set_option() -> None:
    """spec_set 옵션."""
    mock = typed_mock(UserService, spec_set=True)

    # 존재하는 메소드는 접근 가능
    mock.get_user(1)
    mock.get_user.assert_called_once()


def test_reset_mock() -> None:
    """reset_mock 호출."""
    mock = typed_mock(UserService)

    mock.get_user(1)
    mock.get_user.reset_mock()

    # 리셋 후 호출 횟수 초기화
    count: int = mock.get_user.call_count
    assert count == 0


def test_call_args() -> None:
    """call_args, call_args_list 접근."""
    mock = typed_mock(UserService)

    mock.get_user(1)
    mock.get_user(2)

    # call_args 접근
    args = mock.get_user.call_args
    args_list = mock.get_user.call_args_list

    assert args is not None
    assert args_list is not None
    assert len(args_list) == 2

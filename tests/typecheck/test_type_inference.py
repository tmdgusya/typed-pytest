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

    # 반환값 사용 (mock은 Any를 반환하므로 Any로 타입 지정)
    result: Any = mock.get_user(1)
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


# =============================================================================
# Async Method Type Tests (T300, T301)
# =============================================================================


def test_async_method_access() -> None:
    """async 메소드 접근 시 타입 안전성."""
    mock = typed_mock(UserService)

    # async 메소드 접근 가능해야 함
    mock.async_get_user(1)  # int 파라미터
    mock.async_create_user("name", "email@example.com")  # str 파라미터


def test_async_return_value_type() -> None:
    """async 메소드의 return_value 설정."""
    mock = typed_mock(UserService)

    # return_value 설정 가능
    mock.async_get_user.return_value = {"id": 1, "name": "Test"}

    # 반환값 사용 (mock은 Any를 반환하므로 Any로 타입 지정)
    result: Any = mock.async_get_user(1)
    assert result is not None


def test_async_assertion_methods() -> None:
    """async Mock assertion 메소드."""
    mock = typed_mock(UserService)

    # async 메소드 호출 (비동기 컨텍스트 없이 타입만 검증)
    mock.async_get_user(1)

    # assertion 메소드 호출
    mock.async_get_user.assert_called()
    mock.async_get_user.assert_called_once()
    mock.async_get_user.assert_called_with(1)
    mock.async_get_user.assert_called_once_with(1)


def test_async_assert_awaited_methods() -> None:
    """async Mock await assertion 메소드 (타입만 검증).

    Note: assert_awaited* 메소드는 실제 await 후에 호출되어야 합니다.
    타입 검증을 위해 메소드 존재만 확인합니다.
    """
    mock = typed_mock(UserService)

    # await assertion 메소드 존재 확인 (타입만)
    # 런타임에서 호출 시 에러가 발생하므로 타입 체크 목적으로만 사용
    _ = mock.async_get_user.assert_awaited
    _ = mock.async_get_user.assert_awaited_once
    _ = mock.async_get_user.assert_awaited_with


def test_async_mock_properties() -> None:
    """async Mock 속성 접근."""
    mock = typed_mock(UserService)

    # 속성 접근
    count: int = mock.async_get_user.call_count
    called: bool = mock.async_get_user.called
    await_count: int = mock.async_get_user.await_count

    assert count == 0
    assert called is False
    assert await_count == 0


def test_async_side_effect() -> None:
    """async 메소드의 side_effect 설정."""
    mock = typed_mock(UserService)

    # 리스트로 side_effect 설정
    mock.async_get_user.side_effect = [
        {"id": 1, "name": "First"},
        {"id": 2, "name": "Second"},
    ]


def test_async_side_effect_exception() -> None:
    """async 메소드의 side_effect로 예외 설정."""
    mock = typed_mock(UserService)

    # 예외로 side_effect 설정
    mock.async_get_user.side_effect = ValueError("Not found")


def test_sync_and_async_methods_separation() -> None:
    """sync와 async 메소드가 다른 타입을 반환하는지 확인."""
    mock = typed_mock(UserService)

    # sync와 async 메소드 모두 접근 가능
    mock.get_user(1)
    mock.async_get_user(1)

    # 각각의 assertion 메소드 호출
    mock.get_user.assert_called_once()
    mock.async_get_user.assert_called_once()

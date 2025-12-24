"""
typed_mock 팩토리 함수.

타입 안전한 Mock 객체를 생성하는 팩토리 함수입니다.
"""

from __future__ import annotations

from typing import Any, TypeVar, overload

from typed_pytest._mock import TypedMock


T = TypeVar("T")


@overload
def typed_mock(cls: type[T], /) -> TypedMock[T]: ...


@overload
def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    strict: bool = False,
    name: str | None = None,
    **kwargs: Any,
) -> TypedMock[T]: ...


def typed_mock(
    cls: type[T],
    /,
    *,
    spec_set: bool = False,
    strict: bool = False,
    name: str | None = None,
    **kwargs: Any,
) -> TypedMock[T]:
    """타입 안전한 Mock 객체를 생성합니다.

    원본 클래스의 타입 정보를 유지하면서 Mock 기능을 제공하는
    TypedMock 인스턴스를 반환합니다.

    이 함수는 `TypedMock(spec=cls)`보다 더 간결한 API를 제공합니다.

    Args:
        cls: Mock으로 만들 원본 클래스.
        spec_set: True일 경우 spec에 없는 속성 접근/설정 시 AttributeError 발생.
            기본값은 False.
        strict: True일 경우 호출되지 않은 mock에 대해 경고 (향후 구현 예정).
            기본값은 False.
        name: Mock의 이름 (디버깅용). 기본값은 None.
        **kwargs: MagicMock에 전달할 추가 인자.

    Returns:
        원본 클래스의 타입 정보를 가진 TypedMock 인스턴스.

    Raises:
        TypeError: cls가 클래스가 아닐 경우.

    Example:
        기본 사용법:
            >>> from typed_pytest import typed_mock
            >>> mock_service = typed_mock(UserService)
            >>> mock_service.get_user.return_value = {"id": 1}
            >>> mock_service.get_user(1)
            {'id': 1}
            >>> mock_service.get_user.assert_called_once_with(1)

        spec_set 사용:
            >>> mock = typed_mock(UserService, spec_set=True)
            >>> mock.nonexistent_method()  # AttributeError!

        이름 지정:
            >>> mock = typed_mock(UserService, name="test_mock")
            >>> print(mock)  # <TypedMock[UserService] name='test_mock'>

    Note:
        - `spec_set=True`를 사용하면 원본 클래스에 없는 속성에 접근하거나
          설정할 때 AttributeError가 발생합니다. 이는 오타를 방지하는 데 유용합니다.
        - `strict` 옵션은 현재 구현되지 않았으며, 향후 버전에서 추가될 예정입니다.
    """
    # cls가 클래스인지 확인 (런타임 타입 검사)
    # Note: pyright는 타입 힌트로 이미 type[T]임을 알지만,
    # 런타임에서는 사용자가 잘못된 값을 전달할 수 있으므로 검증 필요
    if not isinstance(cls, type):  # pyright: ignore[reportUnnecessaryIsInstance]
        msg = f"typed_mock() argument must be a class, not {type(cls).__name__!r}"
        raise TypeError(msg)

    # strict 옵션은 향후 구현 예정
    if strict:
        # TODO: strict 모드 구현 (호출되지 않은 mock 경고)
        pass

    # TypedMock 생성
    if spec_set:
        return TypedMock(spec_set=cls, name=name, **kwargs)
    return TypedMock(spec=cls, name=name, **kwargs)

"""
TypedMock 제네릭 클래스.

원본 타입 T의 인터페이스를 유지하면서 Mock 기능을 제공하는 클래스입니다.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any, Generic, TypeVar
from unittest.mock import AsyncMock, MagicMock


if TYPE_CHECKING:
    from typed_pytest._method import AsyncMockedMethod, MockedMethod


T = TypeVar("T")


class TypedMock(MagicMock, Generic[T]):  # pyright: ignore[reportInconsistentConstructor]
    """원본 타입 T의 인터페이스를 유지하면서 Mock 기능을 제공하는 클래스.

    TypedMock은 MagicMock을 상속받아 모든 Mock 기능을 제공하면서,
    제네릭 타입 파라미터 T를 통해 원본 클래스의 타입 정보를 유지합니다.

    Usage:
        >>> from typed_pytest import TypedMock
        >>> mock_service: TypedMock[UserService] = TypedMock(spec=UserService)
        >>> mock_service.get_user(1)  # 원본 시그니처 자동완성
        >>> mock_service.get_user.assert_called_once_with(1)  # Mock 메소드 타입 힌트

    Example:
        >>> from unittest.mock import MagicMock
        >>> class UserService:
        ...     def get_user(self, user_id: int) -> dict: ...
        >>> mock: TypedMock[UserService] = TypedMock(spec=UserService)
        >>> mock.get_user.return_value = {"id": 1, "name": "Test"}
        >>> mock.get_user(1)
        {'id': 1, 'name': 'Test'}
        >>> mock.get_user.assert_called_once_with(1)

    Note:
        일반적으로 `typed_mock()` 팩토리 함수를 사용하는 것이 더 편리합니다.
    """

    # _typed_class를 인스턴스 변수로 선언 (MagicMock과 충돌 방지)
    __slots__ = ()

    def __init__(
        self,
        spec: type[T] | None = None,
        *,
        wraps: T | None = None,
        name: str | None = None,
        spec_set: type[T] | None = None,
        **kwargs: Any,
    ) -> None:
        """TypedMock 인스턴스를 생성합니다.

        Args:
            spec: Mock의 스펙으로 사용할 클래스. 이 클래스의 속성만 접근 가능.
            wraps: 실제 객체를 래핑할 경우 해당 객체.
            name: Mock의 이름 (디버깅용).
            spec_set: spec과 동일하나 속성 설정도 제한.
            **kwargs: MagicMock에 전달할 추가 인자.
        """
        # spec 또는 spec_set 결정
        actual_spec = spec_set or spec
        if spec_set is not None:
            kwargs["spec_set"] = spec_set
        elif spec is not None:
            kwargs["spec"] = spec

        if wraps is not None:
            kwargs["wraps"] = wraps
        if name is not None:
            kwargs["name"] = name

        super().__init__(**kwargs)

        # 타입 정보 저장 (MagicMock의 __setattr__를 우회)
        object.__setattr__(self, "_typed_class", actual_spec)

    if TYPE_CHECKING:
        # 타입 체커에게만 보이는 정의
        def __getattr__(
            self, name: str
        ) -> MockedMethod[..., Any] | AsyncMockedMethod[..., Any]:
            """타입 체커에게 MockedMethod 또는 AsyncMockedMethod 반환을 알림."""
            ...

    def _get_child_mock(self, **kwargs: Any) -> MagicMock:
        """자식 Mock 생성 시 async 메소드는 AsyncMock을 반환."""
        name = kwargs.get("name")
        if name and self.typed_class is not None:
            for cls in self.typed_class.__mro__:
                if name in cls.__dict__:
                    attr = cls.__dict__[name]
                    if inspect.iscoroutinefunction(attr):
                        return AsyncMock(**kwargs)
                    break
        return MagicMock(**kwargs)

    @property
    def typed_class(self) -> type[T] | None:
        """제네릭 파라미터로 전달된 원본 클래스."""
        result: type[T] | None = object.__getattribute__(self, "_typed_class")
        return result

    def __repr__(self) -> str:
        """TypedMock의 문자열 표현."""
        typed_class = object.__getattribute__(self, "_typed_class")
        name = self._mock_name

        if typed_class is not None:
            if name:
                return f"<TypedMock[{typed_class.__name__}] name='{name}'>"
            return f"<TypedMock[{typed_class.__name__}] id='{id(self)}'>"

        if name:
            return f"<TypedMock name='{name}'>"
        return f"<TypedMock id='{id(self)}'>"

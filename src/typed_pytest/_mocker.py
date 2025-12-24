"""
TypedMocker 클래스.

pytest-mock의 MockerFixture를 래핑하여 타입 안전한 mock 기능을 제공합니다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar, cast, overload

from typed_pytest._factory import typed_mock
from typed_pytest._method import MockedMethod


if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

    from typed_pytest._mock import TypedMock


T = TypeVar("T")


class TypedMocker:
    """pytest-mock의 MockerFixture를 확장한 타입 안전 모커.

    MockerFixture의 기능을 래핑하여 타입 안전한 mock, patch, spy를 제공합니다.

    Usage:
        >>> def test_example(mocker: MockerFixture):
        ...     typed_mocker = TypedMocker(mocker)
        ...     mock_service = typed_mocker.mock(UserService)
        ...     mock_service.get_user.return_value = {"id": 1}
        ...     assert mock_service.get_user(1) == {"id": 1}

    Example:
        mock() 사용:
            >>> typed_mocker = TypedMocker(mocker)
            >>> mock_service = typed_mocker.mock(UserService)
            >>> mock_service.get_user.return_value = {"id": 1}

        patch() 사용:
            >>> mock = typed_mocker.patch("app.services.UserService", new=UserService)
            >>> mock.get_user.return_value = {"id": 1}

        spy() 사용:
            >>> service = UserService()
            >>> spy = typed_mocker.spy(service, "get_user")
            >>> service.get_user(1)
            >>> spy.assert_called_once_with(1)

    Note:
        TypedMocker가 제공하지 않는 기능은 `mocker` 속성을 통해
        원본 MockerFixture에 접근하여 사용할 수 있습니다.
    """

    __slots__ = ("_mocker",)

    def __init__(self, mocker: MockerFixture) -> None:
        """TypedMocker 인스턴스를 생성합니다.

        Args:
            mocker: pytest-mock의 MockerFixture 인스턴스.
        """
        self._mocker = mocker

    def mock(self, cls: type[T], /, **kwargs: Any) -> TypedMock[T]:
        """타입 안전한 Mock 객체를 생성합니다.

        기존 typed_mock() 팩토리 함수를 재사용합니다.

        Args:
            cls: Mock으로 만들 원본 클래스.
            **kwargs: typed_mock()에 전달할 추가 인자
                (spec_set, strict, name 등).

        Returns:
            원본 클래스의 타입 정보를 가진 TypedMock 인스턴스.

        Example:
            >>> mock_service = typed_mocker.mock(UserService)
            >>> mock_service.get_user.return_value = {"id": 1}
            >>> mock_service.get_user(1)
            {'id': 1}
        """
        return typed_mock(cls, **kwargs)

    @overload
    def patch(
        self,
        target: str,
        *,
        new: type[T],
        **kwargs: Any,
    ) -> TypedMock[T]: ...

    @overload
    def patch(
        self,
        target: str,
        **kwargs: Any,
    ) -> MagicMock: ...

    def patch(
        self,
        target: str,
        *,
        new: type[Any] | None = None,
        **kwargs: Any,
    ) -> TypedMock[Any] | MagicMock:
        """타입 안전한 patch.

        new 파라미터에 타입이 지정되면 TypedMock[T]를 반환합니다.
        지정되지 않으면 기존 MagicMock을 반환합니다.

        Note:
            이 메소드는 컨텍스트 매니저가 아닌 직접 mock을 반환합니다.
            pytest-mock의 mocker.patch()는 테스트 종료 시 자동으로 정리됩니다.

        Args:
            target: patch 대상 (모듈.클래스 형식).
            new: Mock의 spec으로 사용할 클래스 (선택).
            **kwargs: mocker.patch()에 전달할 추가 인자.

        Returns:
            TypedMock[T] (new 지정 시) 또는 MagicMock.

        Example:
            new 타입 지정:
                >>> mock = typed_mocker.patch(
                ...     "app.services.UserService",
                ...     new=UserService,
                ... )
                >>> mock.get_user.return_value = {"id": 1}

            타입 미지정 (기존 동작):
                >>> mock = typed_mocker.patch("app.services.UserService")
                >>> mock.return_value = {"id": 1}
        """
        if new is not None:
            mock_instance = typed_mock(new)
            return self._mocker.patch(target, mock_instance, **kwargs)
        return cast("MagicMock", self._mocker.patch(target, **kwargs))

    def spy(self, obj: object, name: str) -> MockedMethod[..., Any]:
        """실제 객체의 메소드를 spy합니다.

        원본 메소드의 동작을 유지하면서 호출을 추적합니다.

        Args:
            obj: spy할 객체 인스턴스.
            name: spy할 메소드 이름.

        Returns:
            MockedMethod로 래핑된 spy 객체.

        Example:
            >>> service = UserService()
            >>> spy = typed_mocker.spy(service, "get_user")
            >>> service.get_user(1)  # 원본 메소드 실행
            >>> spy.assert_called_once_with(1)
        """
        spy_mock = self._mocker.spy(obj, name)
        return MockedMethod(spy_mock)

    @overload
    def patch_object(
        self,
        target: object,
        attribute: str,
        *,
        new: type[T],
        **kwargs: Any,
    ) -> TypedMock[T]: ...

    @overload
    def patch_object(
        self,
        target: object,
        attribute: str,
        **kwargs: Any,
    ) -> MagicMock: ...

    def patch_object(
        self,
        target: object,
        attribute: str,
        *,
        new: type[Any] | None = None,
        **kwargs: Any,
    ) -> TypedMock[Any] | MagicMock:
        """객체의 속성을 타입 안전하게 patch합니다.

        mocker.patch.object()를 래핑하여 타입 안전한 mock을 제공합니다.

        Args:
            target: patch할 객체.
            attribute: patch할 속성 이름.
            new: Mock의 spec으로 사용할 클래스 (선택).
            **kwargs: mocker.patch.object()에 전달할 추가 인자.

        Returns:
            TypedMock[T] (new 지정 시) 또는 MagicMock.

        Example:
            >>> import os
            >>> mock = typed_mocker.patch_object(os, "getcwd")
            >>> mock.return_value = "/mocked/path"
            >>> os.getcwd()
            '/mocked/path'
        """
        if new is not None:
            mock_instance = typed_mock(new)
            return self._mocker.patch.object(target, attribute, mock_instance, **kwargs)
        return cast("MagicMock", self._mocker.patch.object(target, attribute, **kwargs))

    def patch_dict(
        self,
        in_dict: dict[str, Any] | str,
        values: dict[str, Any] | None = None,
        clear: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """딕셔너리를 patch합니다.

        mocker.patch.dict()를 래핑합니다.
        테스트 종료 시 자동으로 원래 값으로 복원됩니다.

        Args:
            in_dict: patch할 딕셔너리 또는 딕셔너리를 가리키는 문자열.
            values: 딕셔너리에 설정할 값들.
            clear: True면 기존 딕셔너리를 비우고 values만 설정.
            **kwargs: 딕셔너리에 설정할 추가 키-값 쌍.

        Returns:
            patch된 딕셔너리.

        Example:
            >>> import os
            >>> typed_mocker.patch_dict(os.environ, {"MY_VAR": "test"})
            >>> os.environ["MY_VAR"]
            'test'
        """
        if values is None:
            values = {}
        return cast(
            "dict[str, Any]",
            self._mocker.patch.dict(in_dict, values, clear=clear, **kwargs),
        )

    @property
    def mocker(self) -> MockerFixture:
        """원본 MockerFixture에 접근합니다.

        TypedMocker가 제공하지 않는 기능이 필요할 때 사용합니다.
        (예: resetall(), stopall(), stub(), patch.dict() 등)

        Returns:
            원본 MockerFixture 인스턴스.

        Example:
            >>> stub = typed_mocker.mocker.stub(name="callback")
            >>> stub.return_value = "stubbed"
        """
        return self._mocker

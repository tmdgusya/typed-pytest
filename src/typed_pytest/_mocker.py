"""
TypedMocker class.

Wraps pytest-mock's MockerFixture to provide type-safe mock functionality.
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
    """Type-safe mocker extending pytest-mock's MockerFixture.

    Wraps MockerFixture's functionality to provide type-safe mock, patch, and spy.

    Usage:
        >>> def test_example(mocker: MockerFixture):
        ...     typed_mocker = TypedMocker(mocker)
        ...     mock_service = typed_mocker.mock(UserService)
        ...     mock_service.get_user.return_value = {"id": 1}
        ...     assert mock_service.get_user(1) == {"id": 1}

    Example:
        Using mock():
            >>> typed_mocker = TypedMocker(mocker)
            >>> mock_service = typed_mocker.mock(UserService)
            >>> mock_service.get_user.return_value = {"id": 1}

        Using patch():
            >>> mock = typed_mocker.patch("app.services.UserService", new=UserService)
            >>> mock.get_user.return_value = {"id": 1}

        Using spy():
            >>> service = UserService()
            >>> spy = typed_mocker.spy(service, "get_user")
            >>> service.get_user(1)
            >>> spy.assert_called_once_with(1)

    Note:
        Features not provided by TypedMocker can be accessed through the `mocker` attribute
        to use the original MockerFixture.
    """

    __slots__ = ("_mocker",)

    def __init__(self, mocker: MockerFixture) -> None:
        """Creates a TypedMocker instance.

        Args:
            mocker: pytest-mock's MockerFixture instance.
        """
        self._mocker = mocker

    def mock(self, cls: type[T], /, **kwargs: Any) -> TypedMock[T]:
        """Creates a type-safe Mock object.

        Reuses the existing typed_mock() factory function.

        Args:
            cls: Original class to mock.
            **kwargs: Additional arguments to pass to typed_mock()
                (spec_set, strict, name, etc.).

        Returns:
            TypedMock instance with the original class's type information.

        Example:
            >>> mock_service = typed_mocker.mock(UserService)
            >>> mock_service.get_user.return_value = {"id": 1}
            >>> mock_service.get_user(1)
            {'id': 1}
        """
        return typed_mock(cls, **kwargs)

    @overload
    def patch(  # pyright: ignore[reportOverlappingOverload]
        self,
        target: str,
        *,
        new: type[T],
        **kwargs: Any,
    ) -> TypedMock[T]: ...

    @overload
    def patch(  # pyright: ignore[reportOverlappingOverload]
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
        """Type-safe patch.

        Returns TypedMock[T] if new parameter has a type specified.
        Returns regular MagicMock if not specified.

        Note:
            This method returns a mock directly, not a context manager.
            pytest-mock's mocker.patch() is automatically cleaned up at the end of the test.

        Args:
            target: Target to patch (module.Class format).
            new: Class to use as the Mock's spec (optional).
            **kwargs: Additional arguments to pass to mocker.patch().

        Returns:
            TypedMock[T] (when new is specified) or MagicMock.

        Example:
            With type specified:
                >>> mock = typed_mocker.patch(
                ...     "app.services.UserService",
                ...     new=UserService,
                ... )
                >>> mock.get_user.return_value = {"id": 1}

            Without type (legacy behavior):
                >>> mock = typed_mocker.patch("app.services.UserService")
                >>> mock.return_value = {"id": 1}
        """
        if new is not None:
            mock_instance = typed_mock(new)
            return self._mocker.patch(target, mock_instance, **kwargs)
        return cast("MagicMock", self._mocker.patch(target, **kwargs))

    def spy(self, obj: object, name: str) -> MockedMethod[..., Any]:
        """Spies on a method of a real object.

        Tracks calls while preserving the original method's behavior.

        Args:
            obj: Object instance to spy on.
            name: Name of the method to spy on.

        Returns:
            Spy object wrapped in MockedMethod.

        Example:
            >>> service = UserService()
            >>> spy = typed_mocker.spy(service, "get_user")
            >>> service.get_user(1)  # Executes original method
            >>> spy.assert_called_once_with(1)
        """
        spy_mock = self._mocker.spy(obj, name)
        return MockedMethod(spy_mock)

    @overload
    def patch_object(  # pyright: ignore[reportOverlappingOverload]
        self,
        target: object,
        attribute: str,
        *,
        new: type[T],
        **kwargs: Any,
    ) -> TypedMock[T]: ...

    @overload
    def patch_object(  # pyright: ignore[reportOverlappingOverload]
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
        """Patches an object's attribute in a type-safe way.

        Wraps mocker.patch.object() to provide type-safe mock.

        Args:
            target: Object to patch.
            attribute: Attribute name to patch.
            new: Class to use as the Mock's spec (optional).
            **kwargs: Additional arguments to pass to mocker.patch.object().

        Returns:
            TypedMock[T] (when new is specified) or MagicMock.

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
        """Patches a dictionary.

        Wraps mocker.patch.dict(). Automatically restores original values at test end.

        Args:
            in_dict: Dictionary to patch or string pointing to a dictionary.
            values: Values to set in the dictionary.
            clear: If True, clears the existing dictionary and sets only values.
            **kwargs: Additional key-value pairs to set in the dictionary.

        Returns:
            The patched dictionary.

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
        """Accesses the original MockerFixture.

        Use when you need features not provided by TypedMocker.
        (e.g., resetall(), stopall(), stub(), patch.dict(), etc.)

        Returns:
            The original MockerFixture instance.

        Example:
            >>> stub = typed_mocker.mocker.stub(name="callback")
            >>> stub.return_value = "stubbed"
        """
        return self._mocker

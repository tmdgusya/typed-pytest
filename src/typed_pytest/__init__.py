"""
typed-pytest: Type-safe mocking for pytest.

타입 안전한 pytest mocking 라이브러리.
원본 클래스의 타입 정보를 유지하면서 Mock 기능을 제공합니다.

Usage:
    from typed_pytest import TypedMock, typed_mock

    mock_service: TypedMock[UserService] = typed_mock(UserService)
    mock_service.get_user.return_value = {"id": 1}
    mock_service.get_user.assert_called_once_with(1)
"""

from typed_pytest._factory import typed_mock
from typed_pytest._method import AsyncMockedMethod, MockedMethod
from typed_pytest._mock import TypedMock
from typed_pytest._mocker import TypedMocker
from typed_pytest._property import MockedClassMethod, MockedProperty, MockedStaticMethod
from typed_pytest._protocols import AsyncMockProtocol, MockProtocol
from typed_pytest._version import __version__


__all__ = [
    "AsyncMockProtocol",
    "AsyncMockedMethod",
    "MockProtocol",
    "MockedClassMethod",
    "MockedMethod",
    "MockedProperty",
    "MockedStaticMethod",
    "TypedMock",
    "TypedMocker",
    "__version__",
    "typed_mock",
]

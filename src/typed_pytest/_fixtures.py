"""
pytest plugin fixtures for typed-pytest.

이 모듈은 pytest entry-point로 등록되어 자동으로 로드됩니다.
typed_mocker fixture를 제공하여 TypedMocker를 쉽게 사용할 수 있게 합니다.

Usage:
    def test_example(typed_mocker: TypedMocker) -> None:
        mock_service = typed_mocker.mock(UserService)
        mock_service.get_user.return_value = {"id": 1}
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from typed_pytest._mocker import TypedMocker


if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture
def typed_mocker(mocker: MockerFixture) -> TypedMocker:
    """타입 안전한 MockerFixture를 제공하는 fixture.

    pytest-mock의 mocker fixture를 래핑하여 타입 안전한 mock 기능을 제공합니다.

    Args:
        mocker: pytest-mock의 MockerFixture.

    Returns:
        TypedMocker 인스턴스.

    Example:
        >>> def test_service(typed_mocker: TypedMocker) -> None:
        ...     mock = typed_mocker.mock(UserService)
        ...     mock.get_user.return_value = {"id": 1}
        ...     assert mock.get_user(1) == {"id": 1}
    """
    return TypedMocker(mocker)

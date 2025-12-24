"""
pytest 공통 fixture 정의.

이 파일의 fixture는 모든 테스트에서 사용할 수 있습니다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from pytest_mock import MockerFixture

    from typed_pytest._mocker import TypedMocker


# =============================================================================
# Sample class fixtures
# =============================================================================


@pytest.fixture
def user_service_class() -> type[UserService]:
    """UserService 클래스 반환 (인스턴스가 아닌 클래스)."""
    from tests.fixtures.sample_classes import UserService  # noqa: PLC0415

    return UserService


# =============================================================================
# typed-pytest fixtures
# =============================================================================


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
    from typed_pytest._mocker import TypedMocker

    return TypedMocker(mocker)

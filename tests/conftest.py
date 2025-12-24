"""
pytest 공통 fixture 정의.

이 파일의 fixture는 모든 테스트에서 사용할 수 있습니다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from tests.fixtures.sample_classes import UserService


# =============================================================================
# Sample class fixtures
# =============================================================================


@pytest.fixture
def user_service_class() -> type[UserService]:
    """UserService 클래스 반환 (인스턴스가 아닌 클래스)."""
    from tests.fixtures.sample_classes import UserService  # noqa: PLC0415

    return UserService


# Phase 2 (T201)에서 typed_mocker fixture 추가 예정

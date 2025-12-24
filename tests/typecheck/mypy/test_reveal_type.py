"""
reveal_type을 사용한 mypy 타입 추론 검증.

이 파일은 mypy --warn-unreachable로 실행하여 타입 추론을 검증합니다.
reveal_type() 호출은 mypy가 추론한 타입을 출력합니다.

Usage:
    uv run mypy tests/typecheck/mypy/test_reveal_type.py --strict 2>&1 | grep "Revealed type"

Note:
    이 테스트는 런타임 테스트가 아닌 정적 분석용입니다.
    reveal_type()은 mypy 전용 함수로, 런타임에서는 NameError를 발생시킵니다.
"""

# ruff: noqa: F821, I001

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from unittest.mock import MagicMock

    from pytest_mock import MockerFixture

    from tests.fixtures.sample_classes import ProductRepository, UserService
    from typed_pytest import TypedMock, typed_mock
    from typed_pytest._mocker import TypedMocker

    def check_typed_mock_inference() -> None:
        """typed_mock 반환 타입 추론 검증."""
        mock = typed_mock(UserService)
        reveal_type(mock)  # TypedMock[UserService]

    def check_typed_mock_annotation() -> None:
        """TypedMock 제네릭 타입 어노테이션 검증."""
        mock: TypedMock[UserService] = TypedMock(spec=UserService)
        reveal_type(mock)  # TypedMock[UserService]

    def check_method_access() -> None:
        """메소드 접근 타입 검증."""
        mock = typed_mock(UserService)
        method = mock.get_user
        reveal_type(method)  # MagicMock (런타임에서는 MagicMock)

    def check_return_value() -> None:
        """return_value 타입 검증."""
        mock = typed_mock(UserService)
        rv = mock.get_user.return_value
        reveal_type(rv)  # Any

    def check_typed_mocker_mock() -> None:
        """TypedMocker.mock() 타입 검증."""
        mocker = MagicMock(spec=MockerFixture)
        typed_mocker = TypedMocker(mocker)
        mock = typed_mocker.mock(UserService)
        reveal_type(mock)  # TypedMock[UserService]

    def check_typed_mocker_spy() -> None:
        """TypedMocker.spy() 타입 검증."""
        mocker = MagicMock(spec=MockerFixture)
        mocker.spy = MagicMock()
        typed_mocker = TypedMocker(mocker)
        service = UserService()
        spy = typed_mocker.spy(service, "validate_email")
        reveal_type(spy)  # MockedMethod[..., Any]

    def check_product_repository() -> None:
        """ProductRepository 타입 검증."""
        mock = typed_mock(ProductRepository)
        reveal_type(mock)  # TypedMock[ProductRepository]
        reveal_type(mock.find_by_id)  # MagicMock

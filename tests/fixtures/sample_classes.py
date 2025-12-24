"""
테스트용 샘플 클래스 정의.

이 클래스들은 typed-pytest의 기능을 테스트하기 위한 대상입니다.
다양한 메소드 시그니처와 타입을 포함합니다.
"""

from dataclasses import dataclass
from typing import Any


# =============================================================================
# Data classes
# =============================================================================


@dataclass
class User:
    """사용자 엔티티."""

    id: int
    name: str
    email: str | None = None


@dataclass
class Product:
    """상품 엔티티."""

    id: str
    name: str
    price: float


# =============================================================================
# Repository classes
# =============================================================================


class UserRepository:
    """사용자 저장소."""

    def find_by_id(self, user_id: int) -> User | None:
        """ID로 사용자 조회."""
        raise NotImplementedError

    def find_all(self, limit: int = 10, offset: int = 0) -> list[User]:
        """모든 사용자 조회."""
        raise NotImplementedError

    def save(self, user: User) -> User:
        """사용자 저장."""
        raise NotImplementedError

    def delete(self, user_id: int) -> bool:
        """사용자 삭제."""
        raise NotImplementedError


class ProductRepository:
    """상품 저장소."""

    def find_by_id(self, product_id: str) -> Product | None:
        """ID로 상품 조회."""
        raise NotImplementedError

    def find_all(self, limit: int = 10) -> list[Product]:
        """모든 상품 조회."""
        raise NotImplementedError

    def search(self, query: str, *, max_results: int = 100) -> list[Product]:
        """상품 검색 (키워드 전용 인자 포함)."""
        raise NotImplementedError


# =============================================================================
# Service classes
# =============================================================================


class UserService:
    """사용자 서비스 - 다양한 메소드 시그니처 테스트용."""

    def __init__(self, repository: UserRepository | None = None) -> None:
        """생성자."""
        self._repository = repository

    # 기본 메소드
    def get_user(self, user_id: int) -> dict[str, Any]:
        """사용자 조회 - 기본 시그니처."""
        raise NotImplementedError

    def create_user(self, name: str, email: str) -> dict[str, Any]:
        """사용자 생성 - 다중 파라미터."""
        raise NotImplementedError

    def update_user(
        self,
        user_id: int,
        *,
        name: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """사용자 수정 - 키워드 전용 인자."""
        raise NotImplementedError

    def delete_user(self, user_id: int) -> bool:
        """사용자 삭제 - bool 반환."""
        raise NotImplementedError

    # 비동기 메소드
    async def async_get_user(self, user_id: int) -> dict[str, Any]:
        """비동기 사용자 조회."""
        raise NotImplementedError

    async def async_create_user(self, name: str, email: str) -> dict[str, Any]:
        """비동기 사용자 생성."""
        raise NotImplementedError

    # 프로퍼티
    @property
    def connection_status(self) -> str:
        """연결 상태 프로퍼티."""
        return "connected"

    @property
    def is_connected(self) -> bool:
        """연결 여부."""
        return True

    # 클래스 메소드
    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "UserService":
        """설정에서 서비스 생성."""
        return cls()

    # 스태틱 메소드
    @staticmethod
    def validate_email(email: str) -> bool:
        """이메일 유효성 검사."""
        return "@" in email


# =============================================================================
# Complex types for advanced testing
# =============================================================================


class GenericService[T]:
    """제네릭 서비스 - 제네릭 타입 테스트용."""

    def get(self, id: int) -> T | None:
        """제네릭 조회."""
        raise NotImplementedError

    def get_all(self) -> list[T]:
        """제네릭 전체 조회."""
        raise NotImplementedError

    def save(self, item: T) -> T:
        """제네릭 저장."""
        raise NotImplementedError


class NestedService:
    """중첩 서비스 - 중첩 mock 테스트용."""

    def __init__(self) -> None:
        """생성자."""
        self.user_service = UserService()
        self.product_repo = ProductRepository()

    def get_user_products(self, user_id: int) -> list[Product]:
        """사용자의 상품 조회."""
        raise NotImplementedError

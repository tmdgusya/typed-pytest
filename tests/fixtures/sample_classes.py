"""Sample classes for testing.

These classes are used to test typed-pytest functionality.
They include various method signatures and types."""

from dataclasses import dataclass
from typing import Any, Generic, TypeVar


T = TypeVar("T")


# =============================================================================
# Data classes
# =============================================================================


@dataclass
class User:
    """User entity."""

    id: int
    name: str
    email: str | None = None


@dataclass
class Product:
    """Product entity."""

    id: str
    name: str
    price: float


# =============================================================================
# Repository classes
# =============================================================================


class UserRepository:
    """User repository."""

    def find_by_id(self, user_id: int) -> User | None:
        """Find user by ID."""
        raise NotImplementedError

    def find_all(self, limit: int = 10, offset: int = 0) -> list[User]:
        """Find all users."""
        raise NotImplementedError

    def save(self, user: User) -> User:
        """Save user."""
        raise NotImplementedError

    def delete(self, user_id: int) -> bool:
        """Delete user."""
        raise NotImplementedError


class ProductRepository:
    """Product repository."""

    def find_by_id(self, product_id: str) -> Product | None:
        """Find product by ID."""
        raise NotImplementedError

    def find_all(self, limit: int = 10) -> list[Product]:
        """Find all products."""
        raise NotImplementedError

    def search(self, query: str, *, max_results: int = 100) -> list[Product]:
        """Search products (with keyword-only arguments)."""
        raise NotImplementedError


# =============================================================================
# Service classes
# =============================================================================


class UserService:
    """User service - for testing various method signatures."""

    def __init__(self, repository: UserRepository | None = None) -> None:
        """Constructor."""
        self._repository = repository

    # Basic methods
    def get_user(self, user_id: int) -> dict[str, Any]:
        """Get user - basic signature."""
        raise NotImplementedError

    def create_user(self, name: str, email: str) -> dict[str, Any]:
        """Create user - multiple parameters."""
        raise NotImplementedError

    def update_user(
        self,
        user_id: int,
        *,
        name: str | None = None,
        email: str | None = None,
    ) -> dict[str, Any]:
        """Update user - keyword-only arguments."""
        raise NotImplementedError

    def delete_user(self, user_id: int) -> bool:
        """Delete user - returns bool."""
        raise NotImplementedError

    # Async methods
    async def async_get_user(self, user_id: int) -> dict[str, Any]:
        """Async get user."""
        raise NotImplementedError

    async def async_create_user(self, name: str, email: str) -> dict[str, Any]:
        """Async create user."""
        raise NotImplementedError

    # Properties
    @property
    def connection_status(self) -> str:
        """Connection status property."""
        return "connected"

    @property
    def is_connected(self) -> bool:
        """Connection status."""
        return True

    # Class methods
    @classmethod
    def from_config(cls, config: dict[str, Any]) -> "UserService":
        """Create service from config."""
        return cls()

    # Static methods
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email."""
        return "@" in email


# =============================================================================
# Complex types for advanced testing
# =============================================================================


class GenericService(Generic[T]):
    """Generic service - for testing generic types."""

    def get(self, id: int) -> T | None:
        """Generic get."""
        raise NotImplementedError

    def get_all(self) -> list[T]:
        """Generic get all."""
        raise NotImplementedError

    def save(self, item: T) -> T:
        """Generic save."""
        raise NotImplementedError


class NestedService:
    """Nested service - for testing nested mocks."""

    def __init__(self) -> None:
        """Constructor."""
        self.user_service = UserService()
        self.product_repo = ProductRepository()

    def get_user_products(self, user_id: int) -> list[Product]:
        """Get user's products."""
        raise NotImplementedError

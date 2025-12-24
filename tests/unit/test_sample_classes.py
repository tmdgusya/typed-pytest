"""샘플 클래스 테스트 - 테스트 인프라 검증용."""

import pytest

from tests.fixtures.sample_classes import (
    Product,
    ProductRepository,
    User,
    UserRepository,
    UserService,
)


class TestUser:
    """User 데이터클래스 테스트."""

    def test_user_creation(self) -> None:
        """User 인스턴스 생성."""
        user = User(id=1, name="John", email="john@example.com")
        assert user.id == 1
        assert user.name == "John"
        assert user.email == "john@example.com"

    def test_user_optional_email(self) -> None:
        """이메일 없이 User 생성."""
        user = User(id=1, name="John")
        assert user.email is None


class TestProduct:
    """Product 데이터클래스 테스트."""

    def test_product_creation(self) -> None:
        """Product 인스턴스 생성."""
        product = Product(id="P001", name="Widget", price=9.99)
        assert product.id == "P001"
        assert product.name == "Widget"
        assert product.price == 9.99


class TestUserService:
    """UserService 테스트."""

    def test_service_creation(self) -> None:
        """서비스 인스턴스 생성."""
        service = UserService()
        assert service is not None

    def test_service_with_repository(self) -> None:
        """Create service with repository."""
        repo = UserRepository()
        service = UserService(repository=repo)
        # Verify internal attribute (for testing purposes)
        assert service._repository is repo  # noqa: SLF001

    def test_connection_status_property(self) -> None:
        """connection_status 프로퍼티 접근."""
        service = UserService()
        assert service.connection_status == "connected"

    def test_is_connected_property(self) -> None:
        """is_connected 프로퍼티 접근."""
        service = UserService()
        assert service.is_connected is True

    def test_validate_email_static_method(self) -> None:
        """validate_email 스태틱 메소드."""
        assert UserService.validate_email("test@example.com") is True
        assert UserService.validate_email("invalid") is False

    def test_from_config_class_method(self) -> None:
        """from_config 클래스 메소드."""
        service = UserService.from_config({})
        assert isinstance(service, UserService)

    def test_get_user_raises_not_implemented(self) -> None:
        """get_user가 NotImplementedError를 발생시키는지."""
        service = UserService()
        with pytest.raises(NotImplementedError):
            service.get_user(1)

    def test_create_user_raises_not_implemented(self) -> None:
        """create_user가 NotImplementedError를 발생시키는지."""
        service = UserService()
        with pytest.raises(NotImplementedError):
            service.create_user("John", "john@example.com")


class TestUserRepository:
    """UserRepository 테스트."""

    def test_repository_methods_raise_not_implemented(self) -> None:
        """모든 메소드가 NotImplementedError를 발생시키는지."""
        repo = UserRepository()

        with pytest.raises(NotImplementedError):
            repo.find_by_id(1)

        with pytest.raises(NotImplementedError):
            repo.find_all()

        with pytest.raises(NotImplementedError):
            repo.save(User(id=1, name="Test"))

        with pytest.raises(NotImplementedError):
            repo.delete(1)


class TestProductRepository:
    """ProductRepository 테스트."""

    def test_repository_methods_raise_not_implemented(self) -> None:
        """모든 메소드가 NotImplementedError를 발생시키는지."""
        repo = ProductRepository()

        with pytest.raises(NotImplementedError):
            repo.find_by_id("P001")

        with pytest.raises(NotImplementedError):
            repo.find_all()

        with pytest.raises(NotImplementedError):
            repo.search("widget")

"""실제 사용 시나리오 테스트 (T203).

실제 프로젝트에서 typed-pytest를 사용하는 패턴들을 테스트합니다.
이 테스트들은 문서용 예제로도 사용됩니다.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest

from tests.fixtures.sample_classes import ProductRepository, UserService
from typed_pytest._mock import TypedMock


if TYPE_CHECKING:
    from typed_pytest._mocker import TypedMocker


# ============================================================================
# Scenario 1: Service-Repository Pattern
# ============================================================================


class OrderService:
    """예제용 주문 서비스."""

    def __init__(
        self, user_service: UserService, product_repo: ProductRepository
    ) -> None:
        self.user_service = user_service
        self.product_repo = product_repo

    def create_order(
        self, user_id: int, product_id: str, quantity: int
    ) -> dict[str, Any]:
        """주문을 생성합니다."""
        user = self.user_service.get_user(user_id)
        if not user:
            raise ValueError("User not found")

        product = self.product_repo.find_by_id(product_id)
        if not product:
            raise ValueError("Product not found")

        return {
            "user_id": user_id,
            "product_id": product_id,
            "quantity": quantity,
            "total": product.get("price", 0) * quantity,
        }


class TestServiceRepositoryPattern:
    """Service-Repository pattern tests.

    Example:
        This pattern is used in typical architectures where the service layer
        depends on the repository (data access layer) layer.
    """

    def test_service_with_mocked_dependencies(self, typed_mocker: TypedMocker) -> None:
        """Test replacing service dependencies with mocks."""
        # Arrange
        mock_user_service = typed_mocker.mock(UserService)
        mock_product_repo = typed_mocker.mock(ProductRepository)

        mock_user_service.get_user.return_value = {"id": 1, "name": "Test User"}
        mock_product_repo.find_by_id.return_value = {
            "id": "P001",
            "name": "Test Product",
            "price": 100,
        }

        order_service = OrderService(mock_user_service, mock_product_repo)

        # Act
        order = order_service.create_order(1, "P001", 2)

        # Assert
        assert order["total"] == 200
        mock_user_service.get_user.assert_called_once_with(1)
        mock_product_repo.find_by_id.assert_called_once_with("P001")

    def test_service_handles_user_not_found(self, typed_mocker: TypedMocker) -> None:
        """Test when user is not found."""
        mock_user_service = typed_mocker.mock(UserService)
        mock_product_repo = typed_mocker.mock(ProductRepository)

        mock_user_service.get_user.return_value = None

        order_service = OrderService(mock_user_service, mock_product_repo)

        with pytest.raises(ValueError, match="User not found"):
            order_service.create_order(999, "P001", 1)


# ============================================================================
# Scenario 2: External API Client Mock
# ============================================================================


class HttpClient:
    """예제용 HTTP 클라이언트."""

    def get(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """GET 요청을 수행합니다."""
        raise NotImplementedError("Real implementation would make HTTP request")

    def post(self, url: str, data: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
        """POST 요청을 수행합니다."""
        raise NotImplementedError("Real implementation would make HTTP request")


class WeatherService:
    """예제용 날씨 서비스."""

    def __init__(self, http_client: HttpClient) -> None:
        self.client = http_client

    def get_weather(self, city: str) -> dict[str, Any]:
        """도시의 날씨를 조회합니다."""
        response = self.client.get(f"https://api.weather.com/{city}")
        return {
            "city": city,
            "temperature": response.get("temp"),
            "condition": response.get("condition"),
        }


class TestExternalApiMock:
    """External API client mock tests.

    Example:
        Mock external API calls to test without network dependencies.
    """

    def test_weather_service_with_mocked_client(
        self, typed_mocker: TypedMocker
    ) -> None:
        """Test weather service with mocked HTTP client."""
        mock_client = typed_mocker.mock(HttpClient)
        mock_client.get.return_value = {
            "temp": 25,
            "condition": "sunny",
        }

        weather_service = WeatherService(mock_client)
        result = weather_service.get_weather("Seoul")

        assert result["city"] == "Seoul"
        assert result["temperature"] == 25
        assert result["condition"] == "sunny"
        mock_client.get.assert_called_once_with("https://api.weather.com/Seoul")

    def test_api_error_handling(self, typed_mocker: TypedMocker) -> None:
        """Test API error handling."""
        mock_client = typed_mocker.mock(HttpClient)
        mock_client.get.side_effect = ConnectionError("Network error")

        weather_service = WeatherService(mock_client)

        with pytest.raises(ConnectionError, match="Network error"):
            weather_service.get_weather("Tokyo")


# ============================================================================
# Scenario 3: side_effect Usage
# ============================================================================


class TestSideEffectUsage:
    """side_effect를 활용한 다양한 테스트 패턴."""

    def test_sequential_return_values(self, typed_mocker: TypedMocker) -> None:
        """순차적인 반환값 테스트."""
        mock = typed_mocker.mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            {"id": 2, "name": "Second"},
            {"id": 3, "name": "Third"},
        ]

        assert mock.get_user(1)["name"] == "First"
        assert mock.get_user(2)["name"] == "Second"
        assert mock.get_user(3)["name"] == "Third"

    def test_side_effect_with_exception_in_sequence(
        self, typed_mocker: TypedMocker
    ) -> None:
        """시퀀스 중간에 예외 발생 테스트."""
        mock = typed_mocker.mock(UserService)
        mock.get_user.side_effect = [
            {"id": 1, "name": "First"},
            ValueError("User not found"),
            {"id": 3, "name": "Third"},
        ]

        assert mock.get_user(1)["name"] == "First"

        with pytest.raises(ValueError, match="User not found"):
            mock.get_user(2)

        assert mock.get_user(3)["name"] == "Third"

    def test_side_effect_with_callable(self, typed_mocker: TypedMocker) -> None:
        """callable을 side_effect로 사용하는 테스트."""
        mock = typed_mocker.mock(UserService)

        def dynamic_response(user_id: int) -> dict[str, Any]:
            if user_id < 0:
                raise ValueError("Invalid user ID")
            return {"id": user_id, "name": f"User {user_id}"}

        mock.get_user.side_effect = dynamic_response

        assert mock.get_user(1)["name"] == "User 1"
        assert mock.get_user(42)["name"] == "User 42"

        with pytest.raises(ValueError, match="Invalid user ID"):
            mock.get_user(-1)


# ============================================================================
# Scenario 4: Multiple Mock Combinations
# ============================================================================


class TestMultipleMocksCombination:
    """Tests using multiple mocks together."""

    def test_complex_scenario_with_multiple_mocks(
        self, typed_mocker: TypedMocker
    ) -> None:
        """Using multiple mocks in a complex scenario."""
        # Create multiple service mocks
        mock_user_service = typed_mocker.mock(UserService)
        mock_product_repo = typed_mocker.mock(ProductRepository)
        mock_http_client = typed_mocker.mock(HttpClient)

        # Configure each mock
        mock_user_service.get_user.return_value = {"id": 1, "name": "Test"}
        mock_product_repo.find_all.return_value = [
            {"id": "P001", "name": "Product 1"},
            {"id": "P002", "name": "Product 2"},
        ]
        mock_http_client.post.return_value = {"status": "success"}

        # Verify
        user = mock_user_service.get_user(1)
        products = mock_product_repo.find_all()
        response = mock_http_client.post("/api/order", {"user_id": 1})

        assert user["name"] == "Test"
        assert len(products) == 2
        assert response["status"] == "success"

        # Verify all calls
        mock_user_service.get_user.assert_called_once()
        mock_product_repo.find_all.assert_called_once()
        mock_http_client.post.assert_called_once()


# ============================================================================
# Scenario 5: Spy Usage
# ============================================================================


class TestSpyUsage:
    """Spy usage patterns."""

    def test_spy_tracks_real_method_calls(self, typed_mocker: TypedMocker) -> None:
        """Test spy tracks real method calls."""
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        # Call real method (original behavior preserved)
        result1 = service.validate_email("test@example.com")
        result2 = service.validate_email("invalid-email")

        # Verify original behavior
        assert result1 is True
        assert result2 is False

        # Verify call tracking
        assert spy.call_count == 2
        spy.assert_any_call("test@example.com")
        spy.assert_any_call("invalid-email")

    def test_spy_on_internal_method(self, typed_mocker: TypedMocker) -> None:
        """Test spy for internal method call verification."""
        service = UserService()
        spy = typed_mocker.spy(service, "validate_email")

        # Can verify if validate_email was called inside create_user
        # (Whether it's actually called depends on UserService implementation)
        service.validate_email("user@test.com")

        spy.assert_called_once_with("user@test.com")


# ============================================================================
# Scenario 6: Using with patch
# ============================================================================


class TestPatchIntegration:
    """Integration tests using patch."""

    def test_patch_module_level_class(self, typed_mocker: TypedMocker) -> None:
        """Test patching module-level class."""
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 1, "name": "Patched User"}

        from tests.fixtures import sample_classes  # noqa: PLC0415

        # Use patched class
        result = sample_classes.UserService.get_user(1)
        assert result["name"] == "Patched User"

    def test_patch_object_for_single_method(self, typed_mocker: TypedMocker) -> None:
        """Test patching single method only."""
        import os  # noqa: PLC0415

        mock = typed_mocker.patch_object(os.path, "exists")
        mock.return_value = True

        # Use patched function
        assert os.path.exists("/nonexistent/path") is True  # noqa: PTH110
        mock.assert_called_once_with("/nonexistent/path")


# ============================================================================
# Scenario 7: Type Safety Verification
# ============================================================================


class TestTypeSafety:
    """Type safety tests."""

    def test_typed_mock_preserves_type_info(self, typed_mocker: TypedMocker) -> None:
        """Test TypedMock preserves type info."""
        mock = typed_mocker.mock(UserService)

        assert isinstance(mock, TypedMock)
        assert mock.typed_class is UserService

    def test_mock_has_original_methods(self, typed_mocker: TypedMocker) -> None:
        """Test mock has original class methods."""
        mock = typed_mocker.mock(UserService)

        # Original class methods should exist
        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")
        assert hasattr(mock, "delete_user")
        assert hasattr(mock, "validate_email")

    def test_spec_set_prevents_typos(self, typed_mocker: TypedMocker) -> None:
        """Test spec_set prevents typos."""
        mock = typed_mocker.mock(UserService, spec_set=True)

        # Accessing non-existent method should error
        with pytest.raises(AttributeError):
            _ = mock.nonexistent_method


# ============================================================================
# Scenario 8: Assertion Methods Usage
# ============================================================================


class TestAssertionMethods:
    """Various assertion method usage tests."""

    def test_assert_called_variations(self, typed_mocker: TypedMocker) -> None:
        """Test various assert_called variations."""
        mock = typed_mocker.mock(UserService)

        # Before call
        mock.get_user.assert_not_called()

        # First call
        mock.get_user(1)
        mock.get_user.assert_called()
        mock.get_user.assert_called_once()
        mock.get_user.assert_called_with(1)
        mock.get_user.assert_called_once_with(1)

        # Second call
        mock.get_user(2)
        mock.get_user.assert_called()
        assert mock.get_user.call_count == 2
        mock.get_user.assert_any_call(1)
        mock.get_user.assert_any_call(2)

    def test_call_args_inspection(self, typed_mocker: TypedMocker) -> None:
        """Inspect call arguments via call_args."""
        mock = typed_mocker.mock(UserService)

        mock.create_user("John", "john@example.com")

        # Verify last call arguments
        assert mock.create_user.call_args is not None
        args, _kwargs = mock.create_user.call_args
        assert args == ("John", "john@example.com")

    def test_call_args_list_inspection(self, typed_mocker: TypedMocker) -> None:
        """Inspect all calls via call_args_list."""
        mock = typed_mocker.mock(UserService)

        mock.get_user(1)
        mock.get_user(2)
        mock.get_user(3)

        assert len(mock.get_user.call_args_list) == 3
        assert mock.get_user.call_args_list[0].args == (1,)
        assert mock.get_user.call_args_list[1].args == (2,)
        assert mock.get_user.call_args_list[2].args == (3,)

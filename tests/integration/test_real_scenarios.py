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
# 시나리오 1: 서비스-리포지토리 패턴
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
    """서비스-리포지토리 패턴 테스트.

    Example:
        이 패턴은 서비스 레이어가 리포지토리(데이터 접근 레이어)에
        의존하는 일반적인 아키텍처에서 사용됩니다.
    """

    def test_service_with_mocked_dependencies(self, typed_mocker: TypedMocker) -> None:
        """서비스의 의존성을 mock으로 대체하는 테스트."""
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
        """사용자를 찾을 수 없는 경우 테스트."""
        mock_user_service = typed_mocker.mock(UserService)
        mock_product_repo = typed_mocker.mock(ProductRepository)

        mock_user_service.get_user.return_value = None

        order_service = OrderService(mock_user_service, mock_product_repo)

        with pytest.raises(ValueError, match="User not found"):
            order_service.create_order(999, "P001", 1)


# ============================================================================
# 시나리오 2: 외부 API 클라이언트 Mock
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
    """외부 API 클라이언트 mock 테스트.

    Example:
        외부 API 호출을 mock하여 네트워크 의존성 없이 테스트합니다.
    """

    def test_weather_service_with_mocked_client(
        self, typed_mocker: TypedMocker
    ) -> None:
        """HTTP 클라이언트를 mock하여 날씨 서비스 테스트."""
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
        """API 에러 상황 테스트."""
        mock_client = typed_mocker.mock(HttpClient)
        mock_client.get.side_effect = ConnectionError("Network error")

        weather_service = WeatherService(mock_client)

        with pytest.raises(ConnectionError, match="Network error"):
            weather_service.get_weather("Tokyo")


# ============================================================================
# 시나리오 3: side_effect 활용
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
# 시나리오 4: 여러 mock 조합
# ============================================================================


class TestMultipleMocksCombination:
    """여러 mock을 조합하여 사용하는 테스트."""

    def test_complex_scenario_with_multiple_mocks(
        self, typed_mocker: TypedMocker
    ) -> None:
        """복잡한 시나리오에서 여러 mock 사용."""
        # 여러 서비스 mock 생성
        mock_user_service = typed_mocker.mock(UserService)
        mock_product_repo = typed_mocker.mock(ProductRepository)
        mock_http_client = typed_mocker.mock(HttpClient)

        # 각 mock 설정
        mock_user_service.get_user.return_value = {"id": 1, "name": "Test"}
        mock_product_repo.find_all.return_value = [
            {"id": "P001", "name": "Product 1"},
            {"id": "P002", "name": "Product 2"},
        ]
        mock_http_client.post.return_value = {"status": "success"}

        # 검증
        user = mock_user_service.get_user(1)
        products = mock_product_repo.find_all()
        response = mock_http_client.post("/api/order", {"user_id": 1})

        assert user["name"] == "Test"
        assert len(products) == 2
        assert response["status"] == "success"

        # 모든 호출 검증
        mock_user_service.get_user.assert_called_once()
        mock_product_repo.find_all.assert_called_once()
        mock_http_client.post.assert_called_once()


# ============================================================================
# 시나리오 5: spy 활용
# ============================================================================


class TestSpyUsage:
    """spy를 활용한 테스트 패턴."""

    def test_spy_tracks_real_method_calls(self, typed_mocker: TypedMocker) -> None:
        """spy가 실제 메소드 호출을 추적하는지 테스트."""
        service = UserService()

        spy = typed_mocker.spy(service, "validate_email")

        # 실제 메소드 호출 (원본 동작 유지)
        result1 = service.validate_email("test@example.com")
        result2 = service.validate_email("invalid-email")

        # 원본 동작 확인
        assert result1 is True
        assert result2 is False

        # 호출 추적 확인
        assert spy.call_count == 2
        spy.assert_any_call("test@example.com")
        spy.assert_any_call("invalid-email")

    def test_spy_on_internal_method(self, typed_mocker: TypedMocker) -> None:
        """내부 메소드 호출 확인을 위한 spy 사용."""
        service = UserService()
        spy = typed_mocker.spy(service, "validate_email")

        # create_user 내부에서 validate_email이 호출되는지 확인할 수 있음
        # (실제로 호출되는지는 UserService 구현에 따름)
        service.validate_email("user@test.com")

        spy.assert_called_once_with("user@test.com")


# ============================================================================
# 시나리오 6: patch와 함께 사용
# ============================================================================


class TestPatchIntegration:
    """patch를 활용한 통합 테스트 패턴."""

    def test_patch_module_level_class(self, typed_mocker: TypedMocker) -> None:
        """모듈 레벨 클래스를 patch하는 테스트."""
        mock = typed_mocker.patch(
            "tests.fixtures.sample_classes.UserService",
            new=UserService,
        )
        mock.get_user.return_value = {"id": 1, "name": "Patched User"}

        from tests.fixtures import sample_classes  # noqa: PLC0415

        # 패치된 클래스 사용
        result = sample_classes.UserService.get_user(1)
        assert result["name"] == "Patched User"

    def test_patch_object_for_single_method(self, typed_mocker: TypedMocker) -> None:
        """단일 메소드만 patch하는 테스트."""
        import os  # noqa: PLC0415

        mock = typed_mocker.patch_object(os.path, "exists")
        mock.return_value = True

        # 패치된 함수 사용
        assert os.path.exists("/nonexistent/path") is True  # noqa: PTH110
        mock.assert_called_once_with("/nonexistent/path")


# ============================================================================
# 시나리오 7: 타입 안전성 검증
# ============================================================================


class TestTypeSafety:
    """타입 안전성 관련 테스트."""

    def test_typed_mock_preserves_type_info(self, typed_mocker: TypedMocker) -> None:
        """TypedMock이 타입 정보를 보존하는지 테스트."""
        mock = typed_mocker.mock(UserService)

        assert isinstance(mock, TypedMock)
        assert mock.typed_class is UserService

    def test_mock_has_original_methods(self, typed_mocker: TypedMocker) -> None:
        """mock이 원본 클래스의 메소드를 가지는지 테스트."""
        mock = typed_mocker.mock(UserService)

        # 원본 클래스의 메소드들이 존재해야 함
        assert hasattr(mock, "get_user")
        assert hasattr(mock, "create_user")
        assert hasattr(mock, "delete_user")
        assert hasattr(mock, "validate_email")

    def test_spec_set_prevents_typos(self, typed_mocker: TypedMocker) -> None:
        """spec_set이 오타를 방지하는지 테스트."""
        mock = typed_mocker.mock(UserService, spec_set=True)

        # 존재하지 않는 메소드 접근 시 에러
        with pytest.raises(AttributeError):
            _ = mock.nonexistent_method


# ============================================================================
# 시나리오 8: assertion 메소드 활용
# ============================================================================


class TestAssertionMethods:
    """다양한 assertion 메소드 활용 테스트."""

    def test_assert_called_variations(self, typed_mocker: TypedMocker) -> None:
        """다양한 assert_called 변형 테스트."""
        mock = typed_mocker.mock(UserService)

        # 호출 전
        mock.get_user.assert_not_called()

        # 첫 번째 호출
        mock.get_user(1)
        mock.get_user.assert_called()
        mock.get_user.assert_called_once()
        mock.get_user.assert_called_with(1)
        mock.get_user.assert_called_once_with(1)

        # 두 번째 호출
        mock.get_user(2)
        mock.get_user.assert_called()
        assert mock.get_user.call_count == 2
        mock.get_user.assert_any_call(1)
        mock.get_user.assert_any_call(2)

    def test_call_args_inspection(self, typed_mocker: TypedMocker) -> None:
        """call_args를 통한 호출 인자 검사."""
        mock = typed_mocker.mock(UserService)

        mock.create_user("John", "john@example.com")

        # 마지막 호출의 인자 확인
        assert mock.create_user.call_args is not None
        args, _kwargs = mock.create_user.call_args
        assert args == ("John", "john@example.com")

    def test_call_args_list_inspection(self, typed_mocker: TypedMocker) -> None:
        """call_args_list를 통한 모든 호출 검사."""
        mock = typed_mocker.mock(UserService)

        mock.get_user(1)
        mock.get_user(2)
        mock.get_user(3)

        assert len(mock.get_user.call_args_list) == 3
        assert mock.get_user.call_args_list[0].args == (1,)
        assert mock.get_user.call_args_list[1].args == (2,)
        assert mock.get_user.call_args_list[2].args == (3,)

"""공개 API 테스트."""

from unittest.mock import MagicMock

import typed_pytest
from typed_pytest import (
    AsyncMockedMethod,
    AsyncMockProtocol,
    MockedMethod,
    MockProtocol,
    TypedMock,
    __version__,
    typed_mock,
)


class TestPublicAPIImports:
    """공개 API 임포트 테스트."""

    def test_typed_mock_importable(self) -> None:
        """TypedMock을 임포트할 수 있는지 확인."""
        assert TypedMock is not None

    def test_mocked_method_importable(self) -> None:
        """MockedMethod를 임포트할 수 있는지 확인."""
        assert MockedMethod is not None

    def test_async_mocked_method_importable(self) -> None:
        """AsyncMockedMethod를 임포트할 수 있는지 확인."""
        assert AsyncMockedMethod is not None

    def test_typed_mock_factory_importable(self) -> None:
        """typed_mock 팩토리 함수를 임포트할 수 있는지 확인."""
        assert typed_mock is not None
        assert callable(typed_mock)

    def test_mock_protocol_importable(self) -> None:
        """MockProtocol을 임포트할 수 있는지 확인."""
        assert MockProtocol is not None

    def test_async_mock_protocol_importable(self) -> None:
        """AsyncMockProtocol을 임포트할 수 있는지 확인."""
        assert AsyncMockProtocol is not None

    def test_version_importable(self) -> None:
        """__version__을 임포트할 수 있는지 확인."""
        assert __version__ is not None
        assert isinstance(__version__, str)

    def test_all_imports_available(self) -> None:
        """모든 공개 API가 사용 가능한지 확인."""
        assert TypedMock is not None
        assert MockedMethod is not None
        assert AsyncMockedMethod is not None
        assert typed_mock is not None
        assert MockProtocol is not None
        assert AsyncMockProtocol is not None
        assert __version__ is not None


class TestAllMatchesExports:
    """__all__과 실제 export가 일치하는지 테스트."""

    def test_all_items_are_exported(self) -> None:
        """__all__의 모든 항목이 실제로 export되는지 확인."""
        for name in typed_pytest.__all__:
            assert hasattr(typed_pytest, name), f"{name} is in __all__ but not exported"

    def test_all_contains_expected_items(self) -> None:
        """__all__에 예상되는 항목이 포함되어 있는지 확인."""
        expected = [
            "TypedMock",
            "MockedMethod",
            "AsyncMockedMethod",
            "typed_mock",
            "MockProtocol",
            "AsyncMockProtocol",
            "__version__",
        ]
        for item in expected:
            assert item in typed_pytest.__all__, f"{item} is not in __all__"

    def test_no_private_items_in_all(self) -> None:
        """Verify no private items are in __all__."""
        for name in typed_pytest.__all__:
            # __version__ is an exception
            if name == "__version__":
                continue
            assert not name.startswith("_"), f"{name} is private but in __all__"


class TestPublicAPITypes:
    """Public API type tests."""

    def test_typed_mock_is_class(self) -> None:
        """Verify TypedMock is a class."""
        assert isinstance(TypedMock, type)

    def test_mocked_method_is_class(self) -> None:
        """Verify MockedMethod is a class."""
        assert isinstance(MockedMethod, type)

    def test_async_mocked_method_is_class(self) -> None:
        """Verify AsyncMockedMethod is a class."""
        assert isinstance(AsyncMockedMethod, type)

    def test_typed_mock_factory_is_callable(self) -> None:
        """Verify typed_mock is callable."""
        assert callable(typed_mock)

    def test_mock_protocol_is_protocol(self) -> None:
        """Verify MockProtocol is a Protocol."""
        # If runtime_checkable decorator is applied, _is_runtime_protocol is True
        assert getattr(MockProtocol, "_is_runtime_protocol", False)

    def test_async_mock_protocol_is_protocol(self) -> None:
        """Verify AsyncMockProtocol is a Protocol."""
        assert getattr(AsyncMockProtocol, "_is_runtime_protocol", False)


class TestPublicAPIUsability:
    """공개 API 사용성 테스트."""

    def test_typed_mock_can_create_mock(self) -> None:
        """TypedMock으로 mock을 생성할 수 있는지 확인."""

        class SampleService:
            def method(self) -> str:
                return "result"

        mock = TypedMock(spec=SampleService)
        assert mock is not None
        assert hasattr(mock, "method")

    def test_typed_mock_factory_can_create_mock(self) -> None:
        """typed_mock 팩토리로 mock을 생성할 수 있는지 확인."""

        class SampleService:
            def method(self) -> str:
                return "result"

        mock = typed_mock(SampleService)
        assert mock is not None
        assert hasattr(mock, "method")

    def test_mocked_method_wraps_magic_mock(self) -> None:
        """MockedMethod가 MagicMock을 래핑할 수 있는지 확인."""
        underlying_mock = MagicMock()
        method = MockedMethod(underlying_mock)

        method("arg1", kwarg="value")
        underlying_mock.assert_called_once_with("arg1", kwarg="value")

    def test_mock_protocol_is_satisfied_by_magic_mock(self) -> None:
        """MockProtocol이 MagicMock에 의해 만족되는지 확인."""
        mock = MagicMock()
        assert isinstance(mock, MockProtocol)


class TestVersionInfo:
    """Version info tests."""

    def test_version_format(self) -> None:
        """Verify version format is correct."""
        # Version should be in major.minor.patch format
        parts = __version__.split(".")
        assert len(parts) >= 2, "Version should have at least major.minor"

    def test_version_is_semver(self) -> None:
        """Verify version follows SemVer."""
        # Basic SemVer validation
        parts = __version__.split(".")
        # First part should be numeric (major)
        assert parts[0].isdigit(), "Major version should be numeric"


class TestBackwardsCompatibility:
    """Backwards compatibility tests."""

    def test_phase2_exports_available(self) -> None:
        """Verify Phase 2 exports are added (T200 complete)."""
        # T200: TypedMocker class implementation complete
        assert hasattr(typed_pytest, "TypedMocker")
        # typed_mocker fixture is T201 (not yet implemented)
        assert not hasattr(typed_pytest, "typed_mocker")

    def test_phase2_in_all(self) -> None:
        """Verify Phase 2 exports are in __all__."""
        # T200: TypedMocker class
        assert "TypedMocker" in typed_pytest.__all__
        # T201: typed_mocker fixture is not yet implemented
        assert "typed_mocker" not in typed_pytest.__all__

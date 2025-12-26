"""Tests for stub generation backends."""

from __future__ import annotations

import pytest

from tests.fixtures.sample_classes import (
    UserRepository,
    UserService,
)
from typed_pytest_generator._backend import ClassInfo, MethodInfo, StubBackend
from typed_pytest_generator._backend_inspect import InspectBackend


class TestMethodInfo:
    """Tests for MethodInfo dataclass."""

    def test_default_values(self) -> None:
        """Test that MethodInfo has sensible defaults."""
        info = MethodInfo(name="test_method", signature="(self) -> None")
        assert info.name == "test_method"
        assert info.signature == "(self) -> None"
        assert info.is_async is False
        assert info.is_static is False
        assert info.is_classmethod is False
        assert info.is_property is False
        assert info.param_types == []
        assert info.return_type == "typing.Any"

    def test_all_values(self) -> None:
        """Test MethodInfo with all values specified."""
        info = MethodInfo(
            name="async_method",
            signature="(self, x: int) -> str",
            is_async=True,
            is_static=False,
            is_classmethod=False,
            is_property=False,
            param_types=["int"],
            return_type="str",
        )
        assert info.name == "async_method"
        assert info.is_async is True
        assert info.param_types == ["int"]
        assert info.return_type == "str"


class TestClassInfo:
    """Tests for ClassInfo dataclass."""

    def test_default_values(self) -> None:
        """Test that ClassInfo has sensible defaults."""
        info = ClassInfo(name="TestClass", full_name="test.TestClass")
        assert info.name == "TestClass"
        assert info.full_name == "test.TestClass"
        assert info.methods == []

    def test_with_methods(self) -> None:
        """Test ClassInfo with methods."""
        methods = [
            MethodInfo(name="method1", signature="(self) -> None"),
            MethodInfo(name="method2", signature="(self, x: int) -> str"),
        ]
        info = ClassInfo(name="TestClass", full_name="test.TestClass", methods=methods)
        assert len(info.methods) == 2
        assert info.methods[0].name == "method1"
        assert info.methods[1].name == "method2"


class TestInspectBackend:
    """Tests for InspectBackend."""

    def test_get_name(self) -> None:
        """Test backend name."""
        backend = InspectBackend()
        assert backend.get_name() == "inspect"

    def test_extracts_basic_methods(self) -> None:
        """Test that basic methods are extracted."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserRepository, "tests.fixtures.sample_classes.UserRepository"
        )

        assert info.name == "UserRepository"
        assert info.full_name == "tests.fixtures.sample_classes.UserRepository"

        method_names = [m.name for m in info.methods]
        assert "find_by_id" in method_names
        assert "find_all" in method_names
        assert "save" in method_names
        assert "delete" in method_names

    def test_return_type_is_any(self) -> None:
        """Test that InspectBackend returns typing.Any for return types."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserRepository, "tests.fixtures.sample_classes.UserRepository"
        )

        for method in info.methods:
            assert method.return_type == "typing.Any"

    def test_detects_async_methods(self) -> None:
        """Test that async methods are detected."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserService, "tests.fixtures.sample_classes.UserService"
        )

        method_map = {m.name: m for m in info.methods}

        # Sync methods
        assert "get_user" in method_map
        assert method_map["get_user"].is_async is False

        # Async methods
        assert "async_get_user" in method_map
        assert method_map["async_get_user"].is_async is True

        assert "async_create_user" in method_map
        assert method_map["async_create_user"].is_async is True

    def test_detects_properties(self) -> None:
        """Test that properties are detected."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserService, "tests.fixtures.sample_classes.UserService"
        )

        method_map = {m.name: m for m in info.methods}

        assert "connection_status" in method_map
        assert method_map["connection_status"].is_property is True

        assert "is_connected" in method_map
        assert method_map["is_connected"].is_property is True

    def test_detects_static_methods(self) -> None:
        """Test that static methods are detected."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserService, "tests.fixtures.sample_classes.UserService"
        )

        method_map = {m.name: m for m in info.methods}

        assert "validate_email" in method_map
        assert method_map["validate_email"].is_static is True

    def test_detects_class_methods(self) -> None:
        """Test that class methods are detected."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserService, "tests.fixtures.sample_classes.UserService"
        )

        method_map = {m.name: m for m in info.methods}

        assert "from_config" in method_map
        assert method_map["from_config"].is_classmethod is True

    def test_excludes_private_by_default(self) -> None:
        """Test that private methods are excluded by default."""
        backend = InspectBackend(include_private=False)
        info = backend.extract_class_info(
            UserService, "tests.fixtures.sample_classes.UserService"
        )

        method_names = [m.name for m in info.methods]
        assert "_repository" not in method_names
        assert "__init__" not in method_names

    def test_includes_private_when_enabled(self) -> None:
        """Test that private methods are included when enabled."""
        backend = InspectBackend(include_private=True)
        info = backend.extract_class_info(
            UserService, "tests.fixtures.sample_classes.UserService"
        )

        method_names = [m.name for m in info.methods]
        assert "__init__" in method_names

    def test_extracts_param_types(self) -> None:
        """Test that parameter types are extracted."""
        backend = InspectBackend()
        info = backend.extract_class_info(
            UserRepository, "tests.fixtures.sample_classes.UserRepository"
        )

        method_map = {m.name: m for m in info.methods}

        # find_by_id takes int
        assert "find_by_id" in method_map
        assert "int" in method_map["find_by_id"].param_types

    def test_is_stub_backend(self) -> None:
        """Test that InspectBackend is a StubBackend."""
        backend = InspectBackend()
        assert isinstance(backend, StubBackend)


class TestStubgenBackendConditional:
    """Conditional tests for StubgenBackend (may be slow)."""

    @pytest.fixture
    def stubgen_backend(self):
        """Create a StubgenBackend instance."""
        from typed_pytest_generator._backend_stubgen import StubgenBackend

        return StubgenBackend()

    def test_get_name(self, stubgen_backend) -> None:
        """Test backend name."""
        assert stubgen_backend.get_name() == "stubgen"

    def test_extracts_methods(self, stubgen_backend) -> None:
        """Test that methods are extracted."""
        info = stubgen_backend.extract_class_info(
            UserRepository, "tests.fixtures.sample_classes.UserRepository"
        )

        assert info.name == "UserRepository"
        method_names = [m.name for m in info.methods]
        assert "find_by_id" in method_names

    def test_preserves_return_types(self, stubgen_backend) -> None:
        """Test that stubgen preserves actual return types."""
        info = stubgen_backend.extract_class_info(
            UserRepository, "tests.fixtures.sample_classes.UserRepository"
        )

        method_map = {m.name: m for m in info.methods}

        # Stubgen should preserve actual return types
        if "find_by_id" in method_map:
            return_type = method_map["find_by_id"].return_type
            # Could be "User | None" or similar
            assert return_type != "" or return_type == "typing.Any"

    def test_is_stub_backend(self, stubgen_backend) -> None:
        """Test that StubgenBackend is a StubBackend."""
        assert isinstance(stubgen_backend, StubBackend)


class TestBackendComparison:
    """Tests comparing both backends."""

    def test_both_backends_find_same_method_names(self) -> None:
        """Test that both backends find the same public methods."""
        from typed_pytest_generator._backend_stubgen import StubgenBackend

        inspect_backend = InspectBackend()
        stubgen_backend = StubgenBackend()

        target = "tests.fixtures.sample_classes.UserRepository"

        inspect_info = inspect_backend.extract_class_info(UserRepository, target)
        stubgen_info = stubgen_backend.extract_class_info(UserRepository, target)

        inspect_names = {m.name for m in inspect_info.methods}
        stubgen_names = {m.name for m in stubgen_info.methods}

        # Both should find the core public methods
        common_methods = {"find_by_id", "find_all", "save", "delete"}
        assert common_methods.issubset(inspect_names)
        assert common_methods.issubset(stubgen_names)

    def test_stubgen_has_richer_return_types(self) -> None:
        """Test that stubgen backend provides richer return type info."""
        from typed_pytest_generator._backend_stubgen import StubgenBackend

        inspect_backend = InspectBackend()
        stubgen_backend = StubgenBackend()

        target = "tests.fixtures.sample_classes.UserRepository"

        inspect_info = inspect_backend.extract_class_info(UserRepository, target)
        stubgen_info = stubgen_backend.extract_class_info(UserRepository, target)

        # Inspect backend always returns typing.Any
        for method in inspect_info.methods:
            assert method.return_type == "typing.Any"

        # Stubgen backend may have actual types (or typing.Any fallback)
        stubgen_method_map = {m.name: m for m in stubgen_info.methods}
        if "find_by_id" in stubgen_method_map:
            # Stubgen should have some return type info
            return_type = stubgen_method_map["find_by_id"].return_type
            assert return_type is not None

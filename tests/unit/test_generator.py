"""Tests for typed-pytest-generator."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from typed_pytest_generator._generator import StubGenerator, generate_stubs
from typed_pytest_generator._inspector import MethodInfo, inspect_class


class TestInspectClass:
    """Tests for class inspection."""

    def test_inspects_regular_methods(self):
        """Regular methods are correctly identified."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService)

        method_names = [m.name for m in methods]
        assert "get_user" in method_names
        assert "create_user" in method_names
        assert "delete_user" in method_names

    def test_inspects_async_methods(self):
        """Async methods are correctly identified."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService)
        async_methods = [m for m in methods if m.method_type == "async"]

        async_names = [m.name for m in async_methods]
        assert "async_get_user" in async_names
        assert "async_create_user" in async_names

    def test_inspects_properties(self):
        """Properties are correctly identified."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService)
        properties = [m for m in methods if m.method_type == "property"]

        prop_names = [m.name for m in properties]
        assert "connection_status" in prop_names
        assert "is_connected" in prop_names

    def test_inspects_classmethods(self):
        """Class methods are correctly identified."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService)
        classmethods = [m for m in methods if m.method_type == "classmethod"]

        assert len(classmethods) == 1
        assert classmethods[0].name == "from_config"

    def test_inspects_staticmethods(self):
        """Static methods are correctly identified."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService)
        staticmethods = [m for m in methods if m.method_type == "staticmethod"]

        assert len(staticmethods) == 1
        assert staticmethods[0].name == "validate_email"

    def test_excludes_private_methods_by_default(self):
        """Private methods are excluded by default."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService)
        method_names = [m.name for m in methods]

        assert not any(name.startswith("_") for name in method_names)

    def test_includes_private_methods_when_enabled(self):
        """Private methods are included when flag is set."""
        from tests.fixtures.sample_classes import UserService

        methods = inspect_class(UserService, include_private=True)
        method_names = [m.name for m in methods]

        # __init__ should be included
        assert "__init__" in method_names


class TestStubGenerator:
    """Tests for stub generation."""

    def test_generates_stub_file(self):
        """Stub file is generated for specified class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generated = generator.generate()

            assert len(generated) == 2  # UserService.pyi + __init__.pyi

            stub_path = Path(tmpdir) / "UserService.pyi"
            assert stub_path.exists()

            content = stub_path.read_text()
            assert "UserService_TypedMock" in content
            assert "TypedMock" in content

    def test_generated_stub_contains_method_signatures(self):
        """Generated stub contains method signatures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            stub_path = Path(tmpdir) / "UserService.pyi"
            content = stub_path.read_text()

            # Check for method signatures
            assert "def get_user(self, user_id: int)" in content
            assert "MockedMethod" in content

    def test_generated_stub_handles_async(self):
        """Generated stub handles async methods correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            stub_path = Path(tmpdir) / "UserService.pyi"
            content = stub_path.read_text()

            assert "async def async_get_user" in content
            assert "AsyncMockedMethod" in content

    def test_generated_stub_handles_properties(self):
        """Generated stub handles properties correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            stub_path = Path(tmpdir) / "UserService.pyi"
            content = stub_path.read_text()

            assert "@property" in content
            assert "MockedProperty" in content

    def test_generates_init_file(self):
        """__init__.pyi is generated with exports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            init_path = Path(tmpdir) / "__init__.pyi"
            assert init_path.exists()

            content = init_path.read_text()
            assert "UserService_TypedMock" in content
            assert "UserServiceMock" in content
            assert "__all__" in content

    def test_generates_multiple_classes(self):
        """Multiple classes can be specified."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=[
                    "tests.fixtures.sample_classes.UserService",
                    "tests.fixtures.sample_classes.ProductRepository",
                ],
                output_dir=tmpdir,
            )
            generated = generator.generate()

            # Should generate 3 files: 2 class stubs + __init__.pyi
            assert len(generated) == 3

            # Both classes should exist
            user_stub = Path(tmpdir) / "UserService.pyi"
            product_stub = Path(tmpdir) / "ProductRepository.pyi"
            assert user_stub.exists()
            assert product_stub.exists()

    def test_handles_nonexistent_class(self):
        """Nonexistent class is handled gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.NonexistentClass"],
                output_dir=tmpdir,
            )
            # Should not raise exception
            generated = generator.generate()
            # No files generated for nonexistent class
            assert len(generated) == 0


class TestGenerateStubsFunction:
    """Tests for the convenience function."""

    def test_generate_stubs_convenience_function(self):
        """generate_stubs function works as expected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generated = generate_stubs(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )

            assert len(generated) == 2
            assert any(p.name == "UserService.pyi" for p in generated)
            assert any(p.name == "__init__.pyi" for p in generated)

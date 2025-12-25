"""Tests for typed-pytest-generator."""

from __future__ import annotations

import tempfile
from pathlib import Path

from typed_pytest_generator._generator import StubGenerator, generate_stubs
from typed_pytest_generator._inspector import inspect_class


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
        """Stub files are generated for specified class."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generated = generator.generate()

            # __init__.py + _runtime.py
            assert len(generated) == 2

            runtime_path = Path(tmpdir) / "_runtime.py"
            assert runtime_path.exists()

            content = runtime_path.read_text()
            assert "class UserService" in content
            assert "UserService_TypedMock" in content

    def test_generated_stub_contains_method_signatures(self):
        """Generated stub contains method signatures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            runtime_path = Path(tmpdir) / "_runtime.py"
            content = runtime_path.read_text()

            # Check for method signatures in _runtime.py
            assert "def get_user(self, user_id: int)" in content

    def test_generated_stub_handles_async(self):
        """Generated stub handles async methods correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            runtime_path = Path(tmpdir) / "_runtime.py"
            content = runtime_path.read_text()

            # Async methods are included in _runtime.py (as regular methods)
            assert "def async_get_user" in content

    def test_generated_stub_handles_properties(self):
        """Generated stub handles properties correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            # _runtime.py only includes callable methods, not properties
            runtime_path = Path(tmpdir) / "_runtime.py"
            assert runtime_path.exists()

    def test_generates_init_file(self):
        """__init__.py is generated with exports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_classes.UserService"],
                output_dir=tmpdir,
            )
            generator.generate()

            init_path = Path(tmpdir) / "__init__.py"
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

            # __init__.py + _runtime.py
            assert len(generated) == 2

            # Both classes should exist in _runtime.py
            runtime_path = Path(tmpdir) / "_runtime.py"
            content = runtime_path.read_text()
            assert "class UserService" in content
            assert "class ProductRepository" in content

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
            assert any(p.name == "__init__.py" for p in generated)
            assert any(p.name == "_runtime.py" for p in generated)

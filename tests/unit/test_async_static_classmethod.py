"""Test async staticmethod and classmethod detection in stub generation."""

import shutil
import tempfile
from pathlib import Path

from typed_pytest_generator._generator import StubGenerator


class ServiceWithAsyncStaticAndClassMethods:
    """Test class with async staticmethod and classmethod."""

    @staticmethod
    async def async_static_method(value: int) -> str:
        """Async static method."""
        return str(value)

    @classmethod
    async def async_class_method(cls, name: str) -> dict:
        """Async class method."""
        return {"name": name}

    @staticmethod
    def sync_static_method(value: int) -> str:
        """Sync static method."""
        return str(value)

    @classmethod
    def sync_class_method(cls, name: str) -> dict:
        """Sync class method."""
        return {"name": name}

    async def async_instance_method(self, data: str) -> list:
        """Async instance method."""
        return [data]


class TestAsyncStaticAndClassMethodStubGeneration:
    """Test that async staticmethod and classmethod are correctly detected."""

    def test_async_staticmethod_generates_async_def(self) -> None:
        """Async staticmethod should generate 'async def' in stub."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=[
                    "tests.unit.test_async_static_classmethod.ServiceWithAsyncStaticAndClassMethods"
                ],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # Should have async def for async_static_method
            assert "async def async_static_method" in content, (
                f"Expected 'async def async_static_method' in generated stub.\n"
                f"Content:\n{content}"
            )
        finally:
            shutil.rmtree(output_dir)

    def test_async_classmethod_generates_async_def(self) -> None:
        """Async classmethod should generate 'async def' in stub."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=[
                    "tests.unit.test_async_static_classmethod.ServiceWithAsyncStaticAndClassMethods"
                ],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # Should have async def for async_class_method
            assert "async def async_class_method" in content, (
                f"Expected 'async def async_class_method' in generated stub.\n"
                f"Content:\n{content}"
            )
        finally:
            shutil.rmtree(output_dir)

    def test_async_staticmethod_uses_async_mocked_method(self) -> None:
        """Async staticmethod should use AsyncMockedMethod in TypedMock stub."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=[
                    "tests.unit.test_async_static_classmethod.ServiceWithAsyncStaticAndClassMethods"
                ],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # Should use AsyncMockedMethod for async_static_method
            assert "async_static_method" in content
            assert "def async_static_method(self) -> AsyncMockedMethod" in content, (
                f"Expected AsyncMockedMethod for async_static_method.\n"
                f"Content:\n{content}"
            )
        finally:
            shutil.rmtree(output_dir)

    def test_sync_staticmethod_stays_sync(self) -> None:
        """Sync staticmethod should NOT generate 'async def'."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=[
                    "tests.unit.test_async_static_classmethod.ServiceWithAsyncStaticAndClassMethods"
                ],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # Should NOT have async def for sync_static_method
            assert "async def sync_static_method" not in content, (
                f"Did not expect 'async def sync_static_method' in generated stub.\n"
                f"Content:\n{content}"
            )
            # But should have regular def
            assert "def sync_static_method" in content
        finally:
            shutil.rmtree(output_dir)

    def test_sync_classmethod_stays_sync(self) -> None:
        """Sync classmethod should NOT generate 'async def'."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=[
                    "tests.unit.test_async_static_classmethod.ServiceWithAsyncStaticAndClassMethods"
                ],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # Should NOT have async def for sync_class_method
            assert "async def sync_class_method" not in content, (
                f"Did not expect 'async def sync_class_method' in generated stub.\n"
                f"Content:\n{content}"
            )
            # But should have regular def
            assert "def sync_class_method" in content
        finally:
            shutil.rmtree(output_dir)

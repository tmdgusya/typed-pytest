"""Test recursive wildcard pattern expansion."""

import shutil
import tempfile
from pathlib import Path

from typed_pytest_generator._generator import StubGenerator


class TestRecursiveWildcardExpansion:
    """Test ** pattern for recursive submodule scanning."""

    def test_recursive_wildcard_finds_all_submodule_classes(self) -> None:
        """** pattern should find classes in all submodules recursively."""
        generator = StubGenerator(
            targets=["tests.fixtures.sample_package.**"],
            output_dir=Path(tempfile.mkdtemp()),
        )

        expanded = generator._expand_targets(generator.targets)  # noqa: SLF001

        # Verify all expected classes are found
        assert "tests.fixtures.sample_package.PackageLevelClass" in expanded
        assert "tests.fixtures.sample_package.module_a.ClassA" in expanded
        assert "tests.fixtures.sample_package.module_b.ClassB" in expanded
        assert (
            "tests.fixtures.sample_package.subpackage.deep_module.DeepClass" in expanded
        )

    def test_single_wildcard_does_not_find_submodule_classes(self) -> None:
        """* pattern should NOT find classes in submodules."""
        generator = StubGenerator(
            targets=["tests.fixtures.sample_package.*"],
            output_dir=Path(tempfile.mkdtemp()),
        )

        expanded = generator._expand_targets(generator.targets)  # noqa: SLF001

        # Should only find classes from __init__.py
        assert "tests.fixtures.sample_package.PackageLevelClass" in expanded

        # Should NOT find classes from submodules
        assert "tests.fixtures.sample_package.module_a.ClassA" not in expanded
        assert "tests.fixtures.sample_package.module_b.ClassB" not in expanded
        assert (
            "tests.fixtures.sample_package.subpackage.deep_module.DeepClass"
            not in expanded
        )

    def test_recursive_wildcard_generates_stubs(self) -> None:
        """** pattern should generate stubs for all found classes."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=["tests.fixtures.sample_package.**"],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # All classes should be in the generated stub
            assert "class PackageLevelClass:" in content
            assert "class ClassA:" in content
            assert "class ClassB:" in content
            assert "class DeepClass:" in content

            # Async methods should be properly detected
            assert "async def async_method_a" in content
            assert "async def deep_async_method" in content
        finally:
            shutil.rmtree(output_dir)

    def test_module_level_wildcard_works(self) -> None:
        """* pattern on a module (not package) should find its classes."""
        generator = StubGenerator(
            targets=["tests.fixtures.sample_package.module_a.*"],
            output_dir=Path(tempfile.mkdtemp()),
        )

        expanded = generator._expand_targets(generator.targets)  # noqa: SLF001

        assert "tests.fixtures.sample_package.module_a.ClassA" in expanded
        assert len(expanded) == 1

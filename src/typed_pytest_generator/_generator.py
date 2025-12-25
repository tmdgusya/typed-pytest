"""Core stub generation logic for typed-pytest-generator."""

from __future__ import annotations

import ast
import inspect
import sys
from importlib import import_module
from pathlib import Path
from typing import Any, TypeVar, get_type_hints

from typed_pytest_generator._inspector import MethodInfo, inspect_class
from typed_pytest_generator._templates import generate_class_stub, generate_init_stub

T = TypeVar("T")


class StubGenerator:
    """Generates .pyi stub files for TypedMock with method signatures."""

    def __init__(
        self,
        targets: list[str],
        output_dir: str | Path = "typed_pytest_stubs",
        include_private: bool = False,
    ) -> None:
        """Initialize the stub generator.

        Args:
            targets: List of fully qualified class names (e.g., "mypkg.services.UserService")
            output_dir: Directory where stub files will be generated
            include_private: Whether to include private methods (starting with _)
        """
        self.targets = targets
        self.output_dir = Path(output_dir)
        self.include_private = include_private

    def generate(self) -> list[Path]:
        """Generate all stub files for configured targets.

        Returns:
            List of generated stub file paths
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        generated_files: list[Path] = []
        stubs: dict[str, str] = {}

        for target in self.targets:
            cls = self._import_class(target)
            if cls is None:
                print(f"[typed-pytest-generator] Warning: Could not import {target}", file=sys.stderr)
                continue

            stub_content = self._generate_stub(cls, target)
            if stub_content:
                class_name = cls.__name__
                stub_path = self.output_dir / f"{class_name}.pyi"
                stub_path.write_text(stub_content)
                generated_files.append(stub_path)
                stubs[class_name] = stub_content

        # Generate __init__.pyi
        if stubs:
            init_content = generate_init_stub(list(stubs.keys()))
            init_path = self.output_dir / "__init__.pyi"
            init_path.write_text(init_content)
            generated_files.append(init_path)

        return generated_files

    def _import_class(self, target: str) -> type | None:
        """Import the target class from a fully qualified string path.

        Args:
            target: Fully qualified class name (e.g., "mypkg.services.UserService")

        Returns:
            The imported class, or None if import failed
        """
        try:
            module_path, class_name = target.rsplit(".", 1)
            module = import_module(module_path)
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            print(f"[typed-pytest-generator] Error importing {target}: {e}", file=sys.stderr)
            return None

    def _generate_stub(self, cls: type, full_name: str) -> str | None:
        """Generate .pyi content for a single class.

        Args:
            cls: The class to generate stub for
            full_name: Fully qualified name of the class

        Returns:
            Generated .pyi content, or None if generation failed
        """
        try:
            methods = inspect_class(cls, include_private=self.include_private)
            return generate_class_stub(cls.__name__, full_name, methods)
        except Exception as e:
            print(f"[typed-pytest-generator] Error generating stub for {full_name}: {e}", file=sys.stderr)
            return None


def generate_stubs(
    targets: list[str],
    output_dir: str | Path = "typed_pytest_stubs",
    include_private: bool = False,
) -> list[Path]:
    """Convenience function to generate stubs for specified targets.

    Args:
        targets: List of fully qualified class names
        output_dir: Directory for generated stubs
        include_private: Whether to include private methods

    Returns:
        List of generated stub file paths
    """
    generator = StubGenerator(targets, output_dir, include_private)
    return generator.generate()

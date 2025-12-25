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
        class_to_target: dict[str, str] = {}  # Map class name to full target path

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
                class_to_target[class_name] = target

        # Generate __init__.pyi
        if stubs:
            init_content = generate_init_stub(list(stubs.keys()))
            init_path = self.output_dir / "__init__.pyi"
            init_path.write_text(init_content)
            generated_files.append(init_path)

            # Generate __init__.py for the stub package
            # This file allows importing from the stub package at runtime
            # while .pyi files provide type information

            # Generate import lines with commas
            import_parts: list[str] = []
            for name in stubs.keys():
                import_parts.extend([f"    {name}", f"    {name}_TypedMock", f"    {name}Mock"])
            import_lines = [",\n".join(import_parts)]

            # Generate __all__ entries
            all_parts: list[str] = []
            for name in stubs.keys():
                all_parts.extend([f'    "{name}"', f'    "{name}_TypedMock"', f'    "{name}Mock"'])
            all_lines = [",\n".join(all_parts)]

            init_py_lines: list[str] = [
                '"""Type stub package for typed-pytest.',
                '',
                'This package provides stub classes for IDE auto-completion.',
                'Import from here to get type-safe mocks.',
                '',
                'Example:',
                '    from typed_pytest_stubs import UserService',
                '    mock = typed_mock(UserService)',
                '    mock.get_user(1)  # Auto-complete works!',
                '"""',
                'from __future__ import annotations',
                '',
                '# Re-export all stub classes from _runtime for runtime compatibility',
                'from ._runtime import (',
            ]
            init_py_lines.extend(import_lines)
            init_py_lines.extend([
                ')',
                '',
                '__all__ = [',
            ])
            init_py_lines.extend(all_lines)
            init_py_lines.extend([']', ''])

            init_py_content = "\n".join(init_py_lines)
            init_py_path = self.output_dir / "__init__.py"
            init_py_path.write_text(init_py_content)
            generated_files.append(init_py_path)

            # Generate _runtime.py with simplified method signatures
            # Use Any return types to avoid referencing test fixtures
            runtime_classes: list[str] = []
            for class_name, target in class_to_target.items():
                cls = self._import_class(target)
                if cls is None:
                    continue

                # Generate methods with simplified signatures (Any return type)
                method_lines: list[str] = [f"class {class_name}:"]
                for name in dir(cls):
                    if name.startswith("_"):
                        continue
                    attr = getattr(cls, name)
                    if callable(attr) and not isinstance(attr, type):
                        try:
                            sig = inspect.signature(attr)
                            # Simplify signature: replace return type with Any
                            sig_str = str(sig)
                            # Handle return annotation replacement
                            if "->" in sig_str:
                                # Find the return type and replace with Any
                                parts = sig_str.split("->")
                                params = parts[0]
                                params = params.rstrip()
                                simplified = f"{params} -> typing.Any: ..."
                                method_lines.append(f"    def {name}{simplified}")
                            else:
                                method_lines.append(f"    def {name}{sig}: ...")
                        except (ValueError, TypeError):
                            method_lines.append(f"    def {name}(self, *args, **kwargs): ...")

                # Add TypedMock subclass and alias
                method_lines.extend([
                    "",
                    f"class {class_name}_TypedMock:",
                    f"    pass",
                    f"class {class_name}Mock({class_name}_TypedMock):",
                    f"    pass",
                ])
                runtime_classes.append("\n".join(method_lines))

            runtime_py_content = "\n\n".join([
                '"""Runtime-accessible placeholder classes for stub package.',
                '',
                'These classes are used at runtime when importing from typed_pytest_stubs.',
                '"""',
                'from __future__ import annotations',
                '',
                'import typing',
                '',
            ] + runtime_classes + [""])
            runtime_py_path = self.output_dir / "_runtime.py"
            runtime_py_path.write_text(runtime_py_content)
            generated_files.append(runtime_py_path)

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

    def _get_classes_with_methods(self, stubs: dict[str, str]) -> dict[str, type]:
        """Get actual classes with their methods for runtime generation.

        Args:
            stubs: Dictionary mapping stub names to their content

        Returns:
            Dictionary mapping targets to their actual class objects
        """
        result: dict[str, type] = {}
        for target in stubs.keys():
            cls = self._import_class(target)
            if cls is not None:
                result[target] = cls
        return result


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

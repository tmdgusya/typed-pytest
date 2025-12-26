"""Core stub generation logic for typed-pytest-generator."""

from __future__ import annotations

import inspect
import sys
from importlib import import_module
from pathlib import Path
from typing import TypeVar

from typed_pytest_generator._inspector import inspect_class
from typed_pytest_generator._templates import generate_class_stub


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
        # Add current directory to sys.path for importing local modules
        cwd = str(Path.cwd())
        if cwd not in sys.path:
            sys.path.insert(0, cwd)

        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Expand wildcard patterns (e.g., "module.*" -> ["module.Class1", "module.Class2"])
        expanded_targets = self._expand_targets(self.targets)

        generated_files: list[Path] = []
        stubs: dict[str, str] = {}
        class_to_target: dict[str, str] = {}  # Map class name to full target path

        for target in expanded_targets:
            cls = self._import_class(target)
            if cls is None:
                print(
                    f"[typed-pytest-generator] Warning: Could not import {target}",
                    file=sys.stderr,
                )
                continue

            stub_content = self._generate_stub(cls, target)
            if stub_content:
                class_name = cls.__name__
                stubs[class_name] = stub_content
                class_to_target[class_name] = target

        # Generate __init__.py for the stub package
        if stubs:
            # Generate __init__.py for the stub package
            # This file allows importing from the stub package at runtime
            # while .pyi files provide type information

            # Generate import lines with commas
            import_parts: list[str] = []
            for name in stubs:
                import_parts.extend(
                    [f"    {name}", f"    {name}_TypedMock", f"    {name}Mock"]
                )
            # Add typed_mock function
            import_parts.append("    typed_mock")
            import_lines = [",\n".join(import_parts)]

            # Generate __all__ entries
            all_parts: list[str] = []
            for name in stubs:
                all_parts.extend(
                    [f'    "{name}"', f'    "{name}_TypedMock"', f'    "{name}Mock"']
                )
            all_parts.append('    "typed_mock"')
            all_lines = [",\n".join(all_parts)]

            init_py_lines: list[str] = [
                '"""Type stub package for typed-pytest.',
                "",
                "This package provides stub classes for IDE auto-completion.",
                "Import typed_mock from here to get type-safe mocks with full auto-completion.",
                "",
                "Example:",
                "    from typed_pytest_stubs import typed_mock, UserService",
                "",
                "    mock = typed_mock(UserService)",
                "    mock.get_user              # Auto-complete works!",
                "    mock.get_user.return_value # Auto-complete works!",
                '"""',
                "from __future__ import annotations",
                "",
                "# Re-export all stub classes from _runtime for runtime compatibility",
                "from ._runtime import (",
            ]
            init_py_lines.extend(import_lines)
            init_py_lines.extend(
                [
                    ")",
                    "",
                    "__all__ = [",
                ]
            )
            init_py_lines.extend(all_lines)
            init_py_lines.extend(["]", ""])

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

                # Collect method info for both base class and TypedMock class
                method_lines: list[str] = [f"class {class_name}:"]
                typed_mock_lines: list[str] = [
                    f"class {class_name}_TypedMock:",
                    "    @property",
                    f"    def typed_class(self) -> type[{class_name}] | None: ...",
                ]
                has_methods = False

                for name in dir(cls):
                    if name.startswith("_"):
                        continue
                    # Get raw attribute to check for staticmethod/classmethod/property
                    raw_attr = inspect.getattr_static(cls, name)
                    is_static = isinstance(raw_attr, staticmethod)
                    is_classmethod = isinstance(raw_attr, classmethod)
                    is_property = isinstance(raw_attr, property)

                    # Handle properties
                    if is_property:
                        has_methods = True
                        method_lines.append("    @property")
                        method_lines.append(f"    def {name}(self) -> typing.Any: ...")
                        # For TypedMock, properties return MagicMock (via PropertyMock)
                        typed_mock_lines.append("    @property")
                        typed_mock_lines.append(
                            f"    def {name}(self) -> typing.Any: ..."
                        )
                        continue

                    attr = getattr(cls, name)
                    if callable(attr) and not isinstance(attr, type):
                        has_methods = True
                        # Check if it's an async method
                        # For staticmethod/classmethod, we need to unwrap to get the actual function
                        if is_static or is_classmethod:
                            is_async = inspect.iscoroutinefunction(raw_attr.__func__)
                        else:
                            is_async = inspect.iscoroutinefunction(raw_attr)
                        try:
                            sig = inspect.signature(attr)
                            sig_str = str(sig)

                            # Extract parameter types for MockedMethod
                            param_types = self._extract_param_types(sig)

                            # Handle return annotation replacement
                            if "->" in sig_str:
                                parts = sig_str.split("->")
                                params = parts[0].rstrip()
                                simplified = f"{params} -> typing.Any: ..."
                            else:
                                simplified = f"{sig_str}: ..."

                            # Add to base class
                            async_prefix = "async " if is_async else ""
                            if is_static:
                                method_lines.append("    @staticmethod")
                                method_lines.append(
                                    f"    {async_prefix}def {name}{simplified}"
                                )
                            elif is_classmethod:
                                method_lines.append("    @classmethod")
                                method_lines.append(
                                    f"    {async_prefix}def {name}(cls, {simplified[1:]}"
                                    if simplified.startswith("(")
                                    else f"    {async_prefix}def {name}{simplified}"
                                )
                            else:
                                method_lines.append(
                                    f"    {async_prefix}def {name}{simplified}"
                                )

                            # Add to TypedMock class as property returning MockedMethod/AsyncMockedMethod
                            mocked_method_type = (
                                "AsyncMockedMethod" if is_async else "MockedMethod"
                            )
                            typed_mock_lines.append("    @property")
                            typed_mock_lines.append(
                                f"    def {name}(self) -> {mocked_method_type}[{param_types}, typing.Any]: ..."
                            )

                        except (ValueError, TypeError):
                            method_lines.append(
                                f"    def {name}(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any: ..."
                            )
                            typed_mock_lines.append("    @property")
                            typed_mock_lines.append(
                                f"    def {name}(self) -> MockedMethod[..., typing.Any]: ..."
                            )

                # Add pass if class has no methods
                if not has_methods:
                    method_lines.append("    pass")
                    # typed_mock_lines already has typed_class, so no pass needed

                # Combine all class definitions
                method_lines.extend(
                    [
                        "",
                        *typed_mock_lines,
                        "",
                        f"class {class_name}Mock({class_name}_TypedMock):",
                        "    pass",
                    ]
                )
                runtime_classes.append("\n".join(method_lines))

            # Generate overloaded typed_mock function
            typed_mock_overloads: list[str] = []
            for class_name in stubs:
                typed_mock_overloads.append("@typing.overload")
                typed_mock_overloads.append(
                    f"def typed_mock(cls: type[{class_name}], *, "
                    f"spec_set: bool = ..., strict: bool = ...) -> {class_name}_TypedMock: ..."
                )

            # Add the actual implementation
            typed_mock_impl = [
                "",
                "def typed_mock(cls: type, *, spec_set: bool = False, strict: bool = False):",
                '    """Create a typed mock with IDE auto-completion support.',
                "",
                "    Args:",
                "        cls: The class to mock",
                "        spec_set: If True, attempting to set non-existent attributes raises AttributeError",
                "        strict: Alias for spec_set",
                "",
                "    Returns:",
                "        A TypedMock instance with proper type hints for IDE auto-completion",
                '    """',
                "    from typed_pytest import TypedMock",
                "    if spec_set or strict:",
                "        return TypedMock(spec_set=cls)",
                "    return TypedMock(spec=cls)",
            ]

            runtime_py_content = "\n\n".join(
                [
                    '"""Runtime-accessible placeholder classes for stub package.',
                    "",
                    "These classes are used at runtime when importing from typed_pytest_stubs.",
                    "The _TypedMock classes provide IDE auto-completion for mock methods.",
                    '"""',
                    "from __future__ import annotations",
                    "",
                    "import typing",
                    "",
                    "from typed_pytest import AsyncMockedMethod, MockedMethod",
                    "",
                ]
                + runtime_classes
                + ["\n".join(typed_mock_overloads)]
                + ["\n".join(typed_mock_impl)]
                + [""]
            )
            runtime_py_path = self.output_dir / "_runtime.py"
            runtime_py_path.write_text(runtime_py_content)
            generated_files.append(runtime_py_path)

        return generated_files

    def _expand_targets(self, targets: list[str]) -> list[str]:
        """Expand wildcard patterns in targets.

        Supports:
            - "module.submodule.*" - all classes in the module
            - "module.submodule.ClassName" - specific class (no expansion)

        Args:
            targets: List of target patterns

        Returns:
            Expanded list of fully qualified class names
        """
        expanded: list[str] = []

        for target in targets:
            if target.endswith(".*"):
                # Wildcard pattern: import module and find all classes
                module_path = target[:-2]  # Remove ".*"
                try:
                    module = import_module(module_path)
                    for name in dir(module):
                        if name.startswith("_"):
                            continue
                        attr = getattr(module, name)
                        # Only include classes defined in this module
                        if isinstance(attr, type) and attr.__module__ == module_path:
                            expanded.append(f"{module_path}.{name}")
                except ImportError as e:
                    print(
                        f"[typed-pytest-generator] Error importing {module_path}: {e}",
                        file=sys.stderr,
                    )
            else:
                # Regular target, no expansion
                expanded.append(target)

        return expanded

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
            cls = getattr(module, class_name)
            if isinstance(cls, type):
                return cls
            return None
        except (ImportError, AttributeError) as e:
            print(
                f"[typed-pytest-generator] Error importing {target}: {e}",
                file=sys.stderr,
            )
            return None

    def _extract_param_types(self, sig: inspect.Signature) -> str:
        """Extract parameter types from a signature for MockedMethod.

        Args:
            sig: The method signature

        Returns:
            String representation of parameter types, e.g., "[int, str]"
        """
        param_types: list[str] = []
        for i, (name, param) in enumerate(sig.parameters.items()):
            # Skip 'self' for instance methods (classmethods already have cls bound)
            if i == 0 and name == "self":
                continue

            if param.annotation is inspect.Parameter.empty:
                param_types.append("typing.Any")
            else:
                # Convert annotation to string, handling special cases
                ann = param.annotation
                if hasattr(ann, "__name__"):
                    param_types.append(ann.__name__)
                else:
                    ann_str = str(ann)
                    # Clean up typing module prefixes for readability
                    ann_str = ann_str.replace("typing.", "")
                    # Handle forward references
                    if ann_str.startswith("ForwardRef("):
                        ann_str = "typing.Any"
                    param_types.append(ann_str)

        if not param_types:
            return "[]"
        return "[" + ", ".join(param_types) + "]"

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
            print(
                f"[typed-pytest-generator] Error generating stub for {full_name}: {e}",
                file=sys.stderr,
            )
            return None

    def _get_classes_with_methods(self, stubs: dict[str, str]) -> dict[str, type]:
        """Get actual classes with their methods for runtime generation.

        Args:
            stubs: Dictionary mapping stub names to their content

        Returns:
            Dictionary mapping targets to their actual class objects
        """
        result: dict[str, type] = {}
        for target in stubs:
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

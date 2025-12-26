"""Stubgen-based backend for stub generation.

Uses mypy's stubgen for AST-based analysis which provides better
type information than runtime introspection.
"""

from __future__ import annotations

import ast
import subprocess
import tempfile
from pathlib import Path

from typed_pytest_generator._backend import ClassInfo, MethodInfo, StubBackend


class StubgenBackend(StubBackend):
    """Backend using mypy's stubgen for AST-based analysis.

    This backend generates stubs by:
    1. Running stubgen on the module containing the class
    2. Parsing the generated .pyi file
    3. Extracting method signatures from the AST
    """

    def __init__(self, include_private: bool = False) -> None:
        self.include_private = include_private
        self._cache: dict[str, str] = {}  # module -> pyi content

    def get_name(self) -> str:
        return "stubgen"

    def extract_class_info(self, cls: type, full_name: str) -> ClassInfo:
        """Extract class info using stubgen."""
        module_name = cls.__module__

        # Generate stub if not cached
        if module_name not in self._cache:
            pyi_content = self._generate_stub(module_name)
            self._cache[module_name] = pyi_content

        pyi_content = self._cache[module_name]
        if not pyi_content:
            # Fallback: return empty info
            return ClassInfo(name=cls.__name__, full_name=full_name, methods=[])

        # Parse the .pyi content
        return self._parse_class_from_pyi(cls.__name__, full_name, pyi_content)

    def _generate_stub(self, module_name: str) -> str:
        """Generate stub using stubgen CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                ["stubgen", "-m", module_name, "-o", tmpdir],
                check=False,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print(f"[stubgen] Warning: stubgen failed for {module_name}")
                print(f"[stubgen] stderr: {result.stderr}")
                return ""

            # Find the generated .pyi file
            pyi_path = Path(tmpdir) / module_name.replace(".", "/")
            pyi_path = pyi_path.with_suffix(".pyi")

            # Handle nested modules
            if not pyi_path.exists():
                parts = module_name.split(".")
                pyi_path = Path(tmpdir)
                for part in parts[:-1]:
                    pyi_path = pyi_path / part
                pyi_path = pyi_path / f"{parts[-1]}.pyi"

            if pyi_path.exists():
                return pyi_path.read_text()

            return ""

    def _parse_class_from_pyi(
        self, class_name: str, full_name: str, pyi_content: str
    ) -> ClassInfo:
        """Parse a class from .pyi content."""
        try:
            tree = ast.parse(pyi_content)
        except SyntaxError:
            return ClassInfo(name=class_name, full_name=full_name, methods=[])

        methods: list[MethodInfo] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                methods = self._extract_methods_from_class(node)
                break

        return ClassInfo(name=class_name, full_name=full_name, methods=methods)

    def _extract_methods_from_class(self, class_node: ast.ClassDef) -> list[MethodInfo]:
        """Extract methods from a class AST node."""
        methods: list[MethodInfo] = []

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                name = item.name

                # Skip private methods except __init__
                if (
                    name.startswith("_")
                    and not self.include_private
                    and name != "__init__"
                ):
                    continue

                # Check decorators
                is_static = False
                is_classmethod = False
                is_property = False

                for dec in item.decorator_list:
                    if isinstance(dec, ast.Name):
                        if dec.id == "staticmethod":
                            is_static = True
                        elif dec.id == "classmethod":
                            is_classmethod = True
                        elif dec.id == "property":
                            is_property = True

                is_async = isinstance(item, ast.AsyncFunctionDef)

                # Build signature string
                signature = self._build_signature(item)
                param_types = self._extract_param_types_from_func(item)
                return_type = self._get_return_type(item)

                methods.append(
                    MethodInfo(
                        name=name,
                        signature=signature,
                        is_async=is_async,
                        is_static=is_static,
                        is_classmethod=is_classmethod,
                        is_property=is_property,
                        param_types=param_types,
                        return_type=return_type,
                    )
                )

        return methods

    def _build_signature(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Build a signature string from a function AST."""
        args = func.args
        parts: list[str] = []

        # Positional args
        for i, arg in enumerate(args.args):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"

            # Check for default value
            default_idx = i - (len(args.args) - len(args.defaults))
            if default_idx >= 0 and default_idx < len(args.defaults):
                default = args.defaults[default_idx]
                arg_str += f" = {ast.unparse(default)}"

            parts.append(arg_str)

        # *args
        if args.vararg:
            vararg_str = f"*{args.vararg.arg}"
            if args.vararg.annotation:
                vararg_str += f": {ast.unparse(args.vararg.annotation)}"
            parts.append(vararg_str)
        elif args.kwonlyargs:
            parts.append("*")

        # Keyword-only args
        for i, arg in enumerate(args.kwonlyargs):
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            if i < len(args.kw_defaults):
                kw_default = args.kw_defaults[i]
                if kw_default is not None:
                    arg_str += f" = {ast.unparse(kw_default)}"
            parts.append(arg_str)

        # **kwargs
        if args.kwarg:
            kwarg_str = f"**{args.kwarg.arg}"
            if args.kwarg.annotation:
                kwarg_str += f": {ast.unparse(args.kwarg.annotation)}"
            parts.append(kwarg_str)

        params = ", ".join(parts)
        ret = self._get_return_type(func)

        return f"({params}) -> {ret}"

    def _extract_param_types_from_func(
        self, func: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> list[str]:
        """Extract parameter types from function AST."""
        param_types: list[str] = []

        for i, arg in enumerate(func.args.args):
            if i == 0 and arg.arg in ("self", "cls"):
                continue

            if arg.annotation:
                param_types.append(ast.unparse(arg.annotation))
            else:
                param_types.append("typing.Any")

        return param_types

    def _get_return_type(self, func: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
        """Get return type from function AST."""
        if func.returns:
            return ast.unparse(func.returns)
        return "typing.Any"

"""Inspect-based backend for stub generation.

Uses Python's inspect module for runtime introspection.
"""

from __future__ import annotations

import inspect
import re

from typed_pytest_generator._backend import ClassInfo, MethodInfo, StubBackend


def _sanitize_default_value(match: re.Match[str]) -> str:
    """Sanitize a single default value."""
    value = match.group(1)

    # Valid literals - keep as is
    if re.match(r"^-?\d+\.?\d*$", value):  # Numbers
        return f"= {value}"
    if re.match(r'^["\'].*["\']$', value):  # Strings
        return f"= {value}"
    if value in ("True", "False", "None"):
        return f"= {value}"
    if value in ("[]", "{}", "()", "set()"):
        return f"= {value}"
    if value == "...":
        return f"= {value}"

    return "= ..."


def _sanitize_signature(sig_str: str) -> str:
    """Sanitize a signature string to replace invalid default values."""
    sig_str = re.sub(r"<[^>]+>", "...", sig_str)
    return re.sub(r"= ([^,\)]+)(?=[,\)])", _sanitize_default_value, sig_str)


class InspectBackend(StubBackend):
    """Backend using Python's inspect module for runtime introspection."""

    def __init__(self, include_private: bool = False) -> None:
        self.include_private = include_private

    def get_name(self) -> str:
        return "inspect"

    def extract_class_info(self, cls: type, full_name: str) -> ClassInfo:
        """Extract class info using inspect module."""
        methods: list[MethodInfo] = []

        for name in dir(cls):
            if name.startswith("_") and not self.include_private:
                continue

            raw_attr = inspect.getattr_static(cls, name)
            is_static = isinstance(raw_attr, staticmethod)
            is_classmethod = isinstance(raw_attr, classmethod)
            is_property = isinstance(raw_attr, property)

            if is_property:
                methods.append(
                    MethodInfo(
                        name=name,
                        signature="(self) -> typing.Any",
                        is_property=True,
                        return_type="typing.Any",
                    )
                )
                continue

            attr = getattr(cls, name)
            if not callable(attr) or isinstance(attr, type):
                continue

            # Check if async
            if is_static or is_classmethod:
                is_async = inspect.iscoroutinefunction(raw_attr.__func__)
            else:
                is_async = inspect.iscoroutinefunction(raw_attr)

            try:
                sig = inspect.signature(attr)
                sig_str = _sanitize_signature(str(sig))
                param_types = self._extract_param_types(sig)

                # Simplify return type to Any
                if "->" in sig_str:
                    parts = sig_str.split("->")
                    signature = f"{parts[0].rstrip()} -> typing.Any"
                else:
                    signature = sig_str

                methods.append(
                    MethodInfo(
                        name=name,
                        signature=signature,
                        is_async=is_async,
                        is_static=is_static,
                        is_classmethod=is_classmethod,
                        param_types=param_types,
                        return_type="typing.Any",
                    )
                )
            except (ValueError, TypeError):
                methods.append(
                    MethodInfo(
                        name=name,
                        signature="(self, *args: typing.Any, **kwargs: typing.Any) -> typing.Any",
                        param_types=[],
                        return_type="typing.Any",
                    )
                )

        return ClassInfo(name=cls.__name__, full_name=full_name, methods=methods)

    def _extract_param_types(self, sig: inspect.Signature) -> list[str]:
        """Extract parameter types from signature."""
        param_types: list[str] = []
        for i, (name, param) in enumerate(sig.parameters.items()):
            if i == 0 and name == "self":
                continue

            if param.annotation is inspect.Parameter.empty:
                param_types.append("typing.Any")
            else:
                ann = param.annotation
                if hasattr(ann, "__name__"):
                    param_types.append(ann.__name__)
                else:
                    ann_str = str(ann).replace("typing.", "")
                    if ann_str.startswith("ForwardRef("):
                        ann_str = "typing.Any"
                    param_types.append(ann_str)

        return param_types

"""Class introspection utilities for typed-pytest-generator."""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass

# Type hints import - use string for forward compatibility
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from typing import ParamSpec

    P = ParamSpec("P")


@dataclass
class MethodInfo:
    """Information about a method extracted from a class."""

    name: str
    method_type: str  # "method", "async", "property", "classmethod", "staticmethod"
    signature: inspect.Signature
    return_annotation: Any
    parameters: list[inspect.Parameter]


def _get_signature_with_hints(func: Callable[..., Any]) -> inspect.Signature:
    """Get function signature, falling back to annotations if needed."""
    try:
        return inspect.signature(func)
    except (ValueError, TypeError):
        # Fallback: try to get signature from annotations
        annotations: dict[str, Any] = getattr(func, "__annotations__", {})
        params: list[inspect.Parameter] = []
        for name, ann in annotations.items():
            if name != "return":
                params.append(
                    inspect.Parameter(
                        name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=ann,
                    )
                )
        return inspect.Signature(parameters=params)


def _get_return_annotation(func: Callable[..., Any]) -> Any:
    """Get return annotation from a function."""
    annotations = getattr(func, "__annotations__", {})
    return annotations.get("return", "Any")


def inspect_class(
    cls: type,
    include_private: bool = False,
) -> list[MethodInfo]:
    """Inspect a class and extract method information.

    Args:
        cls: The class to inspect
        include_private: Whether to include private methods (starting with _)

    Returns:
        List of MethodInfo objects for each method in the class
    """
    methods: list[MethodInfo] = []

    for name in dir(cls):
        # Skip private methods unless requested
        if not include_private and name.startswith("_"):
            continue

        # Get the attribute from the class's __dict__ (not from instance)
        if name in cls.__dict__:
            attr = cls.__dict__[name]
        else:
            # For inherited members, get from the class where they're defined
            attr = None
            for base_cls in cls.__mro__[1:]:  # Skip the class itself
                if name in base_cls.__dict__:
                    attr = base_cls.__dict__[name]
                    break

        if attr is None:
            continue

        # Analyze the attribute type
        method_info = _analyze_attribute(name, attr, cls)
        if method_info:
            methods.append(method_info)

    return methods


def _analyze_attribute(name: str, attr: Any, cls: type) -> MethodInfo | None:
    """Analyze a single attribute and return MethodInfo if it's a callable or property.

    Args:
        name: Name of the attribute
        attr: The attribute value
        cls: The class being inspected

    Returns:
        MethodInfo if the attribute is a method/property, None otherwise
    """
    # Check for staticmethod
    if isinstance(attr, staticmethod):
        func = attr.__func__
        return MethodInfo(
            name=name,
            method_type="staticmethod",
            signature=_get_signature_with_hints(func),
            return_annotation=_get_return_annotation(func),
            parameters=list(_get_signature_with_hints(func).parameters.values())[
                1:
            ],  # Skip cls
        )

    # Check for classmethod
    if isinstance(attr, classmethod):
        func = attr.__func__
        return MethodInfo(
            name=name,
            method_type="classmethod",
            signature=_get_signature_with_hints(func),
            return_annotation=_get_return_annotation(func),
            parameters=list(_get_signature_with_hints(func).parameters.values())[
                1:
            ],  # Skip cls
        )

    # Check for property
    if isinstance(attr, property):
        return MethodInfo(
            name=name,
            method_type="property",
            signature=inspect.Signature(
                parameters=[
                    inspect.Parameter(
                        "self",
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    )
                ]
            ),
            return_annotation=_get_return_annotation(attr.fget) if attr.fget else "Any",
            parameters=[],
        )

    # Check for async function (must check __dict__ directly)
    if name in cls.__dict__:
        dict_attr = cls.__dict__[name]
        if inspect.iscoroutinefunction(dict_attr):
            return MethodInfo(
                name=name,
                method_type="async",
                signature=_get_signature_with_hints(dict_attr),
                return_annotation=_get_return_annotation(dict_attr),
                parameters=list(
                    _get_signature_with_hints(dict_attr).parameters.values()
                )[1:],  # Skip self
            )

    # Check for regular method (callable but not a type)
    if callable(attr) and not isinstance(attr, type):
        return MethodInfo(
            name=name,
            method_type="method",
            signature=_get_signature_with_hints(attr),
            return_annotation=_get_return_annotation(attr),
            parameters=list(_get_signature_with_hints(attr).parameters.values())[
                1:
            ],  # Skip self
        )

    return None


def format_signature_params(params: list[inspect.Parameter]) -> str:
    """Format parameters as a signature string for .pyi file.

    Args:
        params: List of inspect.Parameter objects

    Returns:
        Formatted parameter string like "(self, user_id: int, name: str)"
    """
    param_strs = []
    for param in params:
        if param.annotation != inspect.Parameter.empty:
            ann_str = (
                param.annotation.__name__
                if hasattr(param.annotation, "__name__")
                else str(param.annotation)
            )
        else:
            ann_str = "Any"

        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            param_strs.append(f"*, {param.name}: {ann_str}")
        elif param.kind == inspect.Parameter.VAR_KEYWORD:
            param_strs.append(f"**kwargs: {ann_str}")
        elif param.kind == inspect.Parameter.VAR_POSITIONAL:
            param_strs.append(f"*args: {ann_str}")
        else:
            param_strs.append(f"{param.name}: {ann_str}")

    return ", ".join(param_strs)

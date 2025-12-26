"""Backend protocols and implementations for stub generation.

This module provides different backends for extracting class information
used to generate type stubs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class MethodInfo:
    """Information about a method extracted from a class."""

    name: str
    signature: str  # e.g., "(self, user_id: int) -> dict"
    is_async: bool = False
    is_static: bool = False
    is_classmethod: bool = False
    is_property: bool = False
    param_types: list[str] = field(default_factory=list)  # e.g., ["int", "str"]
    return_type: str = "typing.Any"


@dataclass
class ClassInfo:
    """Information about a class extracted for stub generation."""

    name: str
    full_name: str  # e.g., "myapp.services.UserService"
    methods: list[MethodInfo] = field(default_factory=list)


class StubBackend(ABC):
    """Abstract base class for stub generation backends.

    Different backends can extract class information using different strategies:
    - InspectBackend: Uses Python's inspect module (runtime introspection)
    - StubgenBackend: Uses mypy's stubgen (AST-based analysis)
    """

    @abstractmethod
    def extract_class_info(self, cls: type, full_name: str) -> ClassInfo:
        """Extract information from a class for stub generation.

        Args:
            cls: The class to analyze
            full_name: Fully qualified class name

        Returns:
            ClassInfo containing method information
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this backend for logging."""
        ...

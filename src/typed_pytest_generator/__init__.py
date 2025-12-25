"""typed-pytest-generator - Generate .pyi stub files for TypedMock auto-completion."""

__version__ = "0.1.1"

from typed_pytest_generator._config import (
    ConfigLoadError,
    GeneratorConfig,
    load_config,
)
from typed_pytest_generator._generator import StubGenerator, generate_stubs
from typed_pytest_generator.cli import main


__all__ = [
    "ConfigLoadError",
    "GeneratorConfig",
    "StubGenerator",
    "generate_stubs",
    "load_config",
    "main",
]

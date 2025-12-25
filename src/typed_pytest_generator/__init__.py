"""typed-pytest-generator - Generate .pyi stub files for TypedMock auto-completion."""

__version__ = "0.1.0"

from typed_pytest_generator._generator import StubGenerator, generate_stubs
from typed_pytest_generator.cli import main


__all__ = ["StubGenerator", "generate_stubs", "main"]

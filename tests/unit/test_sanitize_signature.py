"""Test signature sanitization for invalid default values."""

import shutil
import tempfile
from pathlib import Path
from typing import Literal

from typed_pytest_generator._generator import StubGenerator, _sanitize_signature


class TestSanitizeSignature:
    """Test _sanitize_signature function."""

    def test_sanitize_class_default(self) -> None:
        """Should replace <class '...'> with ..."""
        sig = "(cls, schema_generator: 'type[Foo]' = <class 'module.Foo'>)"
        result = _sanitize_signature(sig)
        assert result == "(cls, schema_generator: 'type[Foo]' = ...)"

    def test_sanitize_function_default(self) -> None:
        """Should replace <function ...> with ..."""
        sig = "(self, callback = <function default_callback at 0x123>)"
        result = _sanitize_signature(sig)
        assert result == "(self, callback = ...)"

    def test_sanitize_multiple_invalid_defaults(self) -> None:
        """Should replace multiple invalid defaults."""
        sig = "(cls, a = <class 'A'>, b = <function b>)"
        result = _sanitize_signature(sig)
        assert result == "(cls, a = ..., b = ...)"

    def test_sanitize_preserves_valid_defaults(self) -> None:
        """Should preserve valid Python defaults."""
        sig = "(self, name: str = 'default', count: int = 0, flag: bool = True)"
        result = _sanitize_signature(sig)
        assert result == sig  # No change

    def test_sanitize_mixed_defaults(self) -> None:
        """Should handle mix of valid and invalid defaults."""
        sig = "(self, a: str = 'hello', b = <class 'Foo'>, c: int = 42)"
        result = _sanitize_signature(sig)
        assert result == "(self, a: str = 'hello', b = ..., c: int = 42)"

    def test_sanitize_undefined_identifier(self) -> None:
        """Should replace undefined identifiers like PydanticUndefined."""
        sig = "(self, encoder = PydanticUndefined, models_as_dict = PydanticUndefined)"
        result = _sanitize_signature(sig)
        assert result == "(self, encoder = ..., models_as_dict = ...)"

    def test_sanitize_camelcase_identifier(self) -> None:
        """Should replace CamelCase identifiers that are likely undefined."""
        sig = "(cls, schema_generator: type = GenerateJsonSchema)"
        result = _sanitize_signature(sig)
        assert result == "(cls, schema_generator: type = ...)"

    def test_sanitize_preserves_none_default(self) -> None:
        """Should preserve None as a default value."""
        sig = "(self, value: str | None = None)"
        result = _sanitize_signature(sig)
        assert result == "(self, value: str | None = None)"

    def test_sanitize_preserves_empty_collections(self) -> None:
        """Should preserve empty collections as defaults."""
        sig = "(self, items: list = [], data: dict = {})"
        result = _sanitize_signature(sig)
        assert result == "(self, items: list = [], data: dict = {})"

    def test_sanitize_preserves_negative_numbers(self) -> None:
        """Should preserve negative numbers."""
        sig = "(self, offset: int = -1, factor: float = -0.5)"
        result = _sanitize_signature(sig)
        assert result == "(self, offset: int = -1, factor: float = -0.5)"

    def test_sanitize_pydantic_json_method(self) -> None:
        """Should handle Pydantic's json method with PydanticUndefined defaults."""
        sig = (
            "(self, *, include: 'IncEx | None' = None, exclude: 'IncEx | None' = None, "
            "by_alias: 'bool' = False, exclude_unset: 'bool' = False, "
            "exclude_defaults: 'bool' = False, exclude_none: 'bool' = False, "
            "encoder: 'Callable[[Any], Any] | None' = PydanticUndefined, "
            "models_as_dict: 'bool' = PydanticUndefined, **dumps_kwargs: 'Any')"
        )
        result = _sanitize_signature(sig)
        # PydanticUndefined should be replaced with ...
        assert "PydanticUndefined" not in result
        assert "encoder: 'Callable[[Any], Any] | None' = ..." in result
        assert "models_as_dict: 'bool' = ..." in result
        # Valid defaults should be preserved
        assert "= None" in result
        assert "= False" in result


class ClassWithClassDefault:
    """Test class with a class as default parameter value."""

    class InnerClass:
        pass

    @classmethod
    def method_with_class_default(
        cls,
        generator: type = InnerClass,
        mode: Literal["a", "b"] = "a",
    ) -> dict:
        return {}


class TestStubGenerationWithInvalidDefaults:
    """Test that stub generation handles invalid defaults."""

    def test_generates_valid_syntax_for_class_defaults(self) -> None:
        """Stub should have valid Python syntax even with class defaults."""
        output_dir = Path(tempfile.mkdtemp())
        try:
            generator = StubGenerator(
                targets=["tests.unit.test_sanitize_signature.ClassWithClassDefault"],
                output_dir=output_dir,
            )
            generator.generate()

            runtime_path = output_dir / "_runtime.py"
            content = runtime_path.read_text()

            # Should not contain <class ...> syntax
            assert "<class" not in content
            # Should contain the method
            assert "method_with_class_default" in content
            # The stub should be valid Python - try to compile it
            compile(content, runtime_path, "exec")
        finally:
            shutil.rmtree(output_dir)

"""Tests for typed-pytest-generator CLI.

These tests verify:
- CLI argument parsing
- Integration with configuration files
- Error handling and exit codes
- Verbose output
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from typed_pytest_generator.cli import main


class TestCliBasicUsage:
    """Tests for basic CLI usage."""

    def test_no_args_no_config_returns_error(self) -> None:
        """Returns error when no targets specified and no config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)  # Empty dir with no pyproject.toml
                exit_code = main([])
                assert exit_code == 1
            finally:
                os.chdir(original_cwd)

    def test_targets_from_cli(self) -> None:
        """Generates stubs when targets specified via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                ]
            )

            assert exit_code == 0
            assert (Path(tmpdir) / "__init__.py").exists()
            assert (Path(tmpdir) / "_runtime.py").exists()

    def test_multiple_targets(self) -> None:
        """Handles multiple targets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "tests.fixtures.sample_classes.ProductRepository",
                    "-o",
                    tmpdir,
                ]
            )

            assert exit_code == 0
            runtime_content = (Path(tmpdir) / "_runtime.py").read_text()
            assert "class UserService:" in runtime_content
            assert "class ProductRepository:" in runtime_content


class TestCliWithConfig:
    """Tests for CLI with configuration file."""

    def test_uses_config_targets(self) -> None:
        """Uses targets from pyproject.toml when not specified in CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create output directory
            output_dir = tmppath / "stubs"
            output_dir.mkdir()

            # Create config file
            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["tests.fixtures.sample_classes.UserService"]
                output-dir = "stubs"
            """)
            )

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                exit_code = main([])
                assert exit_code == 0
                assert (output_dir / "_runtime.py").exists()
            finally:
                os.chdir(original_cwd)

    def test_cli_targets_override_config(self) -> None:
        """CLI targets override config targets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["nonexistent.ConfigTarget"]
            """)
            )

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # CLI target should be used instead of config
                exit_code = main(
                    [
                        "-t",
                        "tests.fixtures.sample_classes.UserService",
                        "-o",
                        tmpdir,
                    ]
                )
                assert exit_code == 0
                runtime = (tmppath / "_runtime.py").read_text()
                assert "UserService" in runtime
            finally:
                os.chdir(original_cwd)

    def test_explicit_config_path(self) -> None:
        """Uses explicitly specified config file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create config in non-standard location
            config_file = tmppath / "custom" / "config.toml"
            config_file.parent.mkdir()
            config_file.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["tests.fixtures.sample_classes.UserService"]
            """)
            )

            exit_code = main(
                [
                    "-c",
                    str(config_file),
                    "-o",
                    tmpdir,
                ]
            )

            assert exit_code == 0


class TestCliExcludeTargets:
    """Tests for exclude targets functionality."""

    def test_exclude_via_cli(self) -> None:
        """Excludes targets specified via CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "tests.fixtures.sample_classes.ProductRepository",
                    "-e",
                    "tests.fixtures.sample_classes.ProductRepository",
                    "-o",
                    tmpdir,
                ]
            )

            assert exit_code == 0
            runtime = (Path(tmpdir) / "_runtime.py").read_text()
            assert "UserService" in runtime
            assert "ProductRepository" not in runtime

    def test_exclude_via_config(self) -> None:
        """Excludes targets specified in config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = [
                    "tests.fixtures.sample_classes.UserService",
                    "tests.fixtures.sample_classes.ProductRepository"
                ]
                exclude-targets = ["tests.fixtures.sample_classes.ProductRepository"]
            """)
            )

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                exit_code = main(["-o", tmpdir])
                assert exit_code == 0
                runtime = (tmppath / "_runtime.py").read_text()
                assert "UserService" in runtime
                assert "ProductRepository" not in runtime
            finally:
                os.chdir(original_cwd)

    def test_exclude_merges_cli_and_config(self) -> None:
        """CLI and config exclusions are merged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                exclude-targets = ["tests.fixtures.sample_classes.ProductRepository"]
            """)
            )

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                # Both targets excluded - one from config, one from CLI
                # Only UserService would remain if we had 3 targets
                exit_code = main(
                    [
                        "-t",
                        "tests.fixtures.sample_classes.UserService",
                        "tests.fixtures.sample_classes.ProductRepository",
                        "-o",
                        tmpdir,
                    ]
                )
                assert exit_code == 0
                runtime = (tmppath / "_runtime.py").read_text()
                assert "UserService" in runtime
                assert "ProductRepository" not in runtime
            finally:
                os.chdir(original_cwd)

    def test_exclude_all_targets_returns_error(self) -> None:
        """Returns error when all targets are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-e",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                ]
            )

            assert exit_code == 1


class TestCliOutputOptions:
    """Tests for output-related CLI options."""

    def test_custom_output_dir(self) -> None:
        """Uses custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "custom_output"

            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    str(output_path),
                ]
            )

            assert exit_code == 0
            assert output_path.exists()
            assert (output_path / "_runtime.py").exists()

    def test_creates_output_dir_if_not_exists(self) -> None:
        """Creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "new" / "nested" / "dir"

            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    str(output_path),
                ]
            )

            assert exit_code == 0
            assert output_path.exists()


class TestCliVerboseOutput:
    """Tests for verbose output mode."""

    def test_verbose_shows_targets(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verbose mode shows target information."""
        with tempfile.TemporaryDirectory() as tmpdir:
            main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                    "-v",
                ]
            )

            captured = capsys.readouterr()
            assert "Targets:" in captured.err
            assert "UserService" in captured.err

    def test_verbose_shows_output_dir(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Verbose mode shows output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                    "-v",
                ]
            )

            captured = capsys.readouterr()
            assert "Output dir:" in captured.err

    def test_verbose_shows_generated_files(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Verbose mode shows generated files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                    "-v",
                ]
            )

            captured = capsys.readouterr()
            assert "Generated" in captured.err
            assert "_runtime.py" in captured.err


class TestCliErrorHandling:
    """Tests for CLI error handling."""

    def test_invalid_target_shows_warning(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """Invalid target shows warning but continues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-t",
                    "nonexistent.module.Class",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                ]
            )

            # Should succeed for valid target
            assert exit_code == 0
            captured = capsys.readouterr()
            assert "Warning" in captured.err or "Error" in captured.err

    def test_invalid_config_returns_error(self) -> None:
        """Invalid config file returns error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text("invalid [ toml")

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                exit_code = main([])
                assert exit_code == 1
            finally:
                os.chdir(original_cwd)

    def test_nonexistent_config_path_returns_error(self) -> None:
        """Nonexistent explicit config path returns error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-c",
                    "/nonexistent/path/pyproject.toml",
                    "-o",
                    tmpdir,
                ]
            )

            assert exit_code == 1


class TestCliIncludePrivate:
    """Tests for include-private option."""

    def test_include_private_via_cli(self) -> None:
        """Include private methods when flag is set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exit_code = main(
                [
                    "-t",
                    "tests.fixtures.sample_classes.UserService",
                    "-o",
                    tmpdir,
                    "--include-private",
                ]
            )

            assert exit_code == 0

    def test_include_private_from_config(self) -> None:
        """Include private methods from config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["tests.fixtures.sample_classes.UserService"]
                include-private = true
            """)
            )

            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                exit_code = main(["-o", tmpdir])
                assert exit_code == 0
            finally:
                os.chdir(original_cwd)

"""Tests for typed-pytest-generator configuration loading.

These tests verify:
- Configuration loading from pyproject.toml
- Default values when no config is present
- CLI argument merging with config
- Exclude targets filtering
- Error handling for invalid configs
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from textwrap import dedent

import pytest

from typed_pytest_generator._config import (
    ConfigLoadError,
    GeneratorConfig,
    _parse_config_dict,
    find_pyproject_toml,
    load_config,
    load_config_from_toml,
)


class TestGeneratorConfig:
    """Tests for GeneratorConfig dataclass."""

    def test_default_values(self) -> None:
        """Default config has expected values."""
        config = GeneratorConfig()

        assert config.targets == []
        assert config.output_dir == "typed_pytest_stubs"
        assert config.include_private is False
        assert config.exclude_targets == []

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = GeneratorConfig(
            targets=["myapp.UserService"],
            output_dir="custom_stubs",
            include_private=True,
            exclude_targets=["myapp.Internal"],
        )

        assert config.targets == ["myapp.UserService"]
        assert config.output_dir == "custom_stubs"
        assert config.include_private is True
        assert config.exclude_targets == ["myapp.Internal"]


class TestGetFilteredTargets:
    """Tests for GeneratorConfig.get_filtered_targets()."""

    def test_no_exclusions_returns_all_targets(self) -> None:
        """Without exclusions, all targets are returned."""
        config = GeneratorConfig(
            targets=["myapp.A", "myapp.B", "myapp.C"],
            exclude_targets=[],
        )

        result = config.get_filtered_targets()

        assert result == ["myapp.A", "myapp.B", "myapp.C"]

    def test_excludes_specified_targets(self) -> None:
        """Specified targets are excluded."""
        config = GeneratorConfig(
            targets=["myapp.A", "myapp.B", "myapp.C"],
            exclude_targets=["myapp.B"],
        )

        result = config.get_filtered_targets()

        assert result == ["myapp.A", "myapp.C"]

    def test_excludes_multiple_targets(self) -> None:
        """Multiple targets can be excluded."""
        config = GeneratorConfig(
            targets=["myapp.A", "myapp.B", "myapp.C", "myapp.D"],
            exclude_targets=["myapp.A", "myapp.C"],
        )

        result = config.get_filtered_targets()

        assert result == ["myapp.B", "myapp.D"]

    def test_exclude_nonexistent_target_is_ignored(self) -> None:
        """Excluding a non-existent target doesn't cause error."""
        config = GeneratorConfig(
            targets=["myapp.A", "myapp.B"],
            exclude_targets=["myapp.NonExistent"],
        )

        result = config.get_filtered_targets()

        assert result == ["myapp.A", "myapp.B"]

    def test_exclude_all_targets_returns_empty(self) -> None:
        """Excluding all targets returns empty list."""
        config = GeneratorConfig(
            targets=["myapp.A", "myapp.B"],
            exclude_targets=["myapp.A", "myapp.B"],
        )

        result = config.get_filtered_targets()

        assert result == []

    def test_preserves_target_order(self) -> None:
        """Target order is preserved after filtering."""
        config = GeneratorConfig(
            targets=["myapp.Z", "myapp.A", "myapp.M", "myapp.B"],
            exclude_targets=["myapp.A"],
        )

        result = config.get_filtered_targets()

        assert result == ["myapp.Z", "myapp.M", "myapp.B"]


class TestMergeWithCli:
    """Tests for GeneratorConfig.merge_with_cli()."""

    def test_cli_targets_override_config(self) -> None:
        """CLI targets completely override config targets."""
        config = GeneratorConfig(targets=["config.A", "config.B"])

        merged = config.merge_with_cli(cli_targets=["cli.X", "cli.Y"])

        assert merged.targets == ["cli.X", "cli.Y"]

    def test_no_cli_targets_uses_config(self) -> None:
        """Without CLI targets, config targets are used."""
        config = GeneratorConfig(targets=["config.A", "config.B"])

        merged = config.merge_with_cli(cli_targets=None)

        assert merged.targets == ["config.A", "config.B"]

    def test_cli_output_dir_overrides_config(self) -> None:
        """CLI output_dir overrides config."""
        config = GeneratorConfig(output_dir="config_dir")

        merged = config.merge_with_cli(cli_output_dir="cli_dir")

        assert merged.output_dir == "cli_dir"

    def test_no_cli_output_dir_uses_config(self) -> None:
        """Without CLI output_dir, config is used."""
        config = GeneratorConfig(output_dir="config_dir")

        merged = config.merge_with_cli(cli_output_dir=None)

        assert merged.output_dir == "config_dir"

    def test_cli_include_private_overrides_config(self) -> None:
        """CLI include_private overrides config."""
        config = GeneratorConfig(include_private=False)

        merged = config.merge_with_cli(cli_include_private=True)

        assert merged.include_private is True

    def test_cli_exclude_targets_merged_with_config(self) -> None:
        """CLI exclude_targets are merged with config (union)."""
        config = GeneratorConfig(exclude_targets=["config.Excluded"])

        merged = config.merge_with_cli(cli_exclude_targets=["cli.Excluded"])

        assert set(merged.exclude_targets) == {"config.Excluded", "cli.Excluded"}

    def test_duplicate_exclude_targets_deduplicated(self) -> None:
        """Duplicate exclude targets are deduplicated."""
        config = GeneratorConfig(exclude_targets=["shared.Class"])

        merged = config.merge_with_cli(
            cli_exclude_targets=["shared.Class", "other.Class"]
        )

        assert set(merged.exclude_targets) == {"shared.Class", "other.Class"}

    def test_full_merge_scenario(self) -> None:
        """Complete merge scenario with all options."""
        config = GeneratorConfig(
            targets=["config.A"],
            output_dir="config_dir",
            include_private=False,
            exclude_targets=["config.Excluded"],
        )

        merged = config.merge_with_cli(
            cli_targets=["cli.X"],
            cli_output_dir="cli_dir",
            cli_include_private=True,
            cli_exclude_targets=["cli.Excluded"],
        )

        assert merged.targets == ["cli.X"]
        assert merged.output_dir == "cli_dir"
        assert merged.include_private is True
        assert set(merged.exclude_targets) == {"config.Excluded", "cli.Excluded"}


class TestFindPyprojectToml:
    """Tests for find_pyproject_toml()."""

    def test_finds_pyproject_in_current_dir(self) -> None:
        """Finds pyproject.toml in the start directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir).resolve()
            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text("[project]\nname = 'test'")

            result = find_pyproject_toml(tmppath)

            assert result == pyproject

    def test_finds_pyproject_in_parent_dir(self) -> None:
        """Finds pyproject.toml in a parent directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir).resolve()
            pyproject = tmppath / "pyproject.toml"
            pyproject.write_text("[project]\nname = 'test'")

            # Create nested directory
            nested = tmppath / "src" / "pkg"
            nested.mkdir(parents=True)

            result = find_pyproject_toml(nested)

            assert result == pyproject

    def test_returns_none_when_not_found(self) -> None:
        """Returns None when pyproject.toml is not found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Don't create pyproject.toml

            result = find_pyproject_toml(tmppath)

            assert result is None

    def test_ignores_directories_named_pyproject_toml(self) -> None:
        """Ignores directories that happen to be named pyproject.toml."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            # Create directory instead of file
            fake_pyproject = tmppath / "pyproject.toml"
            fake_pyproject.mkdir()

            result = find_pyproject_toml(tmppath)

            assert result is None


class TestLoadConfigFromToml:
    """Tests for load_config_from_toml()."""

    def test_loads_full_config(self) -> None:
        """Loads all configuration options."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["myapp.UserService", "myapp.ProductRepo"]
                output-dir = "custom_stubs"
                include-private = true
                exclude-targets = ["myapp.Internal"]
            """)
            )

            config = load_config_from_toml(pyproject)

            assert config.targets == ["myapp.UserService", "myapp.ProductRepo"]
            assert config.output_dir == "custom_stubs"
            assert config.include_private is True
            assert config.exclude_targets == ["myapp.Internal"]

    def test_loads_partial_config_with_defaults(self) -> None:
        """Missing options use default values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["myapp.UserService"]
            """)
            )

            config = load_config_from_toml(pyproject)

            assert config.targets == ["myapp.UserService"]
            assert config.output_dir == "typed_pytest_stubs"  # default
            assert config.include_private is False  # default
            assert config.exclude_targets == []  # default

    def test_returns_defaults_when_section_missing(self) -> None:
        """Returns defaults when [tool.typed-pytest-generator] is missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [project]
                name = "myapp"
            """)
            )

            config = load_config_from_toml(pyproject)

            assert config.targets == []
            assert config.output_dir == "typed_pytest_stubs"

    def test_raises_on_file_not_found(self) -> None:
        """Raises ConfigLoadError when file doesn't exist."""
        with pytest.raises(ConfigLoadError, match="not found"):
            load_config_from_toml(Path("/nonexistent/pyproject.toml"))

    def test_raises_on_invalid_toml(self) -> None:
        """Raises ConfigLoadError on malformed TOML."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("invalid [ toml content")

            with pytest.raises(ConfigLoadError, match="Invalid TOML"):
                load_config_from_toml(pyproject)


class TestParseConfigDict:
    """Tests for _parse_config_dict()."""

    def test_parses_valid_config(self) -> None:
        """Parses valid configuration dictionary."""
        data = {
            "tool": {
                "typed-pytest-generator": {
                    "targets": ["myapp.A"],
                    "output-dir": "stubs",
                    "include-private": True,
                    "exclude-targets": ["myapp.B"],
                }
            }
        }

        config = _parse_config_dict(data)

        assert config.targets == ["myapp.A"]
        assert config.output_dir == "stubs"
        assert config.include_private is True
        assert config.exclude_targets == ["myapp.B"]

    def test_returns_defaults_for_empty_section(self) -> None:
        """Returns defaults when section is empty."""
        data = {"tool": {"typed-pytest-generator": {}}}

        config = _parse_config_dict(data)

        assert config == GeneratorConfig()

    def test_returns_defaults_for_missing_tool(self) -> None:
        """Returns defaults when [tool] section is missing."""
        data = {"project": {"name": "myapp"}}

        config = _parse_config_dict(data)

        assert config == GeneratorConfig()

    def test_raises_on_invalid_targets_type(self) -> None:
        """Raises ConfigLoadError when targets is not a list."""
        data = {"tool": {"typed-pytest-generator": {"targets": "not-a-list"}}}

        with pytest.raises(ConfigLoadError, match="'targets' must be a list"):
            _parse_config_dict(data)

    def test_raises_on_non_string_target(self) -> None:
        """Raises ConfigLoadError when target is not a string."""
        data = {"tool": {"typed-pytest-generator": {"targets": [123, "valid"]}}}

        with pytest.raises(ConfigLoadError, match="must be strings"):
            _parse_config_dict(data)

    def test_raises_on_invalid_output_dir_type(self) -> None:
        """Raises ConfigLoadError when output-dir is not a string."""
        data = {"tool": {"typed-pytest-generator": {"output-dir": 123}}}

        with pytest.raises(ConfigLoadError, match="'output-dir' must be a string"):
            _parse_config_dict(data)

    def test_raises_on_invalid_include_private_type(self) -> None:
        """Raises ConfigLoadError when include-private is not a boolean."""
        data = {"tool": {"typed-pytest-generator": {"include-private": "yes"}}}

        with pytest.raises(
            ConfigLoadError, match="'include-private' must be a boolean"
        ):
            _parse_config_dict(data)

    def test_raises_on_invalid_exclude_targets_type(self) -> None:
        """Raises ConfigLoadError when exclude-targets is not a list."""
        data = {"tool": {"typed-pytest-generator": {"exclude-targets": "not-a-list"}}}

        with pytest.raises(ConfigLoadError, match="'exclude-targets' must be a list"):
            _parse_config_dict(data)


class TestLoadConfig:
    """Tests for load_config() main entry point."""

    def test_loads_from_explicit_path(self) -> None:
        """Loads config from explicitly specified path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "custom.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = ["explicit.Target"]
            """)
            )

            config = load_config(pyproject)

            assert config.targets == ["explicit.Target"]

    def test_returns_defaults_when_no_config_found(self) -> None:
        """Returns defaults when no config file is found."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Change to empty directory with no pyproject.toml
            import os

            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                config = load_config(None)
                assert config == GeneratorConfig()
            finally:
                os.chdir(original_cwd)


class TestConfigIntegration:
    """Integration tests for complete configuration scenarios."""

    def test_complete_workflow_with_config_file(self) -> None:
        """Complete workflow: load config, merge CLI, filter targets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create config file
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                targets = [
                    "myapp.services.UserService",
                    "myapp.services.ProductService",
                    "myapp.internal.PrivateHelper"
                ]
                output-dir = "generated_stubs"
                exclude-targets = ["myapp.internal.PrivateHelper"]
            """)
            )

            # Load and process config
            config = load_config_from_toml(pyproject)

            # Merge with CLI (add more exclusions)
            config = config.merge_with_cli(
                cli_exclude_targets=["myapp.services.ProductService"]
            )

            # Get final targets
            targets = config.get_filtered_targets()

            # Only UserService should remain
            assert targets == ["myapp.services.UserService"]
            assert config.output_dir == "generated_stubs"

    def test_cli_targets_with_config_exclusions(self) -> None:
        """CLI targets work with config exclusions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text(
                dedent("""
                [tool.typed-pytest-generator]
                exclude-targets = ["myapp.Excluded"]
            """)
            )

            config = load_config_from_toml(pyproject)
            config = config.merge_with_cli(
                cli_targets=["myapp.A", "myapp.Excluded", "myapp.B"]
            )

            targets = config.get_filtered_targets()

            assert targets == ["myapp.A", "myapp.B"]

    def test_empty_config_with_cli_only(self) -> None:
        """Empty config file, all settings from CLI."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pyproject = Path(tmpdir) / "pyproject.toml"
            pyproject.write_text("[project]\nname = 'myapp'")

            config = load_config_from_toml(pyproject)
            config = config.merge_with_cli(
                cli_targets=["cli.Target"],
                cli_output_dir="cli_output",
                cli_include_private=True,
            )

            assert config.targets == ["cli.Target"]
            assert config.output_dir == "cli_output"
            assert config.include_private is True

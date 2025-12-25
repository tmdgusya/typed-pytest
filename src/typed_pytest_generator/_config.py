"""Configuration loading for typed-pytest-generator.

Supports loading configuration from pyproject.toml [tool.typed-pytest-generator] section.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GeneratorConfig:
    """Configuration for the stub generator.

    Attributes:
        targets: List of fully qualified class names to generate stubs for
        output_dir: Directory where stub files will be generated
        include_private: Whether to include private methods (starting with _)
        exclude_targets: List of fully qualified class names to exclude
    """

    targets: list[str] = field(default_factory=list)
    output_dir: str = "typed_pytest_stubs"
    include_private: bool = False
    exclude_targets: list[str] = field(default_factory=list)

    def get_filtered_targets(self) -> list[str]:
        """Get targets with exclusions applied.

        Returns:
            List of targets after removing excluded ones
        """
        if not self.exclude_targets:
            return self.targets

        exclude_set = set(self.exclude_targets)
        return [t for t in self.targets if t not in exclude_set]

    def merge_with_cli(
        self,
        cli_targets: list[str] | None = None,
        cli_output_dir: str | None = None,
        cli_include_private: bool | None = None,
        cli_exclude_targets: list[str] | None = None,
    ) -> GeneratorConfig:
        """Merge config with CLI arguments (CLI takes precedence).

        Args:
            cli_targets: Targets from CLI (overrides config if provided)
            cli_output_dir: Output directory from CLI
            cli_include_private: Include private flag from CLI
            cli_exclude_targets: Exclude targets from CLI (merged with config)

        Returns:
            New GeneratorConfig with merged values
        """
        # CLI targets completely override config targets if provided
        targets = cli_targets if cli_targets else self.targets

        # CLI output_dir overrides config if provided
        output_dir = cli_output_dir if cli_output_dir else self.output_dir

        # CLI include_private overrides if explicitly set (True)
        include_private = (
            cli_include_private if cli_include_private else self.include_private
        )

        # Exclude targets are merged (union of both)
        exclude_targets = list(
            set(self.exclude_targets) | set(cli_exclude_targets or [])
        )

        return GeneratorConfig(
            targets=targets,
            output_dir=output_dir,
            include_private=include_private,
            exclude_targets=exclude_targets,
        )


class ConfigLoadError(Exception):
    """Raised when configuration loading fails."""


def find_pyproject_toml(start_path: Path | None = None) -> Path | None:
    """Find pyproject.toml by walking up from start_path.

    Args:
        start_path: Starting directory (defaults to current working directory)

    Returns:
        Path to pyproject.toml if found, None otherwise
    """
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Walk up the directory tree
    while current != current.parent:
        pyproject = current / "pyproject.toml"
        if pyproject.is_file():
            return pyproject
        current = current.parent

    # Check root directory
    pyproject = current / "pyproject.toml"
    if pyproject.is_file():
        return pyproject

    return None


def load_config_from_toml(toml_path: Path) -> GeneratorConfig:
    """Load configuration from a pyproject.toml file.

    Args:
        toml_path: Path to pyproject.toml

    Returns:
        GeneratorConfig with values from the file

    Raises:
        ConfigLoadError: If file cannot be read or parsed
    """
    try:
        with toml_path.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError as e:
        raise ConfigLoadError(f"Config file not found: {toml_path}") from e
    except tomllib.TOMLDecodeError as e:
        raise ConfigLoadError(f"Invalid TOML in {toml_path}: {e}") from e

    return _parse_config_dict(data)


def _parse_config_dict(data: dict[str, Any]) -> GeneratorConfig:
    """Parse configuration from a dictionary (parsed TOML).

    Args:
        data: Dictionary from parsed pyproject.toml

    Returns:
        GeneratorConfig with parsed values
    """
    # Navigate to [tool.typed-pytest-generator] section
    tool_config = data.get("tool", {}).get("typed-pytest-generator", {})

    if not tool_config:
        # No configuration found, return defaults
        return GeneratorConfig()

    # Extract and validate configuration values
    targets = tool_config.get("targets", [])
    if not isinstance(targets, list):
        raise ConfigLoadError("'targets' must be a list of strings")
    if not all(isinstance(t, str) for t in targets):
        raise ConfigLoadError("All 'targets' must be strings")

    output_dir = tool_config.get("output-dir", "typed_pytest_stubs")
    if not isinstance(output_dir, str):
        raise ConfigLoadError("'output-dir' must be a string")

    include_private = tool_config.get("include-private", False)
    if not isinstance(include_private, bool):
        raise ConfigLoadError("'include-private' must be a boolean")

    exclude_targets = tool_config.get("exclude-targets", [])
    if not isinstance(exclude_targets, list):
        raise ConfigLoadError("'exclude-targets' must be a list of strings")
    if not all(isinstance(t, str) for t in exclude_targets):
        raise ConfigLoadError("All 'exclude-targets' must be strings")

    return GeneratorConfig(
        targets=targets,
        output_dir=output_dir,
        include_private=include_private,
        exclude_targets=exclude_targets,
    )


def load_config(config_path: Path | None = None) -> GeneratorConfig:
    """Load configuration, auto-discovering pyproject.toml if not specified.

    Args:
        config_path: Explicit path to config file, or None to auto-discover

    Returns:
        GeneratorConfig with loaded or default values
    """
    if config_path is not None:
        return load_config_from_toml(config_path)

    # Try to find pyproject.toml
    pyproject_path = find_pyproject_toml()
    if pyproject_path is not None:
        return load_config_from_toml(pyproject_path)

    # No config file found, return defaults
    return GeneratorConfig()

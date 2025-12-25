"""CLI tool for typed-pytest-generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from typed_pytest_generator import generate_stubs
from typed_pytest_generator._config import (
    ConfigLoadError,
    load_config,
)


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate stub files for typed-pytest TypedMock auto-completion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use pyproject.toml configuration (auto-discovered)
  typed-pytest-generator

  # Generate stubs for specified classes (overrides config)
  typed-pytest-generator -t mypkg.services.UserService mypkg.repos.OrderRepo

  # Exclude specific targets
  typed-pytest-generator -t mypkg.* --exclude mypkg.internal.PrivateClass

  # Specify output directory
  typed-pytest-generator -o typed_stubs -t mypkg.services.UserService

  # Use explicit config file
  typed-pytest-generator --config /path/to/pyproject.toml

Configuration in pyproject.toml:
  [tool.typed-pytest-generator]
  targets = ["mypkg.services.UserService", "mypkg.repos.ProductRepository"]
  output-dir = "typed_pytest_stubs"
  include-private = false
  exclude-targets = ["mypkg.internal.PrivateClass"]
        """,
    )

    parser.add_argument(
        "-t",
        "--targets",
        nargs="+",
        default=None,
        help="Fully qualified class names to generate stubs for (overrides config)",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help="Output directory for generated stubs (default: typed_pytest_stubs)",
    )

    parser.add_argument(
        "--include-private",
        action="store_true",
        default=False,
        help="Include private methods (starting with _)",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        nargs="+",
        default=None,
        dest="exclude_targets",
        help="Fully qualified class names to exclude (merged with config)",
    )

    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        dest="config_path",
        help="Path to pyproject.toml (default: auto-discover)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args(argv)

    try:
        # Load configuration from file
        config = load_config(args.config_path)

        if args.verbose and args.config_path:
            print(
                f"[typed-pytest-generator] Using config: {args.config_path}",
                file=sys.stderr,
            )

        # Merge with CLI arguments (CLI takes precedence)
        config = config.merge_with_cli(
            cli_targets=args.targets,
            cli_output_dir=args.output_dir,
            cli_include_private=args.include_private if args.include_private else None,
            cli_exclude_targets=args.exclude_targets,
        )

        # Get filtered targets (with exclusions applied)
        targets = config.get_filtered_targets()

        if not targets:
            print(
                "[typed-pytest-generator] Error: No targets specified. "
                "Use -t/--targets or configure in pyproject.toml",
                file=sys.stderr,
            )
            return 1

        if args.verbose:
            print(f"[typed-pytest-generator] Targets: {targets}", file=sys.stderr)
            print(
                f"[typed-pytest-generator] Output dir: {config.output_dir}",
                file=sys.stderr,
            )
            print(
                f"[typed-pytest-generator] Include private: {config.include_private}",
                file=sys.stderr,
            )
            if config.exclude_targets:
                print(
                    f"[typed-pytest-generator] Excluded: {config.exclude_targets}",
                    file=sys.stderr,
                )

        generated = generate_stubs(
            targets=targets,
            output_dir=config.output_dir,
            include_private=config.include_private,
        )

        if args.verbose:
            print(
                f"[typed-pytest-generator] Generated {len(generated)} stub files:",
                file=sys.stderr,
            )
            for path in generated:
                print(f"  - {path}", file=sys.stderr)

        return 0

    except ConfigLoadError as e:
        print(f"[typed-pytest-generator] Config error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[typed-pytest-generator] Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

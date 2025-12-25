"""CLI tool for typed-pytest-generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from typed_pytest_generator import generate_stubs


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate .pyi stub files for typed-pytest TypedMock auto-completion.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate stubs for specified classes
  typed-pytest-generator --targets mypkg.services.UserService mypkg.repos.OrderRepo

  # Specify output directory
  typed-pytest-generator --output-dir typed_stubs --targets mypkg.services.UserService

  # Include private methods
  typed-pytest-generator --include-private --targets mypkg.services.UserService
        """,
    )

    parser.add_argument(
        "-t",
        "--targets",
        nargs="+",
        required=True,
        help="Fully qualified class names to generate stubs for",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        default="typed_pytest_stubs",
        help="Output directory for generated stubs (default: typed_pytest_stubs)",
    )

    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private methods (starting with _)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose output",
    )

    args = parser.parse_args(argv)

    if args.verbose:
        print(f"[typed-pytest-generator] Targets: {args.targets}", file=sys.stderr)
        print(f"[typed-pytest-generator] Output dir: {args.output_dir}", file=sys.stderr)
        print(f"[typed-pytest-generator] Include private: {args.include_private}", file=sys.stderr)

    try:
        generated = generate_stubs(
            targets=args.targets,
            output_dir=args.output_dir,
            include_private=args.include_private,
        )

        if args.verbose:
            print(f"[typed-pytest-generator] Generated {len(generated)} stub files:", file=sys.stderr)
            for path in generated:
                print(f"  - {path}", file=sys.stderr)

        return 0

    except Exception as e:
        print(f"[typed-pytest-generator] Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

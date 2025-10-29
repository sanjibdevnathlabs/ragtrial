"""
Migration CLI entry point.

Usage:
    python -m migration generate <description>
    python -m migration up [--steps N]
    python -m migration down [--steps N]
    python -m migration status
    python -m migration reset
"""

import argparse
import sys

from migration.commands import (
    down_command,
    generate_command,
    reset_command,
    status_command,
    up_command,
)


def main():
    """CLI entry point for migration commands."""
    parser = argparse.ArgumentParser(
        description="Database migration management (Laravel/Goose style)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate a new migration file"
    )
    generate_parser.add_argument(
        "description", help="Migration description (e.g., create_users_table)"
    )

    # Up command
    up_parser = subparsers.add_parser("up", help="Apply pending migrations")
    up_parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Number of migrations to apply (default: all)",
    )

    # Down command
    down_parser = subparsers.add_parser("down", help="Rollback applied migrations")
    down_parser.add_argument(
        "--steps",
        type=int,
        default=1,
        help="Number of migrations to rollback (default: 1)",
    )

    # Status command
    subparsers.add_parser("status", help="Show migration status")

    # Reset command
    reset_parser = subparsers.add_parser(
        "reset", help="Rollback all migrations and reapply"
    )
    reset_parser.add_argument(
        "--yes", action="store_true", help="Skip confirmation prompt"
    )

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to appropriate command
    try:
        if args.command == "generate":
            generate_command(args.description)

        elif args.command == "up":
            up_command(steps=args.steps)

        elif args.command == "down":
            down_command(steps=args.steps)

        elif args.command == "status":
            status_command()

        elif args.command == "reset":
            reset_command(confirm=args.yes)

        else:
            print(f"❌ Unknown command: {args.command}")
            parser.print_help()
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

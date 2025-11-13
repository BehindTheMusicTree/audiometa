#!/usr/bin/env python3
"""AudioMeta CLI - Command-line interface for audio metadata operations."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from audiometa import (
    UnifiedMetadataKey,
    delete_all_metadata,
    get_full_metadata,
    get_unified_metadata,
    update_metadata,
    validate_metadata_for_update,
)
from audiometa.exceptions import FileTypeNotSupportedError, InvalidRatingValueError
from audiometa.utils.types import UnifiedMetadata


def format_output(data: Any, output_format: str) -> str:
    """Format output data according to specified format."""
    if output_format == "json":
        return json.dumps(data, indent=2)
    if output_format == "yaml":
        try:
            import yaml  # type: ignore[import-untyped]

            result = yaml.dump(data, default_flow_style=False)
            return str(result) if result is not None else ""
        except ImportError:
            sys.stderr.write("Warning: PyYAML not installed, falling back to JSON\n")
            return json.dumps(data, indent=2)
    elif output_format == "table":
        return format_as_table(data)
    else:
        return str(data)


def _handle_file_operation_error(exception: Exception, file_path: Path | str, continue_on_error: bool) -> None:
    """Handle exceptions from file operations and write appropriate error messages to stderr.

    Args:
        exception: The exception that was caught
        file_path: The path to the file being operated on
        continue_on_error: Whether to continue on errors or exit
    """
    if isinstance(exception, FileNotFoundError):
        error_msg = f"Error: File not found: {file_path}\n"
    elif isinstance(exception, FileTypeNotSupportedError):
        error_msg = f"Error: File type not supported: {file_path}\n"
    elif isinstance(exception, PermissionError | OSError):
        error_msg = f"Error: {exception!s}\n"
    else:
        error_msg = f"Error: {exception!s}\n"

    sys.stderr.write(error_msg)

    if not continue_on_error:
        sys.exit(1)


def format_as_table(data: dict[str, Any]) -> str:
    """Format metadata as a simple table."""
    lines = []

    if "unified_metadata" in data:
        lines.append("=== UNIFIED METADATA ===")
        for key, value in data["unified_metadata"].items():
            if value is not None:
                lines.append(f"{key:20}: {value}")
        lines.append("")

    if "technical_info" in data:
        lines.append("=== TECHNICAL INFO ===")
        for key, value in data["technical_info"].items():
            if value is not None:
                lines.append(f"{key:20}: {value}")
        lines.append("")

    if "metadata_format" in data:
        lines.append("=== FORMAT METADATA ===")
        for metadata_format_name, format_data in data["metadata_format"].items():
            if format_data:
                lines.append(f"\n{metadata_format_name.upper()}:")
                for key, value in format_data.items():
                    if value is not None:
                        lines.append(f"  {key:18}: {value}")

    return "\n".join(lines)


def _read_metadata(args: argparse.Namespace) -> None:
    """Read and display metadata from audio file(s)."""
    files = expand_file_patterns(
        args.files, getattr(args, "recursive", False), getattr(args, "continue_on_error", False)
    )

    if not files:
        return  # No files found, but continue_on_error was set

    for file_path in files:
        try:
            if getattr(args, "format_type", None) == "unified":
                metadata: Any = get_unified_metadata(file_path)
            else:
                metadata = get_full_metadata(
                    file_path,
                    include_headers=not getattr(args, "no_headers", False),
                    include_technical=not getattr(args, "no_technical", False),
                )

            output = format_output(metadata, args.output_format)

            if args.output:
                try:
                    with Path(args.output).open("w") as f:
                        f.write(output)
                except (PermissionError, OSError) as e:
                    _handle_file_operation_error(e, args.output, args.continue_on_error)
            else:
                sys.stdout.write(output)
                if not output.endswith("\n"):
                    sys.stdout.write("\n")

        except (FileTypeNotSupportedError, FileNotFoundError, PermissionError, OSError, Exception) as e:
            _handle_file_operation_error(e, file_path, args.continue_on_error)


def _write_metadata(args: argparse.Namespace) -> None:
    """Write metadata to audio file(s)."""
    files = expand_file_patterns(
        args.files, getattr(args, "recursive", False), getattr(args, "continue_on_error", False)
    )

    # Build metadata dictionary from command line arguments
    metadata: UnifiedMetadata = {}

    # Validate rating
    if args.rating is not None:
        if args.rating < 0:
            sys.stderr.write("Error: rating cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.RATING] = args.rating

    # Validate year
    if args.year is not None:
        if args.year < 0:
            sys.stderr.write("Error: year cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.RELEASE_DATE] = str(args.year)

    # Only add non-empty string values
    if args.title and args.title.strip():
        metadata[UnifiedMetadataKey.TITLE] = args.title
    if args.artist and args.artist.strip():
        metadata[UnifiedMetadataKey.ARTISTS] = [args.artist]
    if args.album and args.album.strip():
        metadata[UnifiedMetadataKey.ALBUM] = args.album
    if args.genre and args.genre.strip():
        metadata[UnifiedMetadataKey.GENRES_NAMES] = [args.genre]
    if args.comment and args.comment.strip():
        metadata[UnifiedMetadataKey.COMMENT] = args.comment

    try:
        validate_metadata_for_update(metadata)
    except (ValueError, InvalidRatingValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    for file_path in files:
        try:
            update_kwargs: dict[str, Any] = {}
            update_metadata(file_path, metadata, **update_kwargs)
            if len(files) > 1:
                sys.stdout.write(f"Updated metadata for: {file_path}\n")
            else:
                sys.stdout.write("Updated metadata\n")

        except (FileTypeNotSupportedError, FileNotFoundError, PermissionError, OSError, Exception) as e:
            _handle_file_operation_error(e, file_path, args.continue_on_error)


def _delete_metadata(args: argparse.Namespace) -> None:
    """Delete metadata from audio file(s)."""
    files = expand_file_patterns(
        args.files, getattr(args, "recursive", False), getattr(args, "continue_on_error", False)
    )

    for file_path in files:
        try:
            success = delete_all_metadata(file_path)
            if success:
                if len(files) > 1:
                    sys.stdout.write(f"Deleted metadata from: {file_path}\n")
                else:
                    sys.stdout.write("Deleted metadata\n")
            else:
                sys.stderr.write(f"Warning: No metadata found in: {file_path}\n")

        except (FileTypeNotSupportedError, FileNotFoundError, PermissionError, OSError, Exception) as e:
            _handle_file_operation_error(e, file_path, args.continue_on_error)


def expand_file_patterns(patterns: list[str], recursive: bool = False, continue_on_error: bool = False) -> list[Path]:
    """Expand file patterns and globs into a list of Path objects."""
    files = []

    for pattern in patterns:
        path = Path(pattern)

        if path.exists():
            if path.is_file():
                files.append(path)
            elif path.is_dir() and recursive:
                # Recursively find audio files
                for ext in [".mp3", ".flac", ".wav"]:
                    files.extend(path.rglob(f"*{ext}"))
        else:
            # Try glob pattern
            pattern_path = Path(pattern)
            if "*" in pattern or "?" in pattern or "[" in pattern:
                # Use glob for patterns
                if pattern_path.is_absolute():
                    matches = list(pattern_path.parent.glob(pattern_path.name))
                else:
                    matches = list(Path().glob(pattern))
            else:
                matches = [pattern_path]
            for match in matches:
                # Skip hidden files (those starting with .)
                if not match.name.startswith(".") and match.is_file():
                    files.append(match)

    if not files:
        if continue_on_error:
            sys.stderr.write("Warning: No valid audio files found\n")
            return []
        error_msg = "Error: No valid audio files found\n"
        sys.stderr.write(error_msg)
        sys.exit(1)

    return files


def _create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="AudioMeta CLI - Command-line interface for audio metadata operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  audiometa read song.mp3                    # Read full metadata
  audiometa unified song.mp3                 # Read unified metadata only
  audiometa read *.mp3 --format table        # Read multiple files as table
  audiometa write song.mp3 --title "New Title" --artist "Artist"
  audiometa delete song.mp3                  # Delete all metadata
  audiometa read music/ --recursive          # Process directory recursively
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read metadata from audio file(s)")
    read_parser.add_argument("files", nargs="+", help="Audio file(s) or pattern(s)")
    read_parser.add_argument(
        "--format",
        choices=["json", "yaml", "table"],
        default="json",
        dest="output_format",
        help="Output format (default: json)",
    )
    read_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    read_parser.add_argument("--no-headers", action="store_true", help="Exclude header information")
    read_parser.add_argument("--no-technical", action="store_true", help="Exclude technical information")
    read_parser.add_argument("--recursive", "-r", action="store_true", help="Process directories recursively")
    read_parser.add_argument(
        "--continue-on-error", action="store_true", help="Continue processing other files on error"
    )
    read_parser.set_defaults(func=_read_metadata)

    # Unified command
    unified_parser = subparsers.add_parser("unified", help="Read unified metadata only")
    unified_parser.add_argument("files", nargs="+", help="Audio file(s) or pattern(s)")
    unified_parser.add_argument(
        "--format",
        choices=["json", "yaml", "table"],
        default="json",
        dest="output_format",
        help="Output format (default: json)",
    )
    unified_parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    unified_parser.add_argument("--recursive", "-r", action="store_true", help="Process directories recursively")
    unified_parser.add_argument(
        "--continue-on-error", action="store_true", help="Continue processing other files on error"
    )
    unified_parser.set_defaults(func=_read_metadata, format_type="unified")

    # Write command
    write_parser = subparsers.add_parser("write", help="Write metadata to audio file(s)")
    write_parser.add_argument("files", nargs="+", help="Audio file(s) or pattern(s)")
    write_parser.add_argument("--title", help="Song title")
    write_parser.add_argument("--artist", help="Artist name")
    write_parser.add_argument("--album", help="Album name")
    write_parser.add_argument("--year", type=int, help="Release year")
    write_parser.add_argument("--genre", help="Genre")
    write_parser.add_argument("--rating", type=float, help="Rating value (integer or whole-number float like 196.0)")
    write_parser.add_argument("--comment", help="Comment")
    write_parser.add_argument("--recursive", "-r", action="store_true", help="Process directories recursively")
    write_parser.add_argument(
        "--continue-on-error", action="store_true", help="Continue processing other files on error"
    )
    write_parser.set_defaults(func=_write_metadata)

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete all metadata from audio file(s)")
    delete_parser.add_argument("files", nargs="+", help="Audio file(s) or pattern(s)")
    delete_parser.add_argument("--recursive", "-r", action="store_true", help="Process directories recursively")
    delete_parser.add_argument(
        "--continue-on-error", action="store_true", help="Continue processing other files on error"
    )
    delete_parser.set_defaults(func=_delete_metadata)

    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = _create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        sys.exit(1)
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()

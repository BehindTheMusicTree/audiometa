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
from audiometa.exceptions import (
    FileTypeNotSupportedError,
    InvalidRatingValueError,
    MetadataFormatNotSupportedByAudioFormatError,
)
from audiometa.utils.metadata_format import MetadataFormat
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

    # Handle unified metadata dict directly (from unified command)
    if "unified_metadata" not in data and isinstance(data, dict):
        # Check if this is a unified metadata dict (has UnifiedMetadataKey values)
        unified_keys = {
            "title",
            "artists",
            "album",
            "album_artists",
            "genres_names",
            "release_date",
            "track_number",
            "disc_number",
            "disc_total",
            "rating",
            "bpm",
            "language",
            "composer",
            "publisher",
            "copyright",
            "unsynchronized_lyrics",
            "comment",
            "replaygain",
            "archival_location",
        }
        if unified_keys.intersection(set(data.keys())):
            # This is a unified metadata dict, wrap it
            data = {"unified_metadata": data}

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

    # String fields
    if args.title and args.title.strip():
        metadata[UnifiedMetadataKey.TITLE] = args.title
    if args.album and args.album.strip():
        metadata[UnifiedMetadataKey.ALBUM] = args.album
    if args.language and args.language.strip():
        metadata[UnifiedMetadataKey.LANGUAGE] = args.language
    if args.publisher and args.publisher.strip():
        metadata[UnifiedMetadataKey.PUBLISHER] = args.publisher
    if args.copyright and args.copyright.strip():
        metadata[UnifiedMetadataKey.COPYRIGHT] = args.copyright
    if args.lyrics and args.lyrics.strip():
        metadata[UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS] = args.lyrics
    if args.comment and args.comment.strip():
        metadata[UnifiedMetadataKey.COMMENT] = args.comment
    if args.replaygain and args.replaygain.strip():
        metadata[UnifiedMetadataKey.REPLAYGAIN] = args.replaygain
    if args.archival_location and args.archival_location.strip():
        metadata[UnifiedMetadataKey.ARCHIVAL_LOCATION] = args.archival_location

    # List fields (can be specified multiple times)
    if args.artist:
        artists = [a.strip() for a in args.artist if a and a.strip()]
        if artists:
            metadata[UnifiedMetadataKey.ARTISTS] = artists
    if args.album_artists:
        album_artists = [a.strip() for a in args.album_artists if a and a.strip()]
        if album_artists:
            metadata[UnifiedMetadataKey.ALBUM_ARTISTS] = album_artists
    if args.genre:
        genres = [g.strip() for g in args.genre if g and g.strip()]
        if genres:
            metadata[UnifiedMetadataKey.GENRES_NAMES] = genres
    if args.composer:
        composers = [c.strip() for c in args.composer if c and c.strip()]
        if composers:
            metadata[UnifiedMetadataKey.COMPOSERS] = composers

    # Integer fields
    if args.rating is not None:
        if args.rating < 0:
            sys.stderr.write("Error: rating cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.RATING] = args.rating
    if args.disc_number is not None:
        if args.disc_number < 0:
            sys.stderr.write("Error: disc-number cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.DISC_NUMBER] = args.disc_number
    if args.disc_total is not None:
        if args.disc_total < 0:
            sys.stderr.write("Error: disc-total cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.DISC_TOTAL] = args.disc_total
    if args.bpm is not None:
        if args.bpm < 0:
            sys.stderr.write("Error: bpm cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.BPM] = args.bpm

    # Release date (year takes precedence over release-date if both specified)
    if args.year is not None:
        if args.year < 0:
            sys.stderr.write("Error: year cannot be negative\n")
            sys.exit(1)
        metadata[UnifiedMetadataKey.RELEASE_DATE] = str(args.year)
    elif args.release_date and args.release_date.strip():
        metadata[UnifiedMetadataKey.RELEASE_DATE] = args.release_date

    # Track number (string, can be "5" or "5/12")
    if args.track_number and args.track_number.strip():
        metadata[UnifiedMetadataKey.TRACK_NUMBER] = args.track_number

    # Check if any metadata was provided
    if not metadata:
        sys.stderr.write("Error: No metadata fields specified\n")
        sys.exit(1)

    try:
        validate_metadata_for_update(metadata)
    except (ValueError, InvalidRatingValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)

    for file_path in files:
        try:
            update_kwargs: dict[str, Any] = {}
            if hasattr(args, "force_format") and args.force_format:
                format_map = {
                    "id3v2": MetadataFormat.ID3V2,
                    "id3v1": MetadataFormat.ID3V1,
                    "vorbis": MetadataFormat.VORBIS,
                    "riff": MetadataFormat.RIFF,
                }
                update_kwargs["metadata_format"] = format_map[args.force_format]
            update_metadata(file_path, metadata, **update_kwargs)
            if len(files) > 1:
                sys.stdout.write(f"Updated metadata for: {file_path}\n")
            else:
                sys.stdout.write("Updated metadata\n")

        except (FileTypeNotSupportedError, FileNotFoundError, PermissionError, OSError, Exception) as e:
            if isinstance(e, MetadataFormatNotSupportedByAudioFormatError):
                sys.stderr.write(f"Error: {e}\n")
                if not args.continue_on_error:
                    sys.exit(1)
            else:
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
    write_parser.add_argument(
        "--artist", action="append", help="Artist name (can be specified multiple times for multiple artists)"
    )
    write_parser.add_argument("--album", help="Album name")
    write_parser.add_argument(
        "--album-artist",
        action="append",
        dest="album_artists",
        help="Album artist name (can be specified multiple times)",
    )
    write_parser.add_argument("--year", type=int, help="Release year")
    write_parser.add_argument("--release-date", help="Release date in YYYY or YYYY-MM-DD format")
    write_parser.add_argument(
        "--genre", action="append", help="Genre (can be specified multiple times for multiple genres)"
    )
    write_parser.add_argument("--track-number", help="Track number (e.g., '5' or '5/12')")
    write_parser.add_argument("--disc-number", type=int, help="Disc number")
    write_parser.add_argument("--disc-total", type=int, help="Total number of discs")
    write_parser.add_argument("--rating", type=float, help="Rating value (integer or whole-number float like 196.0)")
    write_parser.add_argument("--bpm", type=int, help="Beats per minute")
    write_parser.add_argument("--language", help="Language code (3 characters, e.g., 'eng')")
    write_parser.add_argument("--composer", action="append", help="Composer name (can be specified multiple times)")
    write_parser.add_argument("--publisher", help="Publisher name")
    write_parser.add_argument("--copyright", help="Copyright information")
    write_parser.add_argument("--lyrics", help="Unsynchronized lyrics text")
    write_parser.add_argument("--comment", help="Comment")
    write_parser.add_argument("--replaygain", help="ReplayGain information")
    write_parser.add_argument("--archival-location", help="Archival location")
    write_parser.add_argument(
        "--force-format",
        choices=["id3v2", "id3v1", "vorbis", "riff"],
        help="Force a specific metadata format (id3v2, id3v1, vorbis, or riff)",
    )
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

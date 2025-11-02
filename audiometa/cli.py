#!/usr/bin/env python3
"""AudioMeta CLI - Command-line interface for audio metadata operations."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from audiometa import (
    get_full_metadata,
    get_unified_metadata,
    update_metadata,
    delete_all_metadata,
    UnifiedMetadataKey,
)
from audiometa.exceptions import FileTypeNotSupportedError


def format_output(data: Any, output_format: str) -> str:
    """Format output data according to specified format."""
    if output_format == "json":
        return json.dumps(data, indent=2)
    elif output_format == "yaml":
        try:
            import yaml  # type: ignore[import-untyped]
            return yaml.dump(data, default_flow_style=False)
        except ImportError:
            print("Warning: PyYAML not installed, falling back to JSON", file=sys.stderr)
            return json.dumps(data, indent=2)
    elif output_format == "table":
        return format_as_table(data)
    else:
        return str(data)


def format_as_table(data: Dict[str, Any]) -> str:
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
    
    if "format_metadata" in data:
        lines.append("=== FORMAT METADATA ===")
        for format_name, format_data in data["format_metadata"].items():
            if format_data:
                lines.append(f"\n{format_name.upper()}:")
                for key, value in format_data.items():
                    if value is not None:
                        lines.append(f"  {key:18}: {value}")
    
    return "\n".join(lines)


def read_metadata(args) -> None:
    """Read and display metadata from audio file(s)."""
    files = expand_file_patterns(args.files, getattr(args, 'recursive', False), getattr(args, 'continue_on_error', False))
    
    if not files:
        return  # No files found, but continue_on_error was set
    
    for file_path in files:
        try:
            if getattr(args, 'format_type', None) == "unified":
                metadata = get_unified_metadata(file_path)
            else:
                metadata = get_full_metadata(
                    file_path,
                    include_headers=not getattr(args, 'no_headers', False),
                    include_technical=not getattr(args, 'no_technical', False)
                )
            
            output = format_output(metadata, args.output_format)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Metadata saved to {args.output}")
            else:
                if len(files) > 1:
                    print(f"\n=== {file_path} ===")
                print(output)
                
        except (FileTypeNotSupportedError, FileNotFoundError) as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            if not args.continue_on_error:
                sys.exit(1)
        except Exception as e:
            print(f"Unexpected error processing {file_path}: {e}", file=sys.stderr)
            if not args.continue_on_error:
                sys.exit(1)


def write_metadata(args) -> None:
    """Write metadata to audio file(s)."""
    files = expand_file_patterns(args.files, getattr(args, 'recursive', False), getattr(args, 'continue_on_error', False))
    
    # Build metadata dictionary from command line arguments
    metadata = {}
    
    if args.title:
        metadata[UnifiedMetadataKey.TITLE] = args.title
    if args.artist:
        metadata[UnifiedMetadataKey.ARTISTS] = [args.artist]
    if args.album:
        metadata[UnifiedMetadataKey.ALBUM] = args.album
    if args.year:
        metadata[UnifiedMetadataKey.RELEASE_DATE] = str(args.year)
    if args.genre:
        metadata[UnifiedMetadataKey.GENRE] = args.genre
    if args.rating is not None:
        # Validate rating
        if not (0 <= args.rating <= 100):
            print(f"Error: Rating must be between 0 and 100, got {args.rating}", file=sys.stderr)
            sys.exit(1)
        metadata[UnifiedMetadataKey.RATING] = args.rating
    if args.comment:
        metadata[UnifiedMetadataKey.COMMENT] = args.comment
    
    if not metadata:
        print("Error: No metadata fields specified to write", file=sys.stderr)
        sys.exit(1)
    
    for file_path in files:
        try:
            update_metadata(file_path, metadata)
            print(f"Updated metadata for {file_path}")
            
        except (FileTypeNotSupportedError, FileNotFoundError) as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            if not args.continue_on_error:
                sys.exit(1)
        except Exception as e:
            print(f"Unexpected error processing {file_path}: {e}", file=sys.stderr)
            if not args.continue_on_error:
                sys.exit(1)


def delete_metadata(args) -> None:
    """Delete metadata from audio file(s)."""
    files = expand_file_patterns(args.files, getattr(args, 'recursive', False), getattr(args, 'continue_on_error', False))
    
    for file_path in files:
        try:
            success = delete_all_metadata(file_path)
            if success:
                print(f"Deleted all metadata from {file_path}")
            else:
                print(f"No metadata found in {file_path}")
                
        except (FileTypeNotSupportedError, FileNotFoundError) as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)
            if not args.continue_on_error:
                sys.exit(1)
        except Exception as e:
            print(f"Unexpected error processing {file_path}: {e}", file=sys.stderr)
            if not args.continue_on_error:
                sys.exit(1)


def expand_file_patterns(patterns: List[str], recursive: bool = False, continue_on_error: bool = False) -> List[Path]:
    """Expand file patterns and globs into a list of Path objects."""
    files = []
    
    for pattern in patterns:
        path = Path(pattern)
        
        if path.exists():
            if path.is_file():
                files.append(path)
            elif path.is_dir() and recursive:
                # Recursively find audio files
                for ext in ['.mp3', '.flac', '.wav']:
                    files.extend(path.rglob(f'*{ext}'))
        else:
            # Try glob pattern
            import glob
            matches = glob.glob(pattern)
            for match in matches:
                match_path = Path(match)
                if match_path.is_file():
                    files.append(match_path)
    
    if not files:
        if continue_on_error:
            print("Warning: No valid audio files found", file=sys.stderr)
            return []
        else:
            print("Error: No valid audio files found", file=sys.stderr)
            sys.exit(1)
    
    return files


def create_parser() -> argparse.ArgumentParser:
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
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Read metadata from audio file(s)')
    read_parser.add_argument('files', nargs='+', help='Audio file(s) or pattern(s)')
    read_parser.add_argument('--format', choices=['json', 'yaml', 'table'], 
                           default='json', dest='output_format',
                           help='Output format (default: json)')
    read_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    read_parser.add_argument('--no-headers', action='store_true',
                           help='Exclude header information')
    read_parser.add_argument('--no-technical', action='store_true',
                           help='Exclude technical information')
    read_parser.add_argument('--recursive', '-r', action='store_true',
                           help='Process directories recursively')
    read_parser.add_argument('--continue-on-error', action='store_true',
                           help='Continue processing other files on error')
    read_parser.set_defaults(func=read_metadata)
    
    # Unified command
    unified_parser = subparsers.add_parser('unified', help='Read unified metadata only')
    unified_parser.add_argument('files', nargs='+', help='Audio file(s) or pattern(s)')
    unified_parser.add_argument('--format', choices=['json', 'yaml', 'table'], 
                              default='json', dest='output_format',
                              help='Output format (default: json)')
    unified_parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    unified_parser.add_argument('--recursive', '-r', action='store_true',
                              help='Process directories recursively')
    unified_parser.add_argument('--continue-on-error', action='store_true',
                              help='Continue processing other files on error')
    unified_parser.set_defaults(func=read_metadata, format_type='unified')
    
    # Write command
    write_parser = subparsers.add_parser('write', help='Write metadata to audio file(s)')
    write_parser.add_argument('files', nargs='+', help='Audio file(s) or pattern(s)')
    write_parser.add_argument('--title', help='Song title')
    write_parser.add_argument('--artist', help='Artist name')
    write_parser.add_argument('--album', help='Album name')
    write_parser.add_argument('--year', type=int, help='Release year')
    write_parser.add_argument('--genre', help='Genre')
    write_parser.add_argument('--rating', type=int, help='Rating (0-100)')
    write_parser.add_argument('--comment', help='Comment')
    write_parser.add_argument('--recursive', '-r', action='store_true',
                            help='Process directories recursively')
    write_parser.add_argument('--continue-on-error', action='store_true',
                            help='Continue processing other files on error')
    write_parser.set_defaults(func=write_metadata)
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete all metadata from audio file(s)')
    delete_parser.add_argument('files', nargs='+', help='Audio file(s) or pattern(s)')
    delete_parser.add_argument('--recursive', '-r', action='store_true',
                             help='Process directories recursively')
    delete_parser.add_argument('--continue-on-error', action='store_true',
                             help='Continue processing other files on error')
    delete_parser.set_defaults(func=delete_metadata)
    
    return parser


def main() -> None:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

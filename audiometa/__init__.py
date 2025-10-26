"""Audio metadata handling module.

A comprehensive Python library for reading and writing audio metadata across multiple formats
including MP3, FLAC, WAV, and more. Supports ID3v1, ID3v2, Vorbis (FLAC), and RIFF (WAV) formats
with 50+ metadata fields including title, artist, album, rating, BPM, and more.

Note: OGG file support is planned but not yet implemented.

For detailed metadata support information, see the README.md file.
"""

import warnings
from mutagen.id3 import ID3

from .audio_file import AudioFile
from .exceptions import FileTypeNotSupportedError, MetadataFieldNotSupportedByMetadataFormatError, MetadataWritingConflictParametersError, InvalidMetadataFieldTypeError, MetadataFieldNotSupportedByLib, MetadataFormatNotSupportedByAudioFormatError, FileCorruptedError
from .utils.types import UnifiedMetadata, AppMetadataValue
from .utils.MetadataFormat import MetadataFormat
from .utils.MetadataWritingStrategy import MetadataWritingStrategy
from .utils.UnifiedMetadataKey import UnifiedMetadataKey
from .manager.id3v1.Id3v1Manager import Id3v1Manager
from .manager.MetadataManager import MetadataManager
from .manager.rating_supporting.RatingSupportingMetadataManager import RatingSupportingMetadataManager
from .manager.rating_supporting.Id3v2Manager import Id3v2Manager
from .manager.rating_supporting.RiffManager import RiffManager
from .manager.rating_supporting.VorbisManager import VorbisManager


FILE_EXTENSION_NOT_HANDLED_MESSAGE = "The file's format is not handled by the service."

METADATA_FORMAT_MANAGER_CLASS_MAP = {
    MetadataFormat.ID3V1: Id3v1Manager,
    MetadataFormat.ID3V2: Id3v2Manager,
    MetadataFormat.VORBIS: VorbisManager,
    MetadataFormat.RIFF: RiffManager
}

FILE_TYPE = AudioFile | str


def _get_metadata_manager(
        file: FILE_TYPE, metadata_format: MetadataFormat | None = None, normalized_rating_max_value: int | None = None, id3v2_version: tuple[int, int, int] | None = None
) -> MetadataManager:
    if not isinstance(file, AudioFile):
        file = AudioFile(file)

    audio_file_prioritized_tag_formats = MetadataFormat.get_priorities().get(file.file_extension)
    if not audio_file_prioritized_tag_formats:
        raise FileTypeNotSupportedError(FILE_EXTENSION_NOT_HANDLED_MESSAGE)

    if not metadata_format:
        metadata_format = audio_file_prioritized_tag_formats[0]
    else:
        if metadata_format not in audio_file_prioritized_tag_formats:
            raise MetadataFormatNotSupportedByAudioFormatError(
                f"Tag format {metadata_format} not supported for file extension {file.file_extension}")

    manager_class = METADATA_FORMAT_MANAGER_CLASS_MAP[metadata_format]
    if issubclass(manager_class, RatingSupportingMetadataManager):
        if manager_class == Id3v2Manager:
            # Determine ID3v2 version based on provided version or use default
            if id3v2_version is not None:
                version = id3v2_version
            else:
                version = (2, 3, 0)  # Default to ID3v2.3
            return manager_class(
                audio_file=file, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=version)  # type: ignore
        else:
            return manager_class(
                audio_file=file, normalized_rating_max_value=normalized_rating_max_value)  # type: ignore
    return manager_class(audio_file=file)


def _get_metadata_managers(
    file: FILE_TYPE, tag_formats: list[MetadataFormat] | None = None, normalized_rating_max_value: int | None = None, id3v2_version: tuple[int, int, int] | None = None
) -> dict[MetadataFormat, MetadataManager]:
    if not isinstance(file, AudioFile):
        file = AudioFile(file)

    managers = {}

    if not tag_formats:
        tag_formats = MetadataFormat.get_priorities().get(file.file_extension)
        if not tag_formats:
            raise FileTypeNotSupportedError(FILE_EXTENSION_NOT_HANDLED_MESSAGE)

    for metadata_format in tag_formats:
        managers[metadata_format] = _get_metadata_manager(
            file=file, metadata_format=metadata_format, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
    return managers


def get_unified_metadata(
        file: FILE_TYPE, normalized_rating_max_value: int | None = None, id3v2_version: tuple[int, int, int] | None = None, metadata_format: MetadataFormat | None = None) -> UnifiedMetadata:
    """
    Get metadata from a file, either unified across all formats or from a specific format only.
    
    When metadata_format is None (default), this function reads metadata from all available 
    formats (ID3v1, ID3v2, Vorbis, RIFF) and returns a unified dictionary with the best 
    available data for each field.
    
    When metadata_format is specified, this function reads metadata from only the specified 
    format, returning data from that format only.
    
    Args:
        file: Audio file path or AudioFile object
        normalized_rating_max_value: Maximum value for rating normalization (0-10 scale).
            When provided, ratings are normalized to this scale. Defaults to None (raw values).
        id3v2_version: ID3v2 version tuple for ID3v2-specific operations
        metadata_format: Specific metadata format to read from. If None, reads from all available formats.
        
    Returns:
        Dictionary containing metadata fields
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        # Get all metadata with raw rating values (unified)
        metadata = get_unified_metadata("song.mp3")
        print(metadata.get(UnifiedMetadataKey.TITLE))
        
        # Get all metadata with normalized ratings (unified)
        metadata = get_unified_metadata("song.mp3", normalized_rating_max_value=100)
        print(metadata.get(UnifiedMetadataKey.RATING))  # Returns 0-100
        
        # Get metadata from FLAC file (unified)
        metadata = get_unified_metadata("song.flac")
        print(metadata.get(UnifiedMetadataKey.ARTISTS))
        
        # Get only ID3v2 metadata
        metadata = get_unified_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2)
        print(metadata.get(UnifiedMetadataKey.TITLE))
        
        # Get only Vorbis metadata from FLAC
        metadata = get_unified_metadata("song.flac", metadata_format=MetadataFormat.VORBIS)
        print(metadata.get(UnifiedMetadataKey.ARTISTS))
        
        # Get ID3v2 metadata with normalized ratings
        metadata = get_unified_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100)
        print(metadata.get(UnifiedMetadataKey.RATING))  # Returns 0-100
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)

    # If specific format requested, return data from that format only
    if metadata_format is not None:
        manager = _get_metadata_manager(
            file=file, metadata_format=metadata_format, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
        return manager.get_unified_metadata()

    # Get all available managers for this file type
    all_managers = _get_metadata_managers(file=file, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
    
    # Get file-specific format priorities
    available_formats = MetadataFormat.get_priorities().get(file.file_extension, [])
    managers_by_precedence = []
    
    for format_type in available_formats:
        if format_type in all_managers:
            managers_by_precedence.append((format_type, all_managers[format_type]))

    result = {}
    for unified_metadata_key in UnifiedMetadataKey:
        for format_type, manager in managers_by_precedence:
            try:
                unified_metadata = manager.get_unified_metadata()
                if unified_metadata_key in unified_metadata:
                    value = unified_metadata[unified_metadata_key]
                    if value is not None:
                        result[unified_metadata_key] = value
                        break
            except Exception:
                # If this manager fails, continue to the next one
                continue
    return result


def get_unified_metadata_field(file: FILE_TYPE, unified_metadata_key: UnifiedMetadataKey, normalized_rating_max_value: int | None = None, id3v2_version: tuple[int, int, int] | None = None, metadata_format: MetadataFormat | None = None) -> AppMetadataValue:
    """
    Get a specific unified metadata field from an audio file.
    
    Args:
        file: Audio file path or AudioFile object
        unified_metadata_key: The metadata field to retrieve
        normalized_rating_max_value: Maximum value for rating normalization (0-10 scale).
            Only used when unified_metadata_key is RATING. For other metadata fields,
            this parameter is ignored. Defaults to None (no normalization).
        id3v2_version: ID3v2 version tuple for ID3v2-specific operations
        metadata_format: Specific metadata format to read from. If None, uses priority order.
        
    Returns:
        The metadata value or None if not found
        
    Raises:
        MetadataFieldNotSupportedByMetadataFormatError: When metadata_format is specified and the field 
            is not supported by that format
        MetadataFieldNotSupportedByLib: When the field is not supported by any format in the library
            (only when metadata_format is None and all formats raise MetadataFieldNotSupportedByMetadataFormatError)
        
    Examples:
        # Get title from any format (priority order)
        title = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.TITLE)
        
        # Get title specifically from ID3v2
        title = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V2)
        
        # Get rating without normalization
        rating = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.RATING)
        
        # Get rating with 0-100 normalization
        rating = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.RATING, normalized_rating_max_value=100)
        
        # Handle format-specific errors
        try:
            bpm = get_unified_metadata_field("song.wav", UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.RIFF)
        except MetadataFieldNotSupportedByMetadataFormatError:
            print("BPM not supported by RIFF format")
        
        # Handle library-wide errors
        try:
            value = get_unified_metadata_field("song.mp3", UnifiedMetadataKey.SOME_FIELD)
        except MetadataFieldNotSupportedByLib:
            print("Field not supported by any format in the library")
    """
    # Check if key is a valid UnifiedMetadataKey enum first
    if not isinstance(unified_metadata_key, UnifiedMetadataKey):
        raise MetadataFieldNotSupportedByLib(f"{unified_metadata_key} metadata not supported by the library.")
    
    if not isinstance(file, AudioFile):
        file = AudioFile(file)

    if metadata_format is not None:
        # Get metadata from specific format
        manager = _get_metadata_manager(file=file, metadata_format=metadata_format, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
        try:
            return manager.get_unified_metadata_field(unified_metadata_key=unified_metadata_key)
        except MetadataFieldNotSupportedByMetadataFormatError:
            # Re-raise format-specific errors to let the user know the field is not supported
            raise
        except Exception:
            return None
    else:
        # Use priority order across all formats
        managers_prioritized = _get_metadata_managers(file=file, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
        
        # Try each manager in priority order until we find a value
        format_errors = []
        for format_type, manager in managers_prioritized.items():
            try:
                value = manager.get_unified_metadata_field(unified_metadata_key=unified_metadata_key)
                if value is not None:
                    return value
            except MetadataFieldNotSupportedByMetadataFormatError as e:
                # Track format-specific errors to determine if field is supported by library at all
                format_errors.append((format_type, e))
            except Exception:
                # If this manager fails for other reasons, try the next one
                continue
        
        # If ALL managers raised MetadataFieldNotSupportedByMetadataFormatError, 
        # the field is not supported by the library at all
        if len(format_errors) == len(managers_prioritized) and len(format_errors) > 0:
            raise MetadataFieldNotSupportedByLib(f'{unified_metadata_key} metadata field is not supported by any format in the library')
        
        return None


def _validate_unified_metadata_types(unified_metadata: UnifiedMetadata) -> None:
    """Validate types of values in unified_metadata against UnifiedMetadataKey.get_optional_type().

    Raises InvalidMetadataFieldTypeError when a value does not match the expected type.
    None values are allowed (used to indicate removal of a field).
    """
    if not unified_metadata:
        return

    from typing import get_origin, get_args, Union

    for key, value in unified_metadata.items():
        # Check if key is a valid UnifiedMetadataKey enum first
        if not isinstance(key, UnifiedMetadataKey):
            raise MetadataFieldNotSupportedByLib(f"{key} metadata not supported by the library.")
        
        # Allow None to mean "remove this field"
        if value is None:
            continue

        try:
            expected_type = key.get_optional_type()
        except Exception:
            raise TypeError(f'Cannot determine expected type for key: {key.value}')

        origin = get_origin(expected_type)
        if origin == list:
            # Expect a list of a particular type (e.g., list[str]). Do NOT allow
            # single values of the inner type; callers must provide a list.
            arg_types = get_args(expected_type)
            item_type = arg_types[0] if arg_types else str
            # Value must be a list and all items must be of the expected inner type
            if not isinstance(value, list):
                raise InvalidMetadataFieldTypeError(key.value, f'list[{getattr(item_type, "__name__", str(item_type))}]', value)
            if not all(isinstance(item, item_type) for item in value):
                raise InvalidMetadataFieldTypeError(key.value, f'list[{getattr(item_type, "__name__", str(item_type))}]', value)
        elif origin == Union:
            # Handle Union types (e.g., Union[int, str])
            arg_types = get_args(expected_type)
            if not isinstance(value, arg_types):
                raise InvalidMetadataFieldTypeError(key.value, f'Union[{", ".join(getattr(t, "__name__", str(t)) for t in arg_types)}]', value)
        else:
            # expected_type is a plain type like str or int
            if not isinstance(value, expected_type):
                # Special case for TRACK_NUMBER: allow str in addition to int
                if key == UnifiedMetadataKey.TRACK_NUMBER and isinstance(value, str):
                    continue
                raise InvalidMetadataFieldTypeError(key.value, getattr(expected_type, '__name__', str(expected_type)), value)


def update_metadata(
        file: FILE_TYPE, unified_metadata: UnifiedMetadata, normalized_rating_max_value: int | None = None, 
        id3v2_version: tuple[int, int, int] | None = None, metadata_strategy: MetadataWritingStrategy | None = None,
        metadata_format: MetadataFormat | None = None, fail_on_unsupported_field: bool = False) -> None:
    """
    Update metadata in an audio file.
    
    This function writes metadata to the specified audio file using the appropriate
    format manager. It supports multiple writing strategies and format selection.
    
    Args:
        file: Audio file path or AudioFile object
        unified_metadata: Dictionary containing metadata to write
        normalized_rating_max_value: Maximum value for rating normalization (0-10 scale).
            When provided, ratings are normalized to this scale. Defaults to None (raw values).
        id3v2_version: ID3v2 version tuple for ID3v2-specific operations
        metadata_strategy: Writing strategy (SYNC, PRESERVE, CLEANUP). Defaults to SYNC.
            Ignored when metadata_format is specified.
        metadata_format: Specific format to write to. If None, uses the file's native format.
            When specified, strategy is ignored and metadata is written only to this format.
        fail_on_unsupported_field: If True, fails when any metadata field is not supported by the target format.
            Applies to all strategies (SYNC, PRESERVE, CLEANUP). Defaults to False (graceful handling with warnings).
        
    Returns:
        None
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        MetadataFieldNotSupportedByMetadataFormatError: If the metadata field is not supported by the format (only for PRESERVE, CLEANUP strategies)
        MetadataWritingConflictParametersError: If both metadata_strategy and metadata_format are specified
        InvalidRatingValueError: If invalid rating values are provided
        
    Note:
        Cannot specify both metadata_strategy and metadata_format simultaneously. Choose one approach:
        
        - Use metadata_strategy for multi-format management (SYNC, PRESERVE, CLEANUP)
        - Use metadata_format for single-format writing (writes only to specified format)
        
        When metadata_format is specified, metadata is written only to that format and unsupported
        fields will raise MetadataFieldNotSupportedByMetadataFormatError.
        
        When metadata_strategy is used, unsupported metadata fields are handled based on the
        fail_on_unsupported_field parameter: True raises MetadataFieldNotSupportedByMetadataFormatError, False (default)
        handles gracefully with warnings.
        
        Data Filtering:
        For list-type metadata fields (e.g., ARTISTS, GENRES), empty strings and None values
        are automatically filtered out before writing. If all values in a list are filtered out,
        the field is removed entirely (set to None). This ensures clean metadata without empty
        or invalid entries across all supported formats.
        
    Examples:
        # Basic metadata update
        metadata = {
            UnifiedMetadataKey.TITLE: "New Title",
            UnifiedMetadataKey.ARTISTS: ["Artist Name"]
        }
        update_metadata("song.mp3", metadata)
        
        # Update with rating normalization
        metadata = {
            UnifiedMetadataKey.TITLE: "New Title",
            UnifiedMetadataKey.RATING: 75  # Will be normalized to 0-100 scale
        }
        update_metadata("song.mp3", metadata, normalized_rating_max_value=100)
        
        # Clean up other formats (remove ID3v1, keep only ID3v2)
        update_metadata("song.mp3", metadata, metadata_strategy=MetadataWritingStrategy.CLEANUP)
        
        # Write to specific format
        update_metadata("song.mp3", metadata, metadata_format=MetadataFormat.ID3V2)
        
        # Remove specific fields by setting them to None
        update_metadata("song.mp3", {
            UnifiedMetadataKey.TITLE: None,        # Removes title field
            UnifiedMetadataKey.ARTISTS: None # Removes artist field
        })
        
        # Automatic filtering of empty values
        metadata = {
            UnifiedMetadataKey.ARTISTS: ["", "Artist 1", "   ", "Artist 2", None]
        }
        # Results in: ["Artist 1", "Artist 2"] - empty strings and None filtered out
        update_metadata("song.mp3", metadata)
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    
    # Validate that both parameters are not specified simultaneously
    if metadata_strategy is not None and metadata_format is not None:
        raise MetadataWritingConflictParametersError(
            "Cannot specify both metadata_strategy and metadata_format. "
            "When metadata_format is specified, strategy is not applicable. "
            "Choose either: use metadata_strategy for multi-format management, "
            "or metadata_format for single-format writing."
        )
    
    # Default to SYNC strategy if not specified
    if metadata_strategy is None:
        metadata_strategy = MetadataWritingStrategy.SYNC
    
    # Handle strategy-specific behavior before writing
    # Validate provided unified_metadata value types before attempting any writes
    _validate_unified_metadata_types(unified_metadata)

    _handle_metadata_strategy(file, unified_metadata, metadata_strategy, normalized_rating_max_value, id3v2_version, metadata_format, fail_on_unsupported_field)


def _handle_metadata_strategy(file: AudioFile, unified_metadata: UnifiedMetadata, strategy: MetadataWritingStrategy, 
                             normalized_rating_max_value: int | None, id3v2_version: tuple[int, int, int] | None,
                             target_format: MetadataFormat | None = None, fail_on_unsupported_field: bool = False) -> None:
    """Handle metadata strategy-specific behavior for all strategies."""
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    
    # Get the target format (specified format or native format)
    if target_format:
        target_format_actual = target_format
    else:
        target_format_actual = MetadataFormat.get_priorities().get(file.file_extension)[0]
    
    # When a specific format is forced, ignore strategy and write only to that format
    if target_format:
        all_managers = _get_metadata_managers(
            file=file, tag_formats=[target_format_actual], normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
        target_manager = all_managers[target_format_actual]
        target_manager.update_metadata(unified_metadata)
        return
    
    # Get all available managers for this file type
    all_managers = _get_metadata_managers(
        file=file, normalized_rating_max_value=normalized_rating_max_value, id3v2_version=id3v2_version)
    
    # Get other formats (non-target)
    other_managers = {fmt: mgr for fmt, mgr in all_managers.items() if fmt != target_format_actual}
    
    if strategy == MetadataWritingStrategy.CLEANUP:
        # First, clean up non-target formats
        for fmt, manager in other_managers.items():
            try:
                manager.delete_metadata()
            except Exception:
                # Some managers might not support deletion or might fail
                pass
        
        # Check for unsupported fields by target format
        target_manager = all_managers[target_format_actual]
        unsupported_fields = []
        for field in unified_metadata.keys():
            if hasattr(target_manager, 'metadata_keys_direct_map_write') and target_manager.metadata_keys_direct_map_write:
                if field not in target_manager.metadata_keys_direct_map_write:
                    unsupported_fields.append(field)
        
        if unsupported_fields:
            if fail_on_unsupported_field:
                raise MetadataFieldNotSupportedByMetadataFormatError(f"Fields not supported by {target_format_actual.value} format: {unsupported_fields}")
            else:
                warnings.warn(f"Fields not supported by {target_format_actual.value} format will be skipped: {unsupported_fields}")
                # Create filtered metadata without unsupported fields
                filtered_metadata = {k: v for k, v in unified_metadata.items() if k not in unsupported_fields}
                unified_metadata = filtered_metadata
        
        # Then write to target format
        target_manager.update_metadata(unified_metadata)
        
    elif strategy == MetadataWritingStrategy.SYNC:
        # For SYNC, we need to write to all available formats
        # Check if any fields are unsupported by the target format when fail_on_unsupported_field is True
        if fail_on_unsupported_field:
            target_manager = all_managers[target_format_actual]
            unsupported_fields = []
            for field in unified_metadata.keys():
                if field not in target_manager.metadata_keys_direct_map_write:
                    unsupported_fields.append(field)
            if unsupported_fields:
                raise MetadataFieldNotSupportedByMetadataFormatError(f"Fields not supported by {target_format_actual.value} format: {unsupported_fields}")
        else:
            # Filter out unsupported fields when fail_on_unsupported_field is False
            target_manager = all_managers[target_format_actual]
            unsupported_fields = []
            for field in unified_metadata.keys():
                if field not in target_manager.metadata_keys_direct_map_write:
                    unsupported_fields.append(field)
            if unsupported_fields:
                warnings.warn(f"Fields not supported by {target_format_actual.value} format will be skipped: {unsupported_fields}")
                # Create filtered metadata without unsupported fields
                filtered_metadata = {k: v for k, v in unified_metadata.items() if k not in unsupported_fields}
                unified_metadata = filtered_metadata
        
        # Write to target format first
        target_manager = all_managers[target_format_actual]
        try:
            target_manager.update_metadata(unified_metadata)
        except MetadataFieldNotSupportedByMetadataFormatError as e:
            # For SYNC strategy, log warning but continue with other formats
            warnings.warn(f"Format {target_format_actual} doesn't support some metadata fields: {e}")
        except Exception as e:
            # Re-raise user errors (like InvalidRatingValueError) immediately
            from .exceptions import InvalidRatingValueError, ConfigurationError
            if isinstance(e, (InvalidRatingValueError, ConfigurationError)):
                raise
            # Some managers might not support writing or might fail for other reasons
            pass
        
        # Then sync all other available formats
        # Note: We need to be careful about the order to avoid conflicts
        for fmt, manager in other_managers.items():
            try:
                manager.update_metadata(unified_metadata)
            except MetadataFieldNotSupportedByMetadataFormatError as e:
                # For SYNC strategy, log warning but continue with other formats
                warnings.warn(f"Format {fmt} doesn't support some metadata fields: {e}")
                continue
            except Exception:
                # Some managers might not support writing or might fail for other reasons
                pass
                
    elif strategy == MetadataWritingStrategy.PRESERVE:
        # For PRESERVE, we need to save existing metadata from other formats first
        preserved_metadata = {}
        for fmt, manager in other_managers.items():
            try:
                existing_metadata = manager.get_unified_metadata()
                if existing_metadata:
                    preserved_metadata[fmt] = existing_metadata
            except Exception:
                pass
        
        # Check for unsupported fields by target format
        target_manager = all_managers[target_format_actual]
        unsupported_fields = []
        for field in unified_metadata.keys():
            if hasattr(target_manager, 'metadata_keys_direct_map_write') and target_manager.metadata_keys_direct_map_write:
                if field not in target_manager.metadata_keys_direct_map_write:
                    unsupported_fields.append(field)
        
        if unsupported_fields:
            if fail_on_unsupported_field:
                raise MetadataFieldNotSupportedByMetadataFormatError(f"Fields not supported by {target_format_actual.value} format: {unsupported_fields}")
            else:
                warnings.warn(f"Fields not supported by {target_format_actual.value} format will be skipped: {unsupported_fields}")
                # Create filtered metadata without unsupported fields
                filtered_metadata = {k: v for k, v in unified_metadata.items() if k not in unsupported_fields}
                unified_metadata = filtered_metadata
        
        # Write to target format
        target_manager.update_metadata(unified_metadata)
        
        # Restore preserved metadata from other formats
        for fmt, metadata in preserved_metadata.items():
            try:
                manager = other_managers[fmt]
                manager.update_metadata(metadata)
            except Exception:
                # Some managers might not support writing or might fail for other reasons
                pass


def delete_all_metadata(file, metadata_format: MetadataFormat | None = None, id3v2_version: tuple[int, int, int] | None = None) -> bool:
    """
    Delete all metadata from an audio file, including metadata headers.
    
    This function completely removes all metadata tags and their container structures
    from the specified audio file. This is a destructive operation that removes
    metadata headers entirely, not just the content.
    
    Args:
        file: Audio file path or AudioFile object
        metadata_format: Specific format to delete metadata from. If None, deletes from ALL supported formats.
        id3v2_version: ID3v2 version tuple for ID3v2-specific operations
        
    Returns:
        True if metadata was successfully deleted from at least one format, False otherwise
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        # Delete ALL metadata from ALL supported formats (removes headers completely)
        success = delete_all_metadata("song.mp3")
        
        # Delete only ID3v2 metadata (keep ID3v1, removes ID3v2 headers)
        success = delete_all_metadata("song.mp3", metadata_format=MetadataFormat.ID3V2)
        
        # Delete Vorbis metadata from FLAC (removes Vorbis comment blocks)
        success = delete_all_metadata("song.flac", metadata_format=MetadataFormat.VORBIS)
        
    Note:
        This function removes metadata headers entirely, significantly reducing file size.
        This is different from setting individual fields to None, which only removes
        specific fields while preserving the metadata structure and other fields.
        
        When no metadata_format is specified, the function attempts to delete metadata from
        ALL supported formats for the file type. Some formats may not support deletion
        and will be skipped silently.
        
        Use cases:
        - Complete privacy cleanup (remove all metadata)
        - File size optimization (remove all metadata headers)
        - Format cleanup (remove specific format metadata)
        
        For selective field removal, use update_metadata with None values instead.
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    
    # If specific format requested, delete only that format
    if metadata_format:
        return _get_metadata_manager(file, metadata_format=metadata_format, id3v2_version=id3v2_version).delete_metadata()
    
    # Delete from all supported formats for this file type
    all_managers = _get_metadata_managers(file, normalized_rating_max_value=None, id3v2_version=id3v2_version)
    success_count = 0
    
    for format_type, manager in all_managers.items():
        try:
            if manager.delete_metadata():
                success_count += 1
        except Exception:
            # Some formats may not support deletion (e.g., ID3v1) or may fail
            # Continue with other formats
            pass
    
    # Return True if at least one format was successfully deleted
    return success_count > 0


def get_bitrate(file: FILE_TYPE) -> int:
    """
    Get the bitrate of an audio file.
    
    Args:
        file: Audio file path or AudioFile object
        
    Returns:
        Bitrate in bits per second
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        bitrate = get_bitrate("song.mp3")
        print(f"Bitrate: {bitrate} bps")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    return file.get_bitrate()


def get_channels(file: FILE_TYPE) -> int:
    """
    Get the number of channels in an audio file.
    
    Args:
        file: Audio file path or AudioFile object
        
    Returns:
        Number of audio channels (e.g., 1 for mono, 2 for stereo)
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        channels = get_channels("song.mp3")
        print(f"Channels: {channels}")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    return file.get_channels()


def get_file_size(file: FILE_TYPE) -> int:
    """
    Get the file size of an audio file in bytes.
    
    Args:
        file: Audio file path or AudioFile object
        
    Returns:
        File size in bytes
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        size = get_file_size("song.mp3")
        print(f"File size: {size} bytes")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    return file.get_file_size()


def get_sample_rate(file: FILE_TYPE) -> int:
    """
    Get the sample rate of an audio file in Hz.
    
    Args:
        file: Audio file path or AudioFile object
        
    Returns:
        Sample rate in Hz
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        sample_rate = get_sample_rate("song.mp3")
        print(f"Sample rate: {sample_rate} Hz")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    return file.get_sample_rate()


def get_duration_in_sec(file: FILE_TYPE) -> float:
    """
    Get the duration of an audio file in seconds.
    
    Args:
        file: Audio file path or AudioFile object
        
    Returns:
        Duration in seconds as a float
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        duration = get_duration_in_sec("song.mp3")
        print(f"Duration: {duration:.2f} seconds")
        
        # Convert to minutes
        minutes = duration / 60
        print(f"Duration: {minutes:.2f} minutes")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    return file.get_duration_in_sec()


def is_flac_md5_valid(file: FILE_TYPE) -> bool:
    """
    Check if a FLAC file's MD5 signature is valid.
    
    This function verifies the integrity of a FLAC file by checking its MD5 signature.
    Only works with FLAC files.
    
    Args:
        file: Audio file path or AudioFile object (must be FLAC)
        
    Returns:
        True if MD5 signature is valid, False otherwise
        
    Raises:
        FileTypeNotSupportedError: If the file is not a FLAC file
        FileNotFoundError: If the file does not exist
        
    Examples:
        # Check FLAC file integrity
        is_valid = is_flac_md5_valid("song.flac")
        if is_valid:
            print("FLAC file is intact")
        else:
            print("FLAC file may be corrupted")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    try:
        return file.is_flac_file_md5_valid()
    except FileCorruptedError:
        return False


def fix_md5_checking(file: FILE_TYPE) -> str:
    """
    Returns a temporary file with corrected MD5 signature.

    Args:
        file: The file to fix MD5 for. Can be AudioFile or str path.

    Returns:
        str: Path to a temporary file containing the corrected audio data.

    Raises:
        FileTypeNotSupportedError: If the file is not a FLAC file
        FileCorruptedError: If the FLAC file is corrupted or cannot be corrected
        RuntimeError: If the FLAC command fails to execute
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)
    return file.get_file_with_corrected_md5(delete_original=True)


def get_full_metadata(file: FILE_TYPE, include_headers: bool = True, include_technical: bool = True) -> dict:
    """
    Get comprehensive metadata including all available information from a file, including headers and technical details even when no metadata is present.
    
    This function provides the most complete view of an audio file by combining:
    - All metadata from all supported formats (ID3v1, ID3v2, Vorbis, RIFF)
    - Technical information (duration, bitrate, sample rate, channels, file size)
    - Format-specific headers and structure information
    - Raw metadata details from each format
    
    Args:
        file: Audio file path or AudioFile object
        include_headers: Whether to include format-specific header information (default: True)
        include_technical: Whether to include technical audio information (default: True)
        
    Returns:
        Comprehensive dictionary containing all available metadata and technical information
        
    Raises:
        FileTypeNotSupportedError: If the file format is not supported
        FileNotFoundError: If the file does not exist
        
    Examples:
        # Get complete metadata including headers and technical info
        full_metadata = get_full_metadata("song.mp3")
        
        # Access unified metadata (same as get_unified_metadata)
        print(f"Title: {full_metadata['unified_metadata']['title']}")
        
        # Access technical information
        print(f"Duration: {full_metadata['technical_info']['duration_seconds']} seconds")
        print(f"Bitrate: {full_metadata['technical_info']['bitrate_kbps']} kbps")
        
        # Access format-specific metadata
        print(f"ID3v2 Title: {full_metadata['format_metadata']['id3v2']['title']}")
        
        # Access header information
        print(f"ID3v2 Version: {full_metadata['headers']['id3v2']['version']}")
        print(f"Has ID3v1 Header: {full_metadata['headers']['id3v1']['present']}")
    """
    if not isinstance(file, AudioFile):
        file = AudioFile(file)

    # Get all available managers for this file type
    all_managers = _get_metadata_managers(file=file, normalized_rating_max_value=None, id3v2_version=None)
    
    # Get file-specific format priorities
    available_formats = MetadataFormat.get_priorities().get(file.file_extension, [])
    
    # Initialize result structure
    result = {
        'unified_metadata': {},
        'technical_info': {},
        'format_metadata': {},
        'headers': {},
        'raw_metadata': {},
        'format_priorities': {
            'file_extension': file.file_extension,
            'reading_order': [fmt.value for fmt in available_formats],
            'writing_format': available_formats[0].value if available_formats else None
        }
    }
    
    # Get unified metadata (same as get_unified_metadata)
    result['unified_metadata'] = get_unified_metadata(file)
    
    # Get technical information
    if include_technical:
        try:
            result['technical_info'] = {
                'duration_seconds': file.get_duration_in_sec(),
                'bitrate_kbps': file.get_bitrate(),
                'sample_rate_hz': file.get_sample_rate(),
                'channels': file.get_channels(),
                'file_size_bytes': get_file_size(file),
                'file_extension': file.file_extension,
                'format_name': file.get_format_name(),
                'is_flac_md5_valid': file.is_flac_file_md5_valid() if file.file_extension == '.flac' else None
            }
        except Exception:
            result['technical_info'] = {
                'duration_seconds': 0,
                'bitrate_kbps': 0,
                'sample_rate_hz': 0,
                'channels': 0,
                'file_size_bytes': 0,
                'file_extension': file.file_extension,
                'format_name': file.get_format_name(),
                'is_flac_md5_valid': None
            }
    
    # Get format-specific metadata and headers
    for format_type in available_formats:
        format_key = format_type.value
        manager = all_managers.get(format_type)
        
        if manager:
            # Get format-specific metadata
            try:
                format_metadata = manager.get_unified_metadata()
                result['format_metadata'][format_key] = format_metadata
            except Exception:
                result['format_metadata'][format_key] = {}
            
            # Get header information
            if include_headers:
                try:
                    header_info = manager.get_header_info()
                    result['headers'][format_key] = header_info
                except Exception:
                    result['headers'][format_key] = {
                        'present': False,
                        'version': None,
                        'size_bytes': 0,
                        'position': None,
                        'flags': {},
                        'extended_header': {}
                    }
                
                # Get raw metadata information
                try:
                    raw_info = manager.get_raw_metadata_info()
                    result['raw_metadata'][format_key] = raw_info
                except Exception:
                    result['raw_metadata'][format_key] = {
                        'raw_data': None,
                        'parsed_fields': {},
                        'frames': {},
                        'comments': {},
                        'chunk_structure': {}
                    }
        else:
            # Format not available for this file type
            result['format_metadata'][format_key] = {}
            if include_headers:
                result['headers'][format_key] = {
                    'present': False,
                    'version': None,
                    'size_bytes': 0,
                    'position': None,
                    'flags': {},
                    'extended_header': {}
                }
                result['raw_metadata'][format_key] = {
                    'raw_data': None,
                    'parsed_fields': {},
                    'frames': {},
                    'comments': {},
                    'chunk_structure': {}
                }
    
    return result


def delete_potential_id3_metadata_with_header(file: FILE_TYPE) -> None:
    """
    Delete ID3 metadata headers from an audio file.
    
    This function attempts to remove ID3 metadata headers from the file.
    It's a low-level operation that directly manipulates the file structure.
    
    Args:
        file: Audio file path or AudioFile object
        
    Returns:
        None
        
    Raises:
        FileNotFoundError: If the file does not exist
        
    Examples:
        # Remove ID3 headers from MP3 file
        delete_potential_id3_metadata_with_header("song.mp3")
        
        # This is typically used for cleanup operations
        # when you want to remove all ID3 metadata
    """
    if not isinstance(file, AudioFile):
        audio_file = AudioFile(file)
    try:
        id_metadata = ID3(audio_file.get_file_path_or_object())
        id_metadata.delete()
    except Exception:
        pass

import re
from abc import abstractmethod
from typing import TYPE_CHECKING, TypeVar, Union, cast

from mutagen._file import FileType as MutagenMetadata

from audiometa.exceptions import InvalidMetadataFieldFormatError
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

if TYPE_CHECKING:
    from .._audio_file import _AudioFile
from ..exceptions import MetadataFieldNotSupportedByMetadataFormatError
from ..utils.id3v1_genre_code_map import ID3V1_GENRE_CODE_MAP
from ..utils.types import RawMetadataDict, RawMetadataKey, UnifiedMetadata, UnifiedMetadataValue

# Separators in order of priority for multi-value metadata fields
# Note: null bytes (\x00) are only used in ID3v2.4, not included in generic priority list
METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED = ("//", "\\\\", "\\", ";", "/", ",")


T = TypeVar("T", str, int)


class _MetadataManager:
    audio_file: "_AudioFile"
    metadata_keys_direct_map_read: dict[UnifiedMetadataKey, RawMetadataKey | None]
    metadata_keys_direct_map_write: dict[UnifiedMetadataKey, RawMetadataKey | None] | None
    raw_mutagen_metadata: MutagenMetadata | None = None
    raw_clean_metadata: RawMetadataDict | None = None
    raw_clean_metadata_uppercase_keys: RawMetadataDict | None = None
    update_using_mutagen_metadata: bool

    def __init__(
        self,
        audio_file: "_AudioFile",
        metadata_keys_direct_map_read: dict[UnifiedMetadataKey, RawMetadataKey | None],
        metadata_keys_direct_map_write: dict[UnifiedMetadataKey, RawMetadataKey | None] | None = None,
        update_using_mutagen_metadata: bool = True,
    ):
        self.audio_file = audio_file
        self.metadata_keys_direct_map_read = metadata_keys_direct_map_read
        self.metadata_keys_direct_map_write = metadata_keys_direct_map_write
        self.update_using_mutagen_metadata = update_using_mutagen_metadata

    @abstractmethod
    def _get_formatted_metadata_format_name(self) -> str:
        """Get the formatted metadata format name.

        Returns:
            The formatted format name (e.g., 'RIFF', 'ID3v2', 'Vorbis')
        """
        raise NotImplementedError

    @staticmethod
    def find_safe_separator(values: list[str]) -> str:
        """Find a separator that doesn't appear in any of the provided values.

        Args:
            values: List of string values to check for separator conflicts

        Returns:
            A separator string that doesn't appear in any value, or the last
            separator (comma) as fallback if no separator is safe
        """
        # Find a separator that doesn't appear in any of the values
        for sep in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED:
            if not any(sep in value for value in values):
                return sep

        # If no separator is safe, use the last one (comma)
        return METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED[-1]

    @staticmethod
    def _filter_valid_values(values: list[str | None]) -> list[str]:
        """Filter out None and empty values from a list of strings.

        This is a generic function used by all metadata managers to ensure
        consistent filtering of empty strings and whitespace.

        Args:
            values: List of string or None values to filter

        Returns:
            List of valid (non-empty) values
        """
        return [value for value in values if value is not None and value != ""]

    @staticmethod
    def validate_release_date(release_date: str) -> None:
        """Validate release date format.

        Release dates must be in one of the following formats:
        - YYYY (4 digits) - for year-only dates (e.g., "2024")
        - YYYY-MM-DD (ISO-like format) - for full dates (e.g., "2024-01-01")
        - Empty string is allowed (represents no date)

        Args:
            release_date: The release date string to validate

        Raises:
            InvalidMetadataFieldFormatError: If the release date format is invalid

        Examples:
            >>> _MetadataManager.validate_release_date("2024")  # Valid
            >>> _MetadataManager.validate_release_date("2024-01-01")  # Valid
            >>> _MetadataManager.validate_release_date("")  # Valid (empty string)
            >>> _MetadataManager.validate_release_date("2024/01/01")  # Raises InvalidMetadataFieldFormatError
        """
        if release_date and not (re.match(r"^\d{4}$", release_date) or re.match(r"^\d{4}-\d{2}-\d{2}$", release_date)):
            raise InvalidMetadataFieldFormatError(
                UnifiedMetadataKey.RELEASE_DATE.value, "YYYY (4 digits) or YYYY-MM-DD format", release_date
            )

    @staticmethod
    def validate_track_number(track_number: str | int) -> None:
        """Validate track number format.

        Track numbers must be in one of the following formats:
        - Simple number: "5", "12", "99" (string or int)
        - Number with separator and optional total: "5/12", "5-12", "5/", "5-"
        - Empty string is allowed (represents no track number)

        Args:
            track_number: The track number to validate (string or int)

        Raises:
            InvalidMetadataFieldFormatError: If the track number format is invalid

        Examples:
            >>> _MetadataManager.validate_track_number("5")  # Valid
            >>> _MetadataManager.validate_track_number(5)  # Valid
            >>> _MetadataManager.validate_track_number("5/12")  # Valid
            >>> _MetadataManager.validate_track_number("5-12")  # Valid
            >>> _MetadataManager.validate_track_number("")  # Valid (empty string)
            >>> _MetadataManager.validate_track_number("/12")  # Raises InvalidMetadataFieldFormatError
            >>> _MetadataManager.validate_track_number("5/12/15")  # Raises InvalidMetadataFieldFormatError
            >>> _MetadataManager.validate_track_number("abc")  # Raises InvalidMetadataFieldFormatError
        """
        if isinstance(track_number, int):
            if track_number < 0:
                raise InvalidMetadataFieldFormatError(
                    UnifiedMetadataKey.TRACK_NUMBER.value, "non-negative integer or string format", str(track_number)
                )
            return

        if not isinstance(track_number, str):
            raise InvalidMetadataFieldFormatError(
                UnifiedMetadataKey.TRACK_NUMBER.value, "string or int", str(type(track_number).__name__)
            )

        if not track_number:
            return

        if not re.match(r"^\d+([-/]\d*)?$", track_number):
            raise InvalidMetadataFieldFormatError(
                UnifiedMetadataKey.TRACK_NUMBER.value,
                "simple number (e.g., '5') or number with separator and optional total (e.g., '5/12', '5-12')",
                track_number,
            )

    @abstractmethod
    def _extract_mutagen_metadata(self) -> MutagenMetadata:
        raise NotImplementedError

    @abstractmethod
    def _convert_raw_mutagen_metadata_to_dict_with_potential_duplicate_keys(
        self, raw_mutagen_metadata: MutagenMetadata
    ) -> RawMetadataDict:
        raise NotImplementedError

    @abstractmethod
    def _get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
        self, raw_clean_metadata_uppercase_keys: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> UnifiedMetadataValue:
        raise NotImplementedError

    @abstractmethod
    def _update_undirectly_mapped_metadata(
        self,
        raw_mutagen_metadata: MutagenMetadata,
        app_metadata_value: UnifiedMetadataValue,
        unified_metadata_key: UnifiedMetadataKey,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def _update_formatted_value_in_raw_mutagen_metadata(
        self,
        raw_mutagen_metadata: MutagenMetadata,
        raw_metadata_key: RawMetadataKey,
        app_metadata_value: UnifiedMetadataValue,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def _update_not_using_mutagen_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        raise NotImplementedError

    def _extract_cleaned_raw_metadata_from_file(self) -> RawMetadataDict:
        self.raw_mutagen_metadata = self._extract_mutagen_metadata()
        raw_metadata_with_potential_duplicate_keys = (
            self._convert_raw_mutagen_metadata_to_dict_with_potential_duplicate_keys(self.raw_mutagen_metadata)
        )
        return self._extract_and_regroup_raw_metadata_unique_entries(raw_metadata_with_potential_duplicate_keys)

    def _extract_raw_clean_metadata_uppercase_keys_from_file(self) -> None:
        if self.raw_clean_metadata is None:
            self.raw_clean_metadata = self._extract_cleaned_raw_metadata_from_file()

        # raw_clean_metadata is RawMetadataDict, so all keys are RawMetadataKey enum members
        # Note: VorbisManager overrides this method to handle case-insensitive key merging
        # since Vorbis comments preserve original key case as strings
        self.raw_clean_metadata_uppercase_keys = dict(self.raw_clean_metadata)

    def _should_apply_smart_parsing(self, values_list_str: list[str]) -> bool:
        """Determine if smart parsing should be applied based on entry count and null separators.

        Args:
            values_list_str: List of string values from the metadata

        Returns:
            True if parsing should be applied, False otherwise
        """
        if not values_list_str:
            return False

        # Count non-empty entries
        non_empty_entries = [val.strip() for val in values_list_str if val.strip()]

        if len(non_empty_entries) == 0:
            return False

        # Check if any entry contains null separators
        has_null_separators = any("\x00" in entry for entry in non_empty_entries)

        # If null separators are present, always apply parsing (null separation logic)
        if has_null_separators:
            return True

        # If we have multiple entries without null separators, don't parse (preserve separators)
        # If we have a single entry without null separators, parse it (legacy data detection)
        return len(non_empty_entries) <= 1

    def _apply_smart_parsing(self, values_list_str: list[str]) -> list[str]:
        """Apply smart parsing to split values.

        Args:
            values_list_str: List of string values to parse

        Returns:
            List of parsed values
        """
        if not values_list_str:
            return []

        # Get non-empty values
        non_empty_values = [val.strip() for val in values_list_str if val.strip()]
        if not non_empty_values:
            return []

        # Check if any entry contains null separators
        has_null_separators = any("\x00" in entry for entry in non_empty_values)

        if has_null_separators:
            # Apply null separation logic across all entries
            result = []
            for entry in non_empty_values:
                if "\x00" in entry:
                    # Split on null separator and add non-empty parts
                    parts = [p.strip() for p in entry.split("\x00") if p.strip()]
                    result.extend(parts)
                else:
                    # Entry without null separator, add as-is
                    result.append(entry)
            return result

        # No null separators - use logic for single entry
        first_value = non_empty_values[0]

        # Find the highest-priority separator that actually exists in the value.
        # We should only split on that separator (single-entry fields that
        # used one specific separator) rather than splitting on every known
        # separator sequentially which can produce incorrect fragmentation when
        # lower-priority separators appear inside values.
        for separator in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED:
            if separator in first_value:
                return [p.strip() for p in first_value.split(separator) if p.strip()]

        # No known separator found; return the single trimmed value as list
        return [first_value.strip()]

    def _extract_and_regroup_raw_metadata_unique_entries(
        self, raw_metadata_with_potential_duplicate_keys: RawMetadataDict
    ) -> RawMetadataDict:
        raw_clean_metadata: RawMetadataDict = {}

        for raw_metadata_key, raw_metadata_value in raw_metadata_with_potential_duplicate_keys.items():
            if raw_metadata_value is None:
                raw_clean_metadata[raw_metadata_key] = None
            elif isinstance(raw_metadata_value, list):
                raw_clean_metadata[raw_metadata_key] = raw_metadata_value

        return raw_clean_metadata

    def _get_genre_name_from_raw_clean_metadata_id3v1(
        self, raw_clean_metadata: RawMetadataDict, raw_metadata_ket: RawMetadataKey
    ) -> UnifiedMetadataValue:
        """RIFF and ID3v1 files typically contain a genre code.

        that corresponds to the ID3v1 genre list. This method converts the code to a human-readable genre name.
        """
        if raw_metadata_ket in raw_clean_metadata:
            raw_value_list = raw_clean_metadata.get(raw_metadata_ket)
            if not raw_value_list or len(raw_value_list) == 0:
                return None
            raw_value = raw_value_list[0]
            try:
                genre_code_or_name = int(cast(int, raw_value))
                genre_name = ID3V1_GENRE_CODE_MAP.get(genre_code_or_name)
            except ValueError:
                genre_name = cast(str, raw_value)

            # Return as list since GENRES_NAMES is a multi-value field
            return [genre_name] if genre_name else None
        return None

    def _get_genres_from_raw_clean_metadata_uppercase_keys(
        self, raw_clean_metadata: RawMetadataDict, raw_metadata_key: RawMetadataKey
    ) -> UnifiedMetadataValue:
        """Extract and process genre entries from raw metadata according to the intelligent genre reading logic.

        This method implements the comprehensive genre reading strategy that handles:
        1. Multiple genre entries from the file
        2. Separator parsing for single entries (text with separators, codes, code+text)
        3. ID3v1 genre code conversion
        4. Consistent list output of genre names

        Args:
            raw_clean_metadata: Dictionary of raw metadata values
            raw_metadata_key: The raw metadata key for genres

        Returns:
            List of genre names, or None if no genres found
        """
        if raw_metadata_key not in raw_clean_metadata:
            return None

        raw_value_list = raw_clean_metadata.get(raw_metadata_key)
        if not raw_value_list:
            return None

        # Step 1: Extract all genre entries from the file
        genre_entries = [str(entry).strip() for entry in raw_value_list if str(entry).strip()]

        if not genre_entries:
            return None

        # Step 2: Process entries based on count
        if len(genre_entries) == 1:
            # Single entry - apply separator parsing if needed
            single_entry = genre_entries[0]

            # Check for codes or code+text without separators (e.g., "(17)(6)", "(17)Rock(6)Blues")
            if self._has_genre_separators(single_entry):
                parsed_genres = self._parse_genre_separators(single_entry)
            elif self._has_genre_codes_without_separators(single_entry):
                parsed_genres = self._parse_genre_codes_and_text(single_entry)
            # Check for text with separators (e.g., "Rock/Blues", "Rock; Alternative")
            else:
                # No special parsing needed
                parsed_genres = [single_entry]
        else:
            # Multiple entries - use as-is (no separator parsing)
            parsed_genres = genre_entries

        # Step 3: Convert any genre codes or codes + names to names using ID3v1 genre code map
        converted_genres = []
        for genre in parsed_genres:
            converted = self._convert_genre_code_or_text_to_name(genre)
            if converted:
                converted_genres.append(converted)

        # Step 4: Return list of genre names (remove duplicates while preserving order)
        unique_genres = []
        for genre in converted_genres:
            if genre not in unique_genres:
                unique_genres.append(genre)
        return unique_genres if unique_genres else None

    def _has_genre_codes_without_separators(self, genre_string: str) -> bool:
        """Check if a genre string contains genre codes without separators.

        Examples: "(17)(6)", "(17)Rock(6)Blues", "(17)Rock(6)"
        """
        import re

        # Pattern matches parentheses with digits, optionally followed by text, repeated
        pattern = r"^\(\d+\)(?:\w*\(\d+\))*\w*$"
        return bool(re.match(pattern, genre_string))

    def _has_genre_separators(self, genre_string: str) -> bool:
        """Check if a genre string contains separators for multiple genres.

        Examples: "Rock/Blues", "Rock; Alternative", "(17)Rock/(6)Blues"
        """
        # Check for common separators

        return any(sep in genre_string for sep in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED)

    def _parse_genre_codes_and_text(self, genre_string: str) -> list[str]:
        """Parse genre codes and code+text combinations without separators.

        Examples: "(17)(6)" -> ["(17)", "(6)"]
                  "(17)Rock(6)Blues" -> ["(17)Rock", "(6)Blues"]
        """
        import re

        # Find all consecutive (number)text patterns
        # Each match is a complete code or code+text unit
        pattern = r"\(\d+\)[^(\d]*"
        matches = re.findall(pattern, genre_string)

        if matches:
            # Filter out any empty matches
            return [match for match in matches if match]

        # Fallback: if no matches, return the original string
        return [genre_string]

    def _parse_genre_separators(self, genre_string: str) -> list[str]:
        """Parse genre strings with separators using smart separator logic.

        Examples: "Rock/Blues" -> ["Rock", "Blues"]
                  "(17)Rock/(6)Blues" -> ["(17)Rock", "(6)Blues"]
        """
        # Use the same separator priority as multi-value parsing
        for separator in METADATA_MULTI_VALUE_SEPARATORS_PRIORITIZED:
            if separator in genre_string:
                return [part.strip() for part in genre_string.split(separator) if part.strip()]
        # No separator found
        return [genre_string]

    def _convert_genre_code_or_text_to_name(self, genre_entry: str) -> str | None:
        """Convert a genre code or code+text entry to a genre name using ID3V1_GENRE_CODE_MAP.

        For code + text entries, use text part only for more flexibility.

        Examples:
        - "(17)" -> "Rock"
        - "(17)Rock" -> "Rock" (text part preferred)
        - "17" -> "Rock" (bare numeric code)
        - "Rock" -> "Rock"
        - "(999)" -> None (invalid code)
        """
        import re

        # Check for code + text pattern: (number)text
        code_text_match = re.match(r"^\((\d+)\)(.+)$", genre_entry)
        if code_text_match:
            code = int(code_text_match.group(1))
            text_part = code_text_match.group(2).strip()
            # For code + text entries, use text part only for more flexibility
            if text_part:
                return text_part

        # Check for code only pattern: (number)
        code_only_match = re.match(r"^\((\d+)\)$", genre_entry)
        if code_only_match:
            code = int(code_only_match.group(1))
            return ID3V1_GENRE_CODE_MAP.get(code)

        # Check for bare numeric code: number (without parentheses)
        if genre_entry.isdigit():
            code = int(genre_entry)
            return ID3V1_GENRE_CODE_MAP.get(code)

        # No code found, return as-is
        return genre_entry if genre_entry else None

    def get_unified_metadata(self) -> UnifiedMetadata:
        unified_metadata: UnifiedMetadata = {}
        for metadata_key in self.metadata_keys_direct_map_read:
            unified_metadata_value = self.get_unified_metadata_field(metadata_key)
            if unified_metadata_value is not None:
                unified_metadata[metadata_key] = unified_metadata_value
        return unified_metadata

    def get_unified_metadata_field(self, unified_metadata_key: UnifiedMetadataKey) -> UnifiedMetadataValue:
        if unified_metadata_key not in self.metadata_keys_direct_map_read:
            metadata_format_name = self._get_formatted_metadata_format_name()
            msg = f"{unified_metadata_key} metadata not supported by {metadata_format_name} format"
            raise MetadataFieldNotSupportedByMetadataFormatError(msg)

        if self.raw_clean_metadata_uppercase_keys is None:
            self._extract_raw_clean_metadata_uppercase_keys_from_file()

        raw_metadata_key = self.metadata_keys_direct_map_read[unified_metadata_key]
        if not raw_metadata_key:
            if self.raw_clean_metadata_uppercase_keys is None:
                return None
            return self._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
                raw_clean_metadata_uppercase_keys=self.raw_clean_metadata_uppercase_keys,
                unified_metadata_key=unified_metadata_key,
            )

        if self.raw_clean_metadata_uppercase_keys is None:
            return None
        if raw_metadata_key not in self.raw_clean_metadata_uppercase_keys:
            return None
        value = self.raw_clean_metadata_uppercase_keys[raw_metadata_key]

        if not value or not len(value):
            return None

        # For string types, we need to distinguish between None (not present) and empty string (present but empty)
        unified_metadata_key_optional_type = unified_metadata_key.get_optional_type()
        if unified_metadata_key_optional_type is str and value[0] == "":
            return ""

        if not value[0]:
            return None

        # Special handling for TRACK_NUMBER parsing
        if unified_metadata_key == UnifiedMetadataKey.TRACK_NUMBER:
            track_str = str(value[0])
            if re.match(r"^\d+([-/]\d*)?$", track_str):
                return track_str
            return None

        from typing import get_args, get_origin

        origin = get_origin(unified_metadata_key_optional_type)
        if unified_metadata_key_optional_type is int:
            return int(value[0]) if value else None
        if unified_metadata_key_optional_type is float:
            return float(value[0]) if value else None
        if origin is not None and (origin == Union or (hasattr(origin, "__name__") and origin.__name__ == "UnionType")):
            # Handle union types like int | float
            arg_types = get_args(unified_metadata_key_optional_type)
            if int in arg_types and float in arg_types:
                # For int | float, prefer int if it's a whole number, otherwise float
                try:
                    num_value = float(value[0]) if value else None
                    if num_value is not None and num_value.is_integer():
                        return int(num_value)
                    else:  # noqa: RET505
                        return num_value
                except (ValueError, TypeError):
                    return None
        if unified_metadata_key_optional_type is str:
            return str(value[0]) if value else None
        if unified_metadata_key_optional_type == list[str]:
            return self._get_value_from_multi_values_data(
                unified_metadata_key, cast(list[str], value), raw_metadata_key
            )
        msg = f"Unsupported metadata type: {unified_metadata_key_optional_type}"
        raise ValueError(msg)

    def _get_value_from_multi_values_data(
        self, unified_metadata_key: UnifiedMetadataKey, value: list[str], raw_metadata_key: RawMetadataKey
    ) -> UnifiedMetadataValue:
        if not value:
            return None
        values_list_str = value
        if unified_metadata_key == UnifiedMetadataKey.GENRES_NAMES:
            # Use specialized genre reading logic
            if self.raw_clean_metadata_uppercase_keys is None:
                return None
            return self._get_genres_from_raw_clean_metadata_uppercase_keys(
                self.raw_clean_metadata_uppercase_keys, raw_metadata_key
            )
        if unified_metadata_key.can_semantically_have_multiple_values():
            # Apply smart parsing logic for semantically multi-value fields
            if self._should_apply_smart_parsing(values_list_str):
                # Apply parsing for single entry (legacy data detection)
                parsed_values = self._apply_smart_parsing(values_list_str)
                return parsed_values if parsed_values else None
            # No parsing - return as-is but filter empty/whitespace values
            filtered_values = [val.strip() for val in values_list_str if val.strip()]
            return filtered_values if filtered_values else None
        return values_list_str

    def get_header_info(self) -> dict:
        """Get header information for this metadata format.

        Returns:
            Dictionary containing header information:
            {
                'present': boolean
                'version': str | None,
                'size_bytes': int | None,
                'position': int | None,
                'flags': dict,
                'extended_header': dict
            }
        """
        msg = "Not implemented for this format"
        raise NotImplementedError(msg)

    def get_raw_metadata_info(self) -> dict:
        """Get raw metadata information for this format.

        Returns:
            Dictionary containing raw metadata details:
            {
                'raw_data': bytes | None,
                'parsed_fields': dict,
                'frames': dict,
                'comments': dict,
                'chunk_structure': dict
            }
        """
        msg = "Not implemented for this format"
        raise NotImplementedError(msg)

    def update_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        if not self.metadata_keys_direct_map_write:
            msg = "This format does not support metadata modification"
            raise MetadataFieldNotSupportedByMetadataFormatError(msg)

        if not self.update_using_mutagen_metadata:
            self._update_not_using_mutagen_metadata(unified_metadata)
        else:
            if self.raw_mutagen_metadata is None:
                self.raw_mutagen_metadata = self._extract_mutagen_metadata()

            for unified_metadata_key in list(unified_metadata.keys()):
                app_metadata_value = unified_metadata[unified_metadata_key]

                # Filter out empty values for list-type metadata before processing
                if isinstance(app_metadata_value, list):
                    app_metadata_value = self._filter_valid_values(cast(list[str | None], app_metadata_value))
                    # If all values were filtered out, set to None to remove the field
                    if not app_metadata_value:
                        app_metadata_value = None

                if unified_metadata_key not in self.metadata_keys_direct_map_write:
                    metadata_format_name = self._get_formatted_metadata_format_name()
                    msg = f"{unified_metadata_key} metadata not supported by {metadata_format_name} format"
                    raise MetadataFieldNotSupportedByMetadataFormatError(msg)
                raw_metadata_key = self.metadata_keys_direct_map_write[unified_metadata_key]
                if raw_metadata_key:
                    self._update_formatted_value_in_raw_mutagen_metadata(
                        raw_mutagen_metadata=self.raw_mutagen_metadata,
                        raw_metadata_key=raw_metadata_key,
                        app_metadata_value=app_metadata_value,
                    )
                else:
                    self._update_undirectly_mapped_metadata(
                        raw_mutagen_metadata=self.raw_mutagen_metadata,
                        app_metadata_value=app_metadata_value,
                        unified_metadata_key=unified_metadata_key,
                    )
            self.raw_mutagen_metadata.save(self.audio_file.file_path)

    def delete_metadata(self) -> bool:
        if self.raw_mutagen_metadata is None:
            self.raw_mutagen_metadata = self._extract_mutagen_metadata()

        try:
            self.raw_mutagen_metadata.delete()
        except Exception:
            return False
        else:
            return True

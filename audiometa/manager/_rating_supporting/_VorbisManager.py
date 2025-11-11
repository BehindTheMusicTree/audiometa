import struct
from typing import Any, TypeVar, cast

import taglib  # type: ignore[import-not-found]

from ..._audio_file import _AudioFile
from ...exceptions import FileCorruptedError, InvalidRatingValueError, MetadataFieldNotSupportedByMetadataFormatError
from ...utils.rating_profiles import RatingWriteProfile
from ...utils.types import AppMetadataValue, RawMetadataDict, RawMetadataKey, UnifiedMetadata
from .._MetadataManager import UnifiedMetadataKey
from ._RatingSupportingMetadataManager import _RatingSupportingMetadataManager

T = TypeVar("T", str, int)


class _VorbisManager(_RatingSupportingMetadataManager):
    """Manages Vorbis comments for audio files.

    Vorbis comments are used to store metadata in audio files, primarily in FLAC format.
    (OGG file support is planned but not yet implemented.)
    They are more flexible and extensible compared to ID3 tags, allowing for a wide range of metadata fields.

    Vorbis comments are key-value pairs, where the key is a field name and the value is the corresponding metadata.
    Common fields are defined in the VorbisKey enum class, which includes standardized keys for metadata like
    title, artist, album, genre, rating, and more.

    Implementation Details:
    - Reading: Custom FLAC parsing to preserve original Vorbis comment key casing
    - Writing: TagLib library to maintain proper key casing per Vorbis specification
    - The Vorbis specification recommends uppercase keys, which TagLib preserves during writing
    - Custom parsing for reading avoids mutagen's lowercase conversion behavior

    Compatible Extensions:
    - FLAC: Fully supports Vorbis comments.

    TODO: OGG file support is planned but not yet implemented.
    """

    class VorbisKey(RawMetadataKey):
        # Standard
        TITLE = "TITLE"
        ARTIST = "ARTIST"
        ALBUM = "ALBUM"
        ALBUM_ARTISTS = "ALBUMARTIST"
        GENRES_NAMES = "GENRE"
        DATE = "DATE"  # Creation/Release date
        TRACK_NUMBER = "TRACKNUMBER"
        COMMENT = "COMMENT"
        PERFORMER = "PERFORMER"
        COPYRIGHT = "COPYRIGHT"
        LICENSE = "LICENSE"
        ORGANIZATION = "ORGANIZATION"  # Label or organization
        DESCRIPTION = "DESCRIPTION"
        LOCATION = "LOCATION"  # Recording location
        CONTACT = "CONTACT"  # Contact information
        ISRC = "ISRC"  # International Standard Recording Code

        # Non-standard
        LANGUAGE = "LANGUAGE"
        BPM = "BPM"
        COMPOSERS = "COMPOSER"
        ENCODED_BY = "ENCODEDBY"  # Encoder software
        RATING = "RATING"
        RATING_TRAKTOR = "RATING WMP"  # Traktor rating
        UNSYNCHRONIZED_LYRICS = "LYRICS"  # Not standard
        REPLAYGAIN = "REPLAYGAIN"
        PUBLISHER = "PUBLISHER"

    def __init__(self, audio_file: _AudioFile, normalized_rating_max_value: int | None = None):
        metadata_keys_direct_map_read = {
            UnifiedMetadataKey.TITLE: self.VorbisKey.TITLE,
            UnifiedMetadataKey.ARTISTS: self.VorbisKey.ARTIST,
            UnifiedMetadataKey.ALBUM: self.VorbisKey.ALBUM,
            UnifiedMetadataKey.ALBUM_ARTISTS: self.VorbisKey.ALBUM_ARTISTS,
            UnifiedMetadataKey.GENRES_NAMES: self.VorbisKey.GENRES_NAMES,
            UnifiedMetadataKey.RATING: None,
            UnifiedMetadataKey.LANGUAGE: self.VorbisKey.LANGUAGE,
            UnifiedMetadataKey.RELEASE_DATE: self.VorbisKey.DATE,
            UnifiedMetadataKey.TRACK_NUMBER: self.VorbisKey.TRACK_NUMBER,
            UnifiedMetadataKey.BPM: self.VorbisKey.BPM,
            UnifiedMetadataKey.COMPOSERS: self.VorbisKey.COMPOSERS,
            UnifiedMetadataKey.COPYRIGHT: self.VorbisKey.COPYRIGHT,
            UnifiedMetadataKey.COMMENT: self.VorbisKey.COMMENT,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: self.VorbisKey.UNSYNCHRONIZED_LYRICS,
            UnifiedMetadataKey.REPLAYGAIN: self.VorbisKey.REPLAYGAIN,
            UnifiedMetadataKey.PUBLISHER: self.VorbisKey.PUBLISHER,
        }
        metadata_keys_direct_map_write = {
            UnifiedMetadataKey.TITLE: self.VorbisKey.TITLE,
            UnifiedMetadataKey.ARTISTS: self.VorbisKey.ARTIST,
            UnifiedMetadataKey.ALBUM: self.VorbisKey.ALBUM,
            UnifiedMetadataKey.ALBUM_ARTISTS: self.VorbisKey.ALBUM_ARTISTS,
            UnifiedMetadataKey.GENRES_NAMES: self.VorbisKey.GENRES_NAMES,
            UnifiedMetadataKey.RATING: None,
            UnifiedMetadataKey.LANGUAGE: self.VorbisKey.LANGUAGE,
            UnifiedMetadataKey.RELEASE_DATE: self.VorbisKey.DATE,
            UnifiedMetadataKey.TRACK_NUMBER: self.VorbisKey.TRACK_NUMBER,
            UnifiedMetadataKey.BPM: self.VorbisKey.BPM,
            UnifiedMetadataKey.COMPOSERS: self.VorbisKey.COMPOSERS,
            UnifiedMetadataKey.COPYRIGHT: self.VorbisKey.COPYRIGHT,
            UnifiedMetadataKey.COMMENT: self.VorbisKey.COMMENT,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: self.VorbisKey.UNSYNCHRONIZED_LYRICS,
            UnifiedMetadataKey.REPLAYGAIN: self.VorbisKey.REPLAYGAIN,
            UnifiedMetadataKey.PUBLISHER: self.VorbisKey.PUBLISHER,
        }
        super().__init__(
            audio_file=audio_file,
            metadata_keys_direct_map_read=cast(
                dict[UnifiedMetadataKey, RawMetadataKey | None], metadata_keys_direct_map_read
            ),
            metadata_keys_direct_map_write=cast(
                dict[UnifiedMetadataKey, RawMetadataKey | None], metadata_keys_direct_map_write
            ),
            rating_write_profile=RatingWriteProfile.BASE_100_PROPORTIONAL,
            normalized_rating_max_value=normalized_rating_max_value,
        )

    def _extract_mutagen_metadata(self) -> RawMetadataDict:
        """Read Vorbis comments from a FLAC file.

        This is a custom implementation for extracting Vorbis comments because:
            - Mutagen does not preserve original key case
            - taglib merges duplicate keys with multiple values into a single value
        Returns a dict: {key: [values]}.
        """
        comments: dict[str, list[str]] = {}
        with open(self.audio_file.file_path, "rb") as f:
            # --- Step 1: Skip ID3v2 tags if present, then find FLAC header ---
            header = f.read(4)
            if header == b"ID3\x03" or header == b"ID3\x04":
                # ID3v2 tag present, skip it
                f.seek(0)  # Reset to beginning
                # Read ID3v2 header to get tag size
                id3_header = f.read(10)
                if len(id3_header) >= 10:
                    # ID3v2 tag size is stored in bytes 6-9 (syncsafe integer)
                    tag_size = (
                        ((id3_header[6] & 0x7F) << 21)
                        | ((id3_header[7] & 0x7F) << 14)
                        | ((id3_header[8] & 0x7F) << 7)
                        | (id3_header[9] & 0x7F)
                    )
                    # Skip the ID3v2 tag
                    f.seek(tag_size + 10)
                # Now read the FLAC header
                header = f.read(4)

            if header != b"fLaC":
                raise ValueError("Not a valid FLAC file")

            # --- Step 2: Read metadata blocks ---
            is_last = False
            while not is_last:
                block_header = f.read(4)
                if len(block_header) < 4:
                    break
                is_last = bool(block_header[0] & 0x80)
                block_type = block_header[0] & 0x7F
                block_size = struct.unpack(">I", b"\x00" + block_header[1:])[0]
                data = f.read(block_size)

                # --- Step 3: Look for VORBIS_COMMENT block ---
                if block_type == 4:  # VORBIS_COMMENT
                    offset = 0
                    # Vendor length (32-bit LE)
                    vendor_len = struct.unpack("<I", data[offset : offset + 4])[0]
                    offset += 4 + vendor_len
                    # Number of comments
                    num_comments = struct.unpack("<I", data[offset : offset + 4])[0]
                    offset += 4

                    for _ in range(num_comments):
                        comment_len = struct.unpack("<I", data[offset : offset + 4])[0]
                        offset += 4
                        comment_bytes = data[offset : offset + comment_len]
                        offset += comment_len
                        comment_str = comment_bytes.decode("utf-8", errors="replace")

                        # Split key=value at first '='
                        if "=" not in comment_str:
                            continue
                        key, value = comment_str.split("=", 1)
                        # Preserve original case
                        comments.setdefault(key, []).append(value)
                    break

        return cast(RawMetadataDict, comments)

    def _convert_raw_mutagen_metadata_to_dict_with_potential_duplicate_keys(
        self,
        raw_mutagen_metadata: dict,
    ) -> RawMetadataDict:
        # _extract_mutagen_metadata already returns metadata with list values
        return raw_mutagen_metadata

    def _extract_raw_clean_metadata_uppercase_keys_from_file(self) -> None:
        if self.raw_clean_metadata is None:
            self.raw_clean_metadata = self._extract_cleaned_raw_metadata_from_file()

        # Merge case variants of keys (e.g., "ARTIST" and "artist" -> "ARTIST")
        # Vorbis comments preserve original key case, so we need to merge them
        # Use a temporary dict with string keys for merging, then convert to RawMetadataDict
        # Use Any for values since we're merging different list types and will convert back
        temp_dict: dict[str, list[Any]] = {}
        for key, values in self.raw_clean_metadata.items():
            if values is None:
                continue
            uppercase_key = str(key).upper()
            # Merge values from all case variants
            if isinstance(values, list):
                # values is guaranteed to be a list here (not None)
                if uppercase_key not in temp_dict:
                    # First occurrence: use the list as-is (preserves type)
                    temp_dict[uppercase_key] = list(values)
                else:
                    # Subsequent occurrence: merge while avoiding duplicates
                    existing_list = temp_dict[uppercase_key]
                    for val in values:
                        if val not in existing_list:
                            existing_list.append(val)

        # Convert to RawMetadataDict format
        # Since RawMetadataKey is str, Enum, we can use string keys directly at runtime
        # Use cast to satisfy type checker since RawMetadataKey is str, Enum
        result_dict: dict[str | RawMetadataKey, list[str] | list[int] | list[float]] = {}
        for key_str, values_list in temp_dict.items():
            # Try to find matching enum member, otherwise use string as key
            # RawMetadataKey is str, Enum so string keys work at runtime
            final_key: RawMetadataKey | str = key_str
            for enum_class in RawMetadataKey.__subclasses__():
                for member in enum_class.__members__.values():
                    if str(member.value).upper() == key_str:
                        final_key = member
                        break
                if isinstance(final_key, RawMetadataKey):
                    break
            # values_list is guaranteed to be a list (not empty, not None)
            result_dict[final_key] = values_list

        # Cast to RawMetadataDict since RawMetadataKey is str, Enum and string keys work
        self.raw_clean_metadata_uppercase_keys = cast(RawMetadataDict, result_dict)

    def _get_raw_rating_by_traktor_or_not(self, raw_clean_metadata: RawMetadataDict) -> tuple[int | None, bool]:
        if self.VorbisKey.RATING in raw_clean_metadata:
            rating_list = raw_clean_metadata[self.VorbisKey.RATING]
            if rating_list and len(rating_list) > 0 and rating_list[0] is not None:
                return int(rating_list[0]), False

        if self.VorbisKey.RATING_TRAKTOR in raw_clean_metadata:
            rating_list = raw_clean_metadata[self.VorbisKey.RATING_TRAKTOR]
            if rating_list and len(rating_list) > 0 and rating_list[0] is not None:
                return int(rating_list[0]), True

        return None, False

    def _update_formatted_value_in_raw_mutagen_metadata(
        self,
        raw_mutagen_metadata: dict,
        raw_metadata_key: RawMetadataKey,
        app_metadata_value: AppMetadataValue,
    ) -> None:
        if app_metadata_value is not None:
            if isinstance(app_metadata_value, list):
                # For multi-value fields, keep as separate entries
                raw_mutagen_metadata[raw_metadata_key] = [str(v) for v in app_metadata_value]
            else:
                # Convert BPM to string for Vorbis comments
                if raw_metadata_key == self.VorbisKey.BPM:
                    raw_mutagen_metadata[raw_metadata_key] = [str(app_metadata_value)]
                else:
                    raw_mutagen_metadata[raw_metadata_key] = [str(app_metadata_value)]
        elif raw_metadata_key in raw_mutagen_metadata:
            del raw_mutagen_metadata[raw_metadata_key]

    def update_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        """Update Vorbis metadata in FLAC files using external metaflac tool.

        This method uses the metaflac external command-line tool instead of Python libraries
        to ensure proper Vorbis specification compliance and prevent file corruption.

        Key Features:
        - **Uppercase Key Casing**: Preserves proper Vorbis key casing (TITLE, ARTIST, etc.)
          unlike mutagen which converts to lowercase
        - **Multi-Value Support**: Creates separate tag entries for list values
        - **File Integrity**: Prevents corruption that occurs with some Python libraries
        - **Deletion Support**: Properly removes tags when None values are passed

        Multi-Value Behavior:
        - List values create separate tag entries (Vorbis specification compliant)
        - Example: ["Artist One", "Artist Two"] creates:
          * ARTIST=Artist One
          * ARTIST=Artist Two
        - NOT: ARTIST=Artist One;Artist Two (semicolon-joined)

        External Tool Requirements:
        - Requires 'metaflac' command-line tool to be installed
        - Falls back to FileCorruptedError if metaflac is not available

        Args:
            unified_metadata: Dictionary of metadata to write/update
                             Use None values to delete specific fields

        Raises:
            MetadataFieldNotSupportedByMetadataFormatError: If field not supported
            FileCorruptedError: If metaflac tool fails or is not found
        """
        if not self.metadata_keys_direct_map_write:
            raise MetadataFieldNotSupportedByMetadataFormatError("This format does not support metadata modification")

        self._validate_and_process_rating(unified_metadata)

        # Get current metadata
        current_metadata = self._extract_mutagen_metadata()

        # Update metadata dict
        for unified_metadata_key in list(unified_metadata.keys()):
            app_metadata_value = unified_metadata[unified_metadata_key]
            if unified_metadata_key not in self.metadata_keys_direct_map_write:
                raise MetadataFieldNotSupportedByMetadataFormatError(
                    f"{unified_metadata_key} metadata not supported by this format"
                )
            else:
                raw_metadata_key = self.metadata_keys_direct_map_write[unified_metadata_key]
                if raw_metadata_key:
                    self._update_formatted_value_in_raw_mutagen_metadata(
                        raw_mutagen_metadata=current_metadata,
                        raw_metadata_key=raw_metadata_key,
                        app_metadata_value=app_metadata_value,
                    )
                else:
                    self._update_undirectly_mapped_metadata(
                        raw_mutagen_metadata=current_metadata,
                        app_metadata_value=app_metadata_value,
                        unified_metadata_key=unified_metadata_key,
                    )

        # Write metadata using metaflac
        self._write_metadata_with_metaflac(current_metadata)

        # Clear cached metadata to ensure subsequent reads reflect the changes
        self.raw_clean_metadata = None
        self.raw_clean_metadata_uppercase_keys = None

    def _write_metadata_with_metaflac(self, metadata: dict) -> None:
        """Write metadata to the FLAC file using metaflac external tool."""
        try:
            import subprocess

            # Map unified metadata keys to metaflac tag names (uppercase)
            key_mapping = {
                "TITLE": "TITLE",
                "ARTIST": "ARTIST",
                "ALBUM": "ALBUM",
                "DATE": "DATE",
                "GENRE": "GENRE",
                "COMMENT": "COMMENT",
                "TRACKNUMBER": "TRACKNUMBER",
                "BPM": "BPM",
                "COMPOSER": "COMPOSER",
                "COPYRIGHT": "COPYRIGHT",
                "LYRICS": "LYRICS",
                "LANGUAGE": "LANGUAGE",
                "RATING": "RATING",
                "ALBUMARTIST": "ALBUMARTIST",
                "MOOD": "MOOD",
                "KEY": "KEY",
                "ENCODER": "ENCODER",
                "URL": "URL",
                "ISRC": "ISRC",
                "PUBLISHER": "PUBLISHER",
            }

            # Get all possible tags that we might need to remove
            # This includes both tags in the metadata dict and all possible tags
            tags_to_remove = set()

            # Add tags that are in the metadata dict (these are being updated/deleted)
            for key in metadata.keys():
                if key in key_mapping:
                    tags_to_remove.add(key_mapping[key])

            # Also remove all possible tags to ensure clean state
            # This is necessary because we might be deleting tags that aren't in the metadata dict
            for metaflac_key in key_mapping.values():
                tags_to_remove.add(metaflac_key)

            # Remove all existing tags
            if tags_to_remove:
                for metaflac_key in tags_to_remove:
                    try:
                        subprocess.run(
                            ["metaflac", "--remove-tag=" + metaflac_key, self.audio_file.file_path],
                            check=True,
                            capture_output=True,
                        )
                    except subprocess.CalledProcessError:
                        # Ignore errors when removing non-existent tags
                        pass

            # Then, add new tags for non-None values
            set_cmd = ["metaflac"]
            for key, values in metadata.items():
                if key in key_mapping and values is not None:
                    metaflac_key = key_mapping[key]

                    # Handle list values by creating separate tag entries
                    if isinstance(values, list):
                        for value in values:
                            if value:  # Only add non-empty values
                                set_cmd.extend(["--set-tag", f"{metaflac_key}={value}"])
                    else:
                        value = str(values)
                        if value:  # Only add non-empty values
                            set_cmd.extend(["--set-tag", f"{metaflac_key}={value}"])

            # Add file path and execute
            if len(set_cmd) > 1:  # Only if we have tags to set
                set_cmd.append(self.audio_file.file_path)
                subprocess.run(set_cmd, check=True, capture_output=True)

        except subprocess.CalledProcessError as e:
            raise FileCorruptedError(f"Failed to write metadata with metaflac: {e}")
        except FileNotFoundError:
            raise FileCorruptedError(
                "metaflac tool not found. Please install it to write Vorbis metadata to FLAC files."
            )

    def get_header_info(self) -> dict:
        try:
            # Use TagLib to get file information
            file_obj = taglib.File(self.audio_file.file_path)

            # TagLib provides basic info
            info = {
                "present": True,
                "vendor_string": "TagLib",  # TagLib doesn't provide vendor string directly
                "comment_count": sum(len(values) for values in file_obj.tags.values() if values),
                "block_size": 4096,  # Default Vorbis comment block size
            }

            file_obj.close()
            return info
        except Exception:
            return {"present": False, "vendor_string": None, "comment_count": 0, "block_size": 0}

    def get_raw_metadata_info(self) -> dict:
        try:
            # Use TagLib to get metadata
            file_obj = taglib.File(self.audio_file.file_path)

            return {
                "raw_data": None,  # TagLib handles this internally
                "parsed_fields": {},
                "frames": {},
                "comments": dict(file_obj.tags),  # Convert to regular dict
                "chunk_structure": {},
            }
        except Exception:
            return {"raw_data": None, "parsed_fields": {}, "frames": {}, "comments": {}, "chunk_structure": {}}

    def delete_metadata(self) -> bool:
        """Delete all metadata from the FLAC file by removing the VORBIS_COMMENT block."""
        import subprocess

        try:
            # Remove all VORBIS_COMMENT blocks from the FLAC file
            subprocess.run(
                ["metaflac", "--remove", "--block-type=VORBIS_COMMENT", self.audio_file.file_path],
                capture_output=True,
                text=True,
                check=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
        self, raw_clean_metadata: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> AppMetadataValue:
        raise MetadataFieldNotSupportedByMetadataFormatError(f"Metadata key not handled: {unified_metadata_key}")

    def _update_undirectly_mapped_metadata(
        self,
        raw_mutagen_metadata: dict,
        app_metadata_value: AppMetadataValue,
        unified_metadata_key: UnifiedMetadataKey,
    ) -> None:
        if unified_metadata_key == UnifiedMetadataKey.RATING:
            if app_metadata_value is not None:
                if self.normalized_rating_max_value is None:
                    # When no normalization, write value as-is (already validated by parent class)
                    if isinstance(app_metadata_value, (int, float)):
                        raw_mutagen_metadata[self.VorbisKey.RATING] = [str(int(app_metadata_value))]
                    else:
                        raw_mutagen_metadata[self.VorbisKey.RATING] = [str(app_metadata_value)]
                else:
                    try:
                        if isinstance(app_metadata_value, (int, float)):
                            normalized_rating = int(float(app_metadata_value))
                        else:
                            normalized_rating = int(float(str(app_metadata_value)))
                        file_rating = self._convert_normalized_rating_to_file_rating(normalized_rating)
                        raw_mutagen_metadata[self.VorbisKey.RATING] = [str(file_rating)]
                    except (TypeError, ValueError):
                        raise InvalidRatingValueError(
                            f"Invalid rating value: {app_metadata_value}. Expected a numeric value."
                        )
            else:
                # Remove rating
                if self.VorbisKey.RATING in raw_mutagen_metadata:
                    del raw_mutagen_metadata[self.VorbisKey.RATING]
                if self.VorbisKey.RATING_TRAKTOR in raw_mutagen_metadata:
                    del raw_mutagen_metadata[self.VorbisKey.RATING_TRAKTOR]
        else:
            raise MetadataFieldNotSupportedByMetadataFormatError(f"Metadata key not handled: {unified_metadata_key}")

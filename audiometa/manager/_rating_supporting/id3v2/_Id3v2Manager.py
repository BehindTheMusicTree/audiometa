import contextlib
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

from mutagen._file import FileType as MutagenMetadata
from mutagen.id3 import ID3
from mutagen.id3._frames import (
    COMM,
    POPM,
    TALB,
    TBPM,
    TCOM,
    TCON,
    TCOP,
    TDAT,
    TDRC,
    TDRL,
    TENC,
    TIT2,
    TKEY,
    TLAN,
    TMOO,
    TPE1,
    TPE2,
    TPUB,
    TRCK,
    TSRC,
    TXXX,
    TYER,
    USLT,
    WOAR,
)
from mutagen.id3._util import ID3NoHeaderError

from audiometa.utils.unified_metadata_key import UnifiedMetadataKey

from ....utils.tool_path_resolver import get_tool_path

if TYPE_CHECKING:
    from ...._audio_file import _AudioFile
from ....exceptions import FileCorruptedError, MetadataFieldNotSupportedByMetadataFormatError
from ....utils.rating_profiles import RatingWriteProfile
from ....utils.types import RawMetadataDict, RawMetadataKey, UnifiedMetadata, UnifiedMetadataValue
from ..._MetadataManager import _MetadataManager as MetadataManager
from .._RatingSupportingMetadataManager import _RatingSupportingMetadataManager
from ._id3v2_constants import ID3V2_DATE_FORMAT_LENGTH, ID3V2_VERSION_3, ID3V2_VERSION_4


class _Id3v2Manager(_RatingSupportingMetadataManager):
    """ID3v2 metadata manager for audio files.

    ID3v2 Version Compatibility Table:
    +---------------+----------+----------+----------+
    | Player/Device | ID3v2.2  | ID3v2.3  | ID3v2.4  |
    +---------------+----------+----------+----------+
    | Windows Media Player                           |
    |  - WMP 9-12   |    ✓     |    ✓     |    ~     |
    |  - WMP 7-8    |    ✓     |    ✓     |          |
    +---------------+----------+----------+----------+
    | iTunes                                         |
    |  - 12.x+      |    ✓     |    ✓     |    ✓     |
    |  - 7.x-11.x   |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | Winamp                                         |
    |  - 5.x+       |    ✓     |    ✓     |    ✓     |
    |  - 2.x-4.x    |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | MusicBee                                       |
    |  - 3.x+       |    ✓     |    ✓     |    ✓     |
    |  - 2.x        |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | VLC                                            |
    |  - 2.x+       |    ✓     |    ✓     |    ✓     |
    |  - 1.x        |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | Smartphones                                    |
    |  - iOS 7+     |    ✓     |    ✓     |    ✓     |
    |  - Android 4+ |    ✓     |    ✓     |    ✓     |
    |  - Windows    |    ✓     |    ✓     |    ✓     |
    |  - Blackberry |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | Network Players                                |
    |  - Sonos      |    ✓     |    ✓     |    ✓     |
    |  - Roku       |    ✓     |    ✓     |    ~     |
    |  - Chromecast |    ✓     |    ✓     |    ✓     |
    |  - Apple TV   |    ✓     |    ✓     |    ✓     |
    +---------------+----------+----------+----------+
    |iPods/MP3 Players                               |
    |  - iPod 5G+   |    ✓     |    ✓     |    ✓     |
    |  - iPod 1-4G  |    ✓     |    ✓     |    ~     |
    |  - Zune       |    ✓     |    ✓     |    ~     |
    |  - Sony       |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | Car Systems                                    |
    |  - Post-2010  |    ✓     |    ✓     |    ~     |
    |  - Pre-2010   |    ✓     |    ~     |          |
    +---------------+----------+----------+----------+
    | Home Audio Systems                             |
    |  - Post-2000  |    ✓     |    ✓     |    ~     |
    |  - Pre-2000   |    ✓     |    ~     |          |
    +---------------+----------+----------+----------+
    | DJ Software                                    |
    |  - Traktor    |    ✓     |    ✓     |    ✓     |
    |  - Serato     |    ✓     |    ✓     |    ~     |
    |  - VirtualDJ  |    ✓     |    ✓     |    ~     |
    |  - Rekordbox  |    ✓     |    ✓     |    ~     |
    |  - Mixxx      |    ✓     |    ✓     |    ~     |
    |  - Cross DJ   |    ✓     |    ✓     |    ~     |
    |  - djay Pro   |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | Web Browsers                                   |
    |  - Chrome     |    ✓     |    ✓     |    ✓     |
    |  - Firefox    |    ✓     |    ✓     |    ✓     |
    |  - Safari     |    ✓     |    ✓     |    ✓     |
    |  - Edge       |    ✓     |    ✓     |    ✓     |
    +---------------+----------+----------+----------+
    | Gaming Consoles                                |
    |  - PS4/PS5    |    ✓     |    ✓     |    ✓     |
    |  - Xbox Series|    ✓     |    ✓     |    ✓     |
    |  - PS3        |    ✓     |    ✓     |    ~     |
    |  - Xbox 360   |    ✓     |    ✓     |    ~     |
    +---------------+----------+----------+----------+
    | Smart TVs                                      |
    |  - Samsung    |    ✓     |    ✓     |    ~     |
    |  - LG         |    ✓     |    ✓     |    ~     |
    |  - Sony       |    ✓     |    ✓     |    ~     |
    |  - Android TV |    ✓     |    ✓     |    ✓     |
    +---------------+----------+----------+----------+

    Legend:
    ✓ = Full support
    ~ = Partial support/May have issues
      = No support

    Notes:
    - ID3v2.4 introduced UTF-8 encoding and unsync changes
    - Older players may have issues with ID3v2.4's changes
    - For maximum compatibility, ID3v2.3 is recommended

    - ID3:
        - Writing Policy:
            * The app writes ID3v2 tags in the specified version (default: v2.3)
            * When updating an existing file:
                - Tags are upgraded to the specified version if different
                - v2.2, v2.3, or v2.4 tags are upgraded to the specified version
                - Frame IDs are automatically converted
                - All text is encoded in UTF-8
            * Reading supports all versions (v2.2, v2.3, v2.4)
            * Only one ID3v2 version can exist in a file at a time
            * Native format for MP3 files
            * Version selection allows choosing between v2.3 (maximum compatibility) and v2.4 (modern features)

        - ID3v1:
            * Fixed 128-byte format at end of file
            * ASCII only, no Unicode
            * Limited to 30 chars for text fields
            * Single byte for track number (v1.1 only)
            * Genre limited to predefined codes (0-147)
            * Legacy format

        - ID3v2:
            * v2.2:
                - Introduced in 1998
                - Three-character frame IDs (TT2, TP1, etc.)
                - ISO-8859-1 or UCS-2 text encoding
                - All standard fields supported
                - Simpler header structure than v2.3/v2.4
                - Basic support for embedded images
                - Less common but equally functional

            * v2.3:
                - Introduced in 1999
                - TYER+TDAT frames for date (year and date separately)
                - UTF-16/UTF-16BE text encoding
                - Basic unsynchronization
                - All metadata fields supported
                - Better support for embedded images and other binary data
                - Most widely used version

            * v2.4:
                - Introduced in 2000
                - TDRC frame for full timestamps (YYYY-MM-DD)
                - UTF-8 text encoding
                - Extended header features
                - Unsynchronization per frame
                - All metadata fields supported
                - New frames for more detailed metadata (e.g., TDRC for recording time, TDRL for release time)
                - Preferred version for new tags

    For maximum compatibility, ID3v2.3 is used as the default version for writing metadata.
    Users can choose ID3v2.4 for modern features if their target players support it.
    When reading/updating an existing file, the ID3 tags will be updated to the specified version format.
    """

    ID3_RATING_APP_EMAIL = "audiometa-python@audiometa.dev"

    class Id3TextFrame(RawMetadataKey):
        TITLE = "TIT2"
        ARTISTS = "TPE1"
        ALBUM = "TALB"
        ALBUM_ARTISTS = "TPE2"
        GENRES_NAMES = "TCON"

        # In cleaned metadata, the rating is stored as a tuple the potential identifier (e.g. 'Traktor') and the rating
        # value
        RATING = "POPM"
        LANGUAGE = "TLAN"
        RECORDING_TIME = "TDRC"  # ID3v2.4 recording time
        RELEASE_TIME = "TDRL"  # ID3v2.4 release time
        YEAR = "TYER"  # ID3v2.3 year
        DATE = "TDAT"  # ID3v2.3 date (DDMM)
        TRACK_NUMBER = "TRCK"
        BPM = "TBPM"

        # Additional metadata fields
        COMPOSERS = "TCOM"
        PUBLISHER = "TPUB"
        COPYRIGHT = "TCOP"
        UNSYNCHRONIZED_LYRICS = "USLT"
        COMMENT = "COMM"  # Comment frame
        ENCODER = "TENC"
        URL = "WOAR"  # Official artist/performer webpage
        ISRC = "TSRC"
        MOOD = "TMOO"
        KEY = "TKEY"
        REPLAYGAIN = "REPLAYGAIN"

    ID3_TEXT_FRAME_CLASS_MAP: ClassVar[dict[RawMetadataKey, type]] = {
        Id3TextFrame.TITLE: TIT2,
        Id3TextFrame.ARTISTS: TPE1,
        Id3TextFrame.ALBUM: TALB,
        Id3TextFrame.ALBUM_ARTISTS: TPE2,
        Id3TextFrame.GENRES_NAMES: TCON,
        Id3TextFrame.LANGUAGE: TLAN,
        Id3TextFrame.RECORDING_TIME: TDRC,
        Id3TextFrame.RELEASE_TIME: TDRL,
        Id3TextFrame.YEAR: TYER,
        Id3TextFrame.DATE: TDAT,
        Id3TextFrame.TRACK_NUMBER: TRCK,
        Id3TextFrame.BPM: TBPM,
        Id3TextFrame.RATING: POPM,
        Id3TextFrame.COMPOSERS: TCOM,
        Id3TextFrame.PUBLISHER: TPUB,
        Id3TextFrame.COPYRIGHT: TCOP,
        Id3TextFrame.UNSYNCHRONIZED_LYRICS: USLT,
        Id3TextFrame.COMMENT: COMM,
        Id3TextFrame.ENCODER: TENC,
        Id3TextFrame.URL: WOAR,
        Id3TextFrame.ISRC: TSRC,
        Id3TextFrame.MOOD: TMOO,
        Id3TextFrame.KEY: TKEY,
    }

    def __init__(
        self,
        audio_file: "_AudioFile",
        normalized_rating_max_value: int | None = None,
        id3v2_version: tuple[int, int, int] = (2, 3, 0),
    ):
        self.id3v2_version = id3v2_version
        metadata_keys_direct_map_read = {
            UnifiedMetadataKey.TITLE: self.Id3TextFrame.TITLE,
            UnifiedMetadataKey.ARTISTS: self.Id3TextFrame.ARTISTS,
            UnifiedMetadataKey.ALBUM: self.Id3TextFrame.ALBUM,
            UnifiedMetadataKey.ALBUM_ARTISTS: self.Id3TextFrame.ALBUM_ARTISTS,
            UnifiedMetadataKey.GENRES_NAMES: self.Id3TextFrame.GENRES_NAMES,
            UnifiedMetadataKey.RATING: None,
            UnifiedMetadataKey.LANGUAGE: self.Id3TextFrame.LANGUAGE,
            UnifiedMetadataKey.RELEASE_DATE: self.Id3TextFrame.RECORDING_TIME,
            UnifiedMetadataKey.TRACK_NUMBER: self.Id3TextFrame.TRACK_NUMBER,
            UnifiedMetadataKey.BPM: self.Id3TextFrame.BPM,
            UnifiedMetadataKey.COMPOSERS: self.Id3TextFrame.COMPOSERS,
            UnifiedMetadataKey.PUBLISHER: self.Id3TextFrame.PUBLISHER,
            UnifiedMetadataKey.COPYRIGHT: self.Id3TextFrame.COPYRIGHT,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: self.Id3TextFrame.UNSYNCHRONIZED_LYRICS,
            UnifiedMetadataKey.COMMENT: self.Id3TextFrame.COMMENT,
            UnifiedMetadataKey.REPLAYGAIN: None,
        }
        metadata_keys_direct_map_write: dict[UnifiedMetadataKey, RawMetadataKey | None] = {
            UnifiedMetadataKey.TITLE: self.Id3TextFrame.TITLE,
            UnifiedMetadataKey.ARTISTS: self.Id3TextFrame.ARTISTS,
            UnifiedMetadataKey.ALBUM: self.Id3TextFrame.ALBUM,
            UnifiedMetadataKey.ALBUM_ARTISTS: self.Id3TextFrame.ALBUM_ARTISTS,
            UnifiedMetadataKey.GENRES_NAMES: self.Id3TextFrame.GENRES_NAMES,
            UnifiedMetadataKey.RATING: self.Id3TextFrame.RATING,
            UnifiedMetadataKey.LANGUAGE: self.Id3TextFrame.LANGUAGE,
            UnifiedMetadataKey.RELEASE_DATE: self.Id3TextFrame.RECORDING_TIME,
            UnifiedMetadataKey.TRACK_NUMBER: self.Id3TextFrame.TRACK_NUMBER,
            UnifiedMetadataKey.BPM: self.Id3TextFrame.BPM,
            UnifiedMetadataKey.COMPOSERS: self.Id3TextFrame.COMPOSERS,
            UnifiedMetadataKey.PUBLISHER: self.Id3TextFrame.PUBLISHER,
            UnifiedMetadataKey.COPYRIGHT: self.Id3TextFrame.COPYRIGHT,
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: self.Id3TextFrame.UNSYNCHRONIZED_LYRICS,
            UnifiedMetadataKey.COMMENT: self.Id3TextFrame.COMMENT,
            UnifiedMetadataKey.REPLAYGAIN: None,
        }

        super().__init__(
            audio_file=audio_file,
            metadata_keys_direct_map_read=cast(
                dict[UnifiedMetadataKey, RawMetadataKey | None], metadata_keys_direct_map_read
            ),
            metadata_keys_direct_map_write=metadata_keys_direct_map_write,
            rating_write_profile=RatingWriteProfile.BASE_255_NON_PROPORTIONAL,
            normalized_rating_max_value=normalized_rating_max_value,
        )

    def _extract_mutagen_metadata(self) -> RawMetadataDict:
        try:
            id3 = ID3(self.audio_file.file_path, load_v1=False, translate=False)

            # Upgrade to specified version if different
            if id3.version != self.id3v2_version:
                id3.version = self.id3v2_version

            return cast(RawMetadataDict, id3)
        except ID3NoHeaderError:
            try:
                id3 = ID3(self.audio_file.file_path, load_v1=True, translate=False)
                id3.clear()  # Exclude ID3v1 tags
                id3.version = self.id3v2_version
                return cast(RawMetadataDict, id3)
            except ID3NoHeaderError:
                # Create empty ID3 object - will be saved during write operations
                # This allows write operations to work with files that have no ID3v2 header
                id3 = ID3()
                id3.version = self.id3v2_version
                return cast(RawMetadataDict, id3)

    def _convert_raw_mutagen_metadata_to_dict_with_potential_duplicate_keys(
        self, raw_mutagen_metadata: MutagenMetadata
    ) -> RawMetadataDict:
        raw_metadata_id3: ID3 = cast(ID3, raw_mutagen_metadata)
        result: RawMetadataDict = {}

        for frame_key in self.Id3TextFrame.__members__.values():
            if frame_key == self.Id3TextFrame.RATING:
                for raw_mutagen_frame in raw_mutagen_metadata.items():
                    popm_key = raw_mutagen_frame[0]
                    if popm_key.startswith(self.Id3TextFrame.RATING):
                        popm: POPM = raw_mutagen_frame[1]
                        popm_key_without_prefixes = popm_key.replace(f"{self.Id3TextFrame.RATING}:", "")
                        result[self.Id3TextFrame.RATING] = [
                            popm_key_without_prefixes,
                            getattr(popm, "rating", 0),
                        ]
                        break
            elif frame_key == self.Id3TextFrame.COMMENT:
                # Handle COMM frames (comment frames)
                for raw_mutagen_frame in raw_mutagen_metadata.items():
                    if raw_mutagen_frame[0].startswith("COMM"):
                        comm_frame = raw_mutagen_frame[1]
                        result[frame_key] = comm_frame.text
                        break
            elif frame_key == self.Id3TextFrame.UNSYNCHRONIZED_LYRICS:
                # Handle USLT frames (unsynchronized lyrics frames)
                for raw_mutagen_frame in raw_mutagen_metadata.items():
                    if raw_mutagen_frame[0].startswith("USLT"):
                        uslt_frame = raw_mutagen_frame[1]
                        result[frame_key] = [uslt_frame.text]
                        break
            elif frame_key == self.Id3TextFrame.URL:
                # Handle WOAR frames (official artist/performer webpage)
                for raw_mutagen_frame in raw_mutagen_metadata.items():
                    if raw_mutagen_frame[0].startswith("WOAR"):
                        woar_frame = raw_mutagen_frame[1]
                        result[frame_key] = [woar_frame.url]
                        break
            else:
                frame_value = frame_key in raw_metadata_id3 and raw_metadata_id3[frame_key]
                if not frame_value:
                    continue

                if not frame_value.text:
                    continue

                result[frame_key] = frame_value.text

        # Handle TXXX frames for REPLAYGAIN
        for raw_mutagen_frame in raw_mutagen_metadata.items():
            if raw_mutagen_frame[0].startswith("TXXX"):
                txxx_frame = raw_mutagen_frame[1]
                if hasattr(txxx_frame, "desc") and txxx_frame.desc == "REPLAYGAIN":
                    result[self.Id3TextFrame.REPLAYGAIN] = txxx_frame.text
                    break

        # Special handling for release date: if TDRC is not present, try to construct from TYER + TDAT
        # Only do this for ID3v2 files (not ID3v1) and only when both TYER and TDAT are present
        if self.Id3TextFrame.RECORDING_TIME not in result:
            year_key: RawMetadataKey = self.Id3TextFrame.YEAR
            date_key: RawMetadataKey = self.Id3TextFrame.DATE
            tyer_value = result.get(year_key, None)
            tdat_value = result.get(date_key, None)
            if tyer_value and tdat_value:
                # Parse TDAT (DDMM) and TYER to construct YYYY-MM-DD
                try:
                    year = str(tyer_value[0]) if isinstance(tyer_value, list) else str(tyer_value)
                    date_str = str(tdat_value[0]) if isinstance(tdat_value, list) else str(tdat_value)
                    if len(date_str) == ID3V2_DATE_FORMAT_LENGTH:  # DDMM format
                        day = date_str[:2]
                        month = date_str[2:]
                        # Construct YYYY-MM-DD
                        release_date = f"{year}-{month}-{day}"
                        result[self.Id3TextFrame.RECORDING_TIME] = [release_date]
                except (IndexError, ValueError):
                    pass  # If parsing fails, don't add release date

        return result

    def _get_raw_rating_by_traktor_or_not(self, raw_clean_metadata: RawMetadataDict) -> tuple[int | None, bool]:
        for raw_metadata_key, raw_metadata_values in raw_clean_metadata.items():
            if raw_metadata_values and len(raw_metadata_values) > 0 and raw_metadata_key == self.Id3TextFrame.RATING:
                first_popm = cast(list, raw_metadata_values)
                first_popm_identifier = first_popm[0]
                first_popm_rating = first_popm[1]
                if first_popm_identifier.find("Traktor") != -1:
                    return int(first_popm_rating), True
                return int(first_popm_rating), False

        return None, False

    def _update_undirectly_mapped_metadata(
        self,
        raw_mutagen_metadata: ID3,
        app_metadata_value: UnifiedMetadataValue,
        unified_metadata_key: UnifiedMetadataKey,
    ) -> None:
        if unified_metadata_key == UnifiedMetadataKey.REPLAYGAIN:
            # Remove existing TXXX:REPLAYGAIN frames
            raw_mutagen_metadata.delall("TXXX:REPLAYGAIN")
            if app_metadata_value is not None:
                # Add new TXXX frame with desc 'REPLAYGAIN'
                raw_mutagen_metadata.add(TXXX(encoding=3, desc="REPLAYGAIN", text=str(app_metadata_value)))
        else:
            super()._update_undirectly_mapped_metadata(  # type: ignore[safe-super]
                cast(Any, raw_mutagen_metadata), app_metadata_value, unified_metadata_key
            )

    def _get_undirectly_mapped_metadata_value_other_than_rating_from_raw_clean_metadata(
        self, raw_clean_metadata: RawMetadataDict, unified_metadata_key: UnifiedMetadataKey
    ) -> UnifiedMetadataValue:
        if unified_metadata_key == UnifiedMetadataKey.REPLAYGAIN:
            replaygain_key = self.Id3TextFrame.REPLAYGAIN
            if replaygain_key not in raw_clean_metadata:
                return None
            replaygain_value = raw_clean_metadata[replaygain_key]
            if replaygain_value is None:
                return None
            if len(replaygain_value) == 0:
                return None
            first_value = replaygain_value[0]
            return cast(UnifiedMetadataValue, first_value)
        msg = f"Metadata key not handled: {unified_metadata_key}"
        raise MetadataFieldNotSupportedByMetadataFormatError(msg)

    def _update_formatted_value_in_raw_mutagen_metadata(
        self,
        raw_mutagen_metadata: ID3,
        raw_metadata_key: RawMetadataKey,
        app_metadata_value: UnifiedMetadataValue,
    ) -> None:
        raw_mutagen_metadata_id3: ID3 = raw_mutagen_metadata
        raw_mutagen_metadata_id3.delall(raw_metadata_key)

        # If value is None, don't add any frames (field is removed)
        if app_metadata_value is None:
            return

        # Defensive check: if list contains None values, filter them out (should not happen after base class filtering)
        if isinstance(app_metadata_value, list):
            app_metadata_value = [v for v in app_metadata_value if v is not None and v != ""]
            if not app_metadata_value:
                return

        # Handle multiple values by creating separate frames for multi-value fields
        if isinstance(app_metadata_value, list) and all(isinstance(item, str) for item in app_metadata_value):
            # Get the corresponding UnifiedMetadataKey
            unified_metadata_key = None
            if self.metadata_keys_direct_map_write is None:
                return
            for key, raw_key in self.metadata_keys_direct_map_write.items():
                if raw_key == raw_metadata_key:
                    unified_metadata_key = key
                    break

            if unified_metadata_key and unified_metadata_key.can_semantically_have_multiple_values():
                # Check ID3v2 version to determine handling
                # Use self.id3v2_version instead of trying to get it from the mutagen object
                # as the object might not have the version set yet during writing
                id3v2_version = self.id3v2_version

                # ID3v2.4 supports multi-value text frames (single frame with null-separated values per spec)
                if id3v2_version[1] >= ID3V2_VERSION_4:
                    # Create single frame with multiple text values (ID3v2.4 spec: null-separated values in one frame)
                    # Officially supported fields: TPE1 (artists), TPE2 (album artists), TCOM (composers), TCON (genres)
                    text_frame_class = self.ID3_TEXT_FRAME_CLASS_MAP[raw_metadata_key]
                    # Values are already filtered at the base level
                    if app_metadata_value:
                        self._add_id3_frame_v24_multi(raw_mutagen_metadata_id3, text_frame_class, app_metadata_value)
                    return

                # For ID3v2.3, use concatenation with separators (ID3v2.3 doesn't support null-separated values)
                # Find a separator that doesn't appear in any of the values and concatenate
                separator = MetadataManager.find_safe_separator(app_metadata_value)
                app_metadata_value = separator.join(app_metadata_value)
                # Continue to handle as single value
            else:
                # For non-multi-value fields, concatenate with separators as fallback
                # Find a separator that doesn't appear in any of the values and concatenate
                separator = MetadataManager.find_safe_separator(app_metadata_value)
                app_metadata_value = separator.join(app_metadata_value)

        # Handle single values
        text_frame_class = self.ID3_TEXT_FRAME_CLASS_MAP[raw_metadata_key]
        self._add_id3_frame(raw_mutagen_metadata_id3, text_frame_class, raw_metadata_key, app_metadata_value)

    def _add_id3_frame(
        self,
        raw_mutagen_metadata_id3: ID3,
        text_frame_class: type[Any],
        raw_metadata_key: RawMetadataKey,
        app_metadata_value: UnifiedMetadataValue,
    ) -> None:
        """Add a single ID3 frame with proper encoding and format handling."""
        # Determine encoding based on ID3v2 version
        encoding = 0 if self.id3v2_version[1] == ID3V2_VERSION_3 else 3

        if raw_metadata_key == self.Id3TextFrame.RATING:
            raw_mutagen_metadata_id3.add(text_frame_class(email=self.ID3_RATING_APP_EMAIL, rating=app_metadata_value))
        elif raw_metadata_key == self.Id3TextFrame.COMMENT:
            # Handle COMM frames (comment frames)
            raw_mutagen_metadata_id3.add(
                text_frame_class(encoding=encoding, lang="eng", desc="", text=app_metadata_value)
            )
        elif raw_metadata_key == self.Id3TextFrame.UNSYNCHRONIZED_LYRICS:
            # Handle USLT frames (unsynchronized lyrics frames)
            raw_mutagen_metadata_id3.add(
                text_frame_class(encoding=encoding, lang="eng", desc="", text=app_metadata_value)
            )
        elif raw_metadata_key == self.Id3TextFrame.URL:
            # Handle WOAR frames (official artist/performer webpage)
            raw_mutagen_metadata_id3.add(text_frame_class(url=app_metadata_value))
        elif raw_metadata_key == self.Id3TextFrame.BPM:
            # Handle TBPM frames (BPM must be a string)
            raw_mutagen_metadata_id3.add(text_frame_class(encoding=encoding, text=str(app_metadata_value)))
        elif raw_metadata_key == self.Id3TextFrame.TRACK_NUMBER:
            # Handle TRCK frames (track number must be a string)
            raw_mutagen_metadata_id3.add(text_frame_class(encoding=encoding, text=str(app_metadata_value)))
        else:
            raw_mutagen_metadata_id3.add(text_frame_class(encoding=encoding, text=app_metadata_value))

    def _add_id3_frame_v24_multi(
        self, raw_mutagen_metadata_id3: ID3, text_frame_class: type[Any], values: list[str]
    ) -> None:
        """ID3v2.4: add a single text frame containing multiple null-separated values.

        Mutagen accepts a list for the `text` parameter and will write it as
        null-separated strings in a single frame which matches the ID3v2.4 spec.
        """
        # Add one frame with multiple text values (mutagen handles null separation)
        raw_mutagen_metadata_id3.add(text_frame_class(encoding=3, text=values))

    def _preserve_id3v1_metadata(self, file_path: str) -> bytes | None:
        """Read and preserve existing ID3v1 metadata from the end of the file.

        Returns:
            The 128-byte ID3v1 tag data if present, None otherwise
        """
        with Path(file_path).open("rb") as f:
            f.seek(-128, 2)  # Seek to last 128 bytes
            data = f.read(128)
            if data.startswith(b"TAG"):
                return data
        return None

    def _save_with_id3v1_preservation(self, file_path: str, id3v1_data: bytes | None) -> None:
        """Save ID3v2 metadata while preserving ID3v1 data.

        Args:
            file_path: Path to the audio file
            id3v1_data: The 128-byte ID3v1 tag data to preserve, or None
        """
        if self.raw_mutagen_metadata is not None:
            # Extract the major version number from the tuple (2, 3, 0) -> 3
            version_major = self.id3v2_version[1]
            id3_metadata: ID3 = cast(ID3, self.raw_mutagen_metadata)

            if id3v1_data:
                # Save to a temporary file first
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                    temp_path = temp_file.name

                try:
                    # Copy the original file to temp file first
                    shutil.copy2(file_path, temp_path)

                    # Save ID3v2 to temp file (this will overwrite ID3v2 tags in the copy)
                    id3_metadata.save(temp_path, v2_version=version_major)

                    # Read the temp file and append ID3v1 data
                    with Path(temp_path).open("rb") as f:
                        temp_data = f.read()

                    # Append ID3v1 data to the temp file
                    final_data = temp_data + id3v1_data

                    # Write the final file
                    with Path(file_path).open("wb") as f:
                        f.write(final_data)

                finally:
                    # Clean up temp file
                    with contextlib.suppress(OSError):
                        Path(temp_path).unlink()
            else:
                # No ID3v1 data to preserve, save normally
                id3_metadata.save(file_path, v2_version=version_major)

    def _save_with_version(self, file_path: str) -> None:
        """Save ID3 tags with the specified version, preserving existing ID3v1 metadata."""
        if self.raw_mutagen_metadata is not None:
            # Preserve existing ID3v1 metadata before saving ID3v2
            id3v1_data = self._preserve_id3v1_metadata(file_path)

            # Save ID3v2 while preserving ID3v1
            self._save_with_id3v1_preservation(file_path, id3v1_data)

    def update_metadata(self, unified_metadata: UnifiedMetadata) -> None:
        """Update ID3v2 metadata using hybrid approach: mutagen for most formats, external tools for FLAC.

        This method automatically chooses the appropriate tool based on the audio file format
        to ensure optimal performance and file integrity.

        Format-Specific Behavior:
        - **MP3 and other formats**: Uses mutagen (Python library) for fast, reliable updates
        - **FLAC files**: Uses external tools (id3v2/mid3v2) to prevent file corruption

        Why External Tools for FLAC?
        - Mutagen's ID3 class corrupts FLAC file structure when writing ID3v2 tags
        - External tools properly handle FLAC's metadata block structure
        - Prevents "Not a valid FLAC file" errors and file corruption

        Tool Selection Logic:
        - **ID3v2.3**: Uses 'id3v2' command-line tool
        - **ID3v2.4**: Uses 'mid3v2' command-line tool
        - **Other formats**: Uses mutagen for optimal performance

        Key Features:
        - **Version Control**: Maintains specified ID3v2 version (2.3 or 2.4)
        - **ID3v1 Preservation**: Preserves existing ID3v1 tags when present
        - **File Integrity**: Prevents corruption across all supported formats

        External Tool Requirements (FLAC only):
        - Requires 'id3v2' or 'mid3v2' command-line tools
        - Falls back to FileCorruptedError if tools are not available

        Args:
            unified_metadata: Dictionary of metadata to write/update
                             Use None values to delete specific fields

        Raises:
            MetadataFieldNotSupportedByMetadataFormatError: If field not supported
            FileCorruptedError: If external tools fail or are not found (FLAC only)
            ConfigurationError: If rating configuration is invalid
        """
        # For FLAC files, use external tools instead of mutagen to avoid file corruption
        if self.audio_file.file_extension == ".flac":
            self._update_metadata_for_flac(unified_metadata)
            return

        if not self.metadata_keys_direct_map_write:
            msg = "This format does not support metadata modification"
            raise MetadataFieldNotSupportedByMetadataFormatError(msg)

        self._validate_and_process_rating(unified_metadata)

        # Preserve ID3v1 metadata before any modifications
        id3v1_data = self._preserve_id3v1_metadata(self.audio_file.file_path)

        # Update the raw mutagen metadata (without saving yet)
        if self.raw_mutagen_metadata is None:
            self.raw_mutagen_metadata = cast(MutagenMetadata, self._extract_mutagen_metadata())

        id3_metadata: ID3 = cast(ID3, self.raw_mutagen_metadata)

        for unified_metadata_key in list(unified_metadata.keys()):
            app_metadata_value = unified_metadata[unified_metadata_key]
            if unified_metadata_key not in self.metadata_keys_direct_map_write:
                metadata_format_name = self._get_formatted_metadata_format_name()
                msg = f"{unified_metadata_key} metadata not supported by {metadata_format_name} format"
                raise MetadataFieldNotSupportedByMetadataFormatError(msg)
            raw_metadata_key = self.metadata_keys_direct_map_write[unified_metadata_key]
            if raw_metadata_key:
                self._update_formatted_value_in_raw_mutagen_metadata(
                    raw_mutagen_metadata=id3_metadata,
                    raw_metadata_key=raw_metadata_key,
                    app_metadata_value=app_metadata_value,
                )
            else:
                self._update_undirectly_mapped_metadata(
                    raw_mutagen_metadata=id3_metadata,
                    app_metadata_value=app_metadata_value,
                    unified_metadata_key=unified_metadata_key,
                )

        # Save with ID3v1 preservation
        self._save_with_id3v1_preservation(self.audio_file.file_path, id3v1_data)

    def _update_metadata_for_flac(self, unified_metadata: UnifiedMetadata) -> None:
        """Update ID3v2 metadata for FLAC files using external tools to avoid file corruption."""
        if not self.metadata_keys_direct_map_write:
            msg = "This format does not support metadata modification"
            raise MetadataFieldNotSupportedByMetadataFormatError(msg)

        self._validate_and_process_rating(unified_metadata)

        # Use external tools to write ID3v2 metadata to FLAC files
        # This avoids the file corruption that occurs with mutagen's ID3 class
        # Determine the tool and version based on the configured ID3v2 version
        if self.id3v2_version[1] == ID3V2_VERSION_3:
            tool = "id3v2"
            cmd = [get_tool_path("id3v2"), "--id3v2-only"]
        else:  # ID3v2.4
            tool = "mid3v2"
            cmd = [get_tool_path("mid3v2")]

        # Map unified metadata keys to external tool arguments
        key_mapping = {
            UnifiedMetadataKey.TITLE: "--song",
            UnifiedMetadataKey.ARTISTS: "--artist",
            UnifiedMetadataKey.ALBUM: "--album",
            UnifiedMetadataKey.ALBUM_ARTISTS: "--TPE2",
            UnifiedMetadataKey.GENRES_NAMES: "--genre",
            UnifiedMetadataKey.COMMENT: "--comment",
            UnifiedMetadataKey.TRACK_NUMBER: "--track",
            UnifiedMetadataKey.BPM: "--TBPM",
            UnifiedMetadataKey.COMPOSERS: "--TCOM",
            UnifiedMetadataKey.COPYRIGHT: "--TCOP",
            UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: "--USLT",
            UnifiedMetadataKey.LANGUAGE: "--TLAN",
            UnifiedMetadataKey.PUBLISHER: "--TPUB",
        }

        # Build command with metadata
        # First, remove frames for keys explicitly set to None
        frames_to_remove = []
        for unified_key, value in unified_metadata.items():
            if unified_key in self.metadata_keys_direct_map_write:
                raw_key = self.metadata_keys_direct_map_write[unified_key]
                if raw_key and value is None:
                    frames_to_remove.append(raw_key)

        try:
            if frames_to_remove:
                if self.id3v2_version[1] == ID3V2_VERSION_3:
                    # id3v2 supports removing a single frame at a time via -r
                    for frame in frames_to_remove:
                        with contextlib.suppress(subprocess.CalledProcessError):
                            subprocess.run(
                                [get_tool_path("id3v2"), "-r", frame, self.audio_file.file_path],
                                check=True,
                                capture_output=True,
                            )
                else:
                    # mid3v2 supports deleting multiple frames with --delete-frames
                    frames_arg = ",".join(frames_to_remove)
                    with contextlib.suppress(subprocess.CalledProcessError):
                        subprocess.run(
                            [get_tool_path("mid3v2"), f"--delete-frames={frames_arg}", self.audio_file.file_path],
                            check=True,
                            capture_output=True,
                        )
        except FileNotFoundError:
            # If removal tool not found, proceed and hope save will remove frames
            pass

        # Build command with metadata (only non-None values)
        for unified_key, value in unified_metadata.items():
            if unified_key in key_mapping and value is not None:
                tool_arg = key_mapping[unified_key]

                processed_value = value
                if unified_key == UnifiedMetadataKey.ARTISTS and isinstance(value, list):
                    # Handle multiple artists by joining with semicolon
                    processed_value = ";".join(value)
                elif unified_key == UnifiedMetadataKey.GENRES_NAMES and isinstance(value, list):
                    # Handle multiple genres by joining with semicolon
                    processed_value = ";".join(value)
                elif unified_key == UnifiedMetadataKey.COMPOSERS and isinstance(value, list):
                    # Handle multiple composers by joining with semicolon
                    processed_value = ";".join(value)
                elif unified_key == UnifiedMetadataKey.ALBUM_ARTISTS and isinstance(value, list):
                    # Handle multiple album artists by joining with semicolon
                    processed_value = ";".join(value)

                cmd.extend([tool_arg, str(processed_value)])

        # Add file path and execute
        cmd.append(self.audio_file.file_path)

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            msg = f"Failed to write ID3v2 metadata with {tool}: {e}"
            raise FileCorruptedError(msg) from e
        except FileNotFoundError as e:
            msg = f"External tool {tool} not found. Please install it to write ID3v2 metadata to FLAC files."
            raise FileCorruptedError(msg) from e

    def delete_metadata(self) -> bool:
        """Delete all ID3v2 metadata from the audio file.

        This removes all ID3v2 frames from the file while preserving the audio data.
        Uses ID3.delete() which is more reliable than deleting individual frames,
        especially for non-MP3 files like FLAC that might have ID3v2 tags.

        Returns:
            bool: True if metadata was successfully deleted, False otherwise
        """
        try:
            # Create a new ID3 instance and use delete() to remove all ID3v2 tags
            id3 = ID3(self.audio_file.file_path)
            id3.delete()
        except ID3NoHeaderError:
            # No ID3 tags present, consider this a success
            return True
        except Exception:
            return False
        else:
            return True

    def get_header_info(self) -> dict:
        try:
            if self.raw_mutagen_metadata is None:
                self.raw_mutagen_metadata = cast(MutagenMetadata, self._extract_mutagen_metadata())

            if not self.raw_mutagen_metadata:
                return {"present": False, "version": None, "header_size_bytes": 0, "flags": {}, "extended_header": {}}

            id3_metadata: ID3 = cast(ID3, self.raw_mutagen_metadata)

            # Get ID3v2 version
            version = getattr(id3_metadata, "version", None)
            version_str = f"{version[0]}.{version[1]}.{version[2]}" if version else None

            # Get header size
            header_size = getattr(id3_metadata, "size", 0)

            # Get flags
            flags = {}
            if hasattr(id3_metadata, "flags"):
                flags = {
                    "unsync": bool(id3_metadata.flags & 0x80),
                    "extended_header": bool(id3_metadata.flags & 0x40),
                    "experimental": bool(id3_metadata.flags & 0x20),
                    "footer": bool(id3_metadata.flags & 0x10),
                }

            # Get extended header info
            extended_header = {}
            if hasattr(id3_metadata, "extended_header"):
                ext_header = id3_metadata.extended_header
                if ext_header:
                    extended_header = {
                        "size": getattr(ext_header, "size", 0),
                        "flags": getattr(ext_header, "flags", 0),
                        "padding_size": getattr(ext_header, "padding_size", 0),
                    }
        except Exception:
            return {"present": False, "version": None, "header_size_bytes": 0, "flags": {}, "extended_header": {}}
        else:
            return {
                "present": True,
                "version": version_str,
                "header_size_bytes": header_size,
                "flags": flags,
                "extended_header": extended_header,
            }

    def get_raw_metadata_info(self) -> dict:
        try:
            if self.raw_mutagen_metadata is None:
                self.raw_mutagen_metadata = cast(MutagenMetadata, self._extract_mutagen_metadata())

            if not self.raw_mutagen_metadata:
                return {"raw_data": None, "parsed_fields": {}, "frames": {}, "comments": {}, "chunk_structure": {}}

            id3_metadata: ID3 = cast(ID3, self.raw_mutagen_metadata)

            # Get raw frames (exclude binary frames like APIC)
            frames = {}
            binary_frame_types = {
                "APIC:",
                "GEOB:",
                "AENC:",
                "RVA2:",
                "RVRB:",
                "EQU2:",
                "PCNT:",
                "POPM:",
                "RBUF:",
                "LINK:",
                "POSS:",
                "SYLT:",
                "USLT:",
                "SYTC:",
                "ETCO:",
                "MLLT:",
                "OWNE:",
                "COMR:",
                "ENCR:",
                "GRID:",
                "PRIV:",
                "SIGN:",
                "SEEK:",
                "ASPI:",
            }

            for frame_id, frame in id3_metadata.items():
                # Skip binary frames to avoid including large image/audio data
                if frame_id in binary_frame_types:
                    frames[frame_id] = {
                        "text": f"<Binary data: {getattr(frame, 'size', 0)} bytes>",
                        "size": getattr(frame, "size", 0),
                        "flags": getattr(frame, "flags", 0),
                    }
                else:
                    frames[frame_id] = {
                        "text": str(frame) if hasattr(frame, "__str__") else repr(frame),
                        "size": getattr(frame, "size", 0),
                        "flags": getattr(frame, "flags", 0),
                    }
        except Exception:
            return {"raw_data": None, "parsed_fields": {}, "frames": {}, "comments": {}, "chunk_structure": {}}
        else:
            return {
                "raw_data": None,  # ID3v2 data is complex, not storing raw bytes
                "parsed_fields": {},
                "frames": frames,
                "comments": {},
                "chunk_structure": {},
            }

"""Tests for writing ISRC metadata field across different formats."""

import pytest

from audiometa import get_unified_metadata, get_unified_metadata_field, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestISRCWritingByMetadataFormat:
    """Test ISRC writing explicitly by metadata format (ID3v2, Vorbis, RIFF)."""

    # Test 12-character format against each metadata format
    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC17607839",  # Standard 12-char format
            "GBUM71505078",  # UK code
        ],
    )
    def test_id3v2_12_char_format(self, isrc):
        """Test 12-character ISRC format with ID3v2."""
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ISRC: isrc},
                metadata_format=MetadataFormat.ID3V2,
            )
            result = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.ID3V2
            )
            assert result == isrc

    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC17607839",  # Standard 12-char format
            "GBUM71505078",  # UK code
        ],
    )
    def test_vorbis_12_char_format(self, isrc):
        """Test 12-character ISRC format with Vorbis."""
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ISRC: isrc},
                metadata_format=MetadataFormat.VORBIS,
            )
            result = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.VORBIS
            )
            assert result == isrc

    @pytest.mark.parametrize(
        "isrc",
        [
            "USRC17607839",  # Standard 12-char format
            "GBUM71505078",  # UK code
        ],
    )
    def test_riff_12_char_format(self, isrc):
        """Test 12-character ISRC format with RIFF."""
        with temp_file_with_metadata({}, "wav") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ISRC: isrc},
                metadata_format=MetadataFormat.RIFF,
            )
            result = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.RIFF)
            assert result == isrc

    # Test hyphenated format against each metadata format
    @pytest.mark.parametrize(
        "isrc",
        [
            "US-RC1-76-07839",  # Standard hyphenated format
            "GB-UM7-15-05078",  # UK code with hyphens
        ],
    )
    def test_id3v2_hyphenated_format(self, isrc):
        """Test hyphenated ISRC format with ID3v2."""
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ISRC: isrc},
                metadata_format=MetadataFormat.ID3V2,
            )
            result = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.ID3V2
            )
            assert result == isrc

    @pytest.mark.parametrize(
        "isrc",
        [
            "US-RC1-76-07839",  # Standard hyphenated format
            "GB-UM7-15-05078",  # UK code with hyphens
        ],
    )
    def test_vorbis_hyphenated_format(self, isrc):
        """Test hyphenated ISRC format with Vorbis."""
        with temp_file_with_metadata({}, "flac") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ISRC: isrc},
                metadata_format=MetadataFormat.VORBIS,
            )
            result = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.VORBIS
            )
            assert result == isrc

    @pytest.mark.parametrize(
        "isrc",
        [
            "US-RC1-76-07839",  # Standard hyphenated format
            "GB-UM7-15-05078",  # UK code with hyphens
        ],
    )
    def test_riff_hyphenated_format(self, isrc):
        """Test hyphenated ISRC format with RIFF."""
        with temp_file_with_metadata({}, "wav") as test_file:
            update_metadata(
                test_file,
                {UnifiedMetadataKey.ISRC: isrc},
                metadata_format=MetadataFormat.RIFF,
            )
            result = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.RIFF)
            assert result == isrc

    def test_id3v1_isrc_not_supported_on_write(self, sample_mp3_file):
        """Test that ISRC is not supported by ID3v1 format when explicitly targeting ID3v1."""
        test_metadata = {UnifiedMetadataKey.ISRC: "USRC17607839"}

        with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError):
            update_metadata(
                sample_mp3_file,
                test_metadata,
                metadata_format=MetadataFormat.ID3V1,
                fail_on_unsupported_field=True,
            )


@pytest.mark.integration
class TestISRCWritingRoundtrip:
    """Test ISRC writing roundtrip by file format."""

    def test_isrc_with_other_fields(self):
        test_metadata = {
            UnifiedMetadataKey.TITLE: "Test Song",
            UnifiedMetadataKey.ARTISTS: ["Test Artist"],
            UnifiedMetadataKey.ALBUM: "Test Album",
            UnifiedMetadataKey.ISRC: "USRC17607839",
        }

        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, test_metadata)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Test Song"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Test Artist"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "Test Album"
            assert metadata.get(UnifiedMetadataKey.ISRC) == "USRC17607839"

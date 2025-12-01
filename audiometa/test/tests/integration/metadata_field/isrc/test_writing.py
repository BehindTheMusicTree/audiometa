"""Tests for writing ISRC metadata field across different formats."""

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestISRCWriting:
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

    # Test 12-character format across all formats
    @pytest.mark.parametrize(
        ("file_format", "isrc"),
        [
            ("mp3", "USRC17607839"),
            ("flac", "GBUM71505078"),
            ("wav", "FRXM01500014"),
        ],
    )
    def test_isrc_12_char_format_roundtrip(self, file_format, isrc):
        """Test 12-character ISRC format roundtrip across all formats."""
        test_metadata = {UnifiedMetadataKey.ISRC: isrc}

        with temp_file_with_metadata({}, file_format) as test_file:
            update_metadata(test_file, test_metadata)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ISRC) == isrc

    # Test hyphenated format across all formats
    @pytest.mark.parametrize(
        ("file_format", "isrc"),
        [
            ("mp3", "US-RC1-76-07839"),
            ("flac", "GB-UM7-15-05078"),
            ("wav", "FR-XM0-15-00014"),
        ],
    )
    def test_isrc_hyphenated_format_roundtrip(self, file_format, isrc):
        """Test hyphenated ISRC format roundtrip across all formats."""
        test_metadata = {UnifiedMetadataKey.ISRC: isrc}

        with temp_file_with_metadata({}, file_format) as test_file:
            update_metadata(test_file, test_metadata)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.ISRC) == isrc

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

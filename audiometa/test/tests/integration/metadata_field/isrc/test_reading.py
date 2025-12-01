"""Tests for reading ISRC metadata field across different formats."""

import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.riff import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestISRCReading:
    def test_id3v1_isrc_not_supported(self, sample_mp3_file):
        """Test that ISRC is not supported by ID3v1 format when explicitly requesting ID3v1."""
        with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError):
            get_unified_metadata_field(sample_mp3_file, UnifiedMetadataKey.ISRC, metadata_format=MetadataFormat.ID3V1)

    def test_vorbis_max_isrc(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_max_metadata(test_file)
            isrc = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC)
            # Max ISRC set by set_max_metadata is "USXXX9999999" (12 chars, standard format)
            assert isrc == "USXXX9999999"
            assert len(isrc) == 12

    def test_riff_max_isrc(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_max_metadata(test_file)
            isrc = get_unified_metadata_field(test_file, UnifiedMetadataKey.ISRC)
            # Max ISRC set by set_max_metadata is "USXXX9999999" (12 chars, standard format)
            assert isrc == "USXXX9999999"
            assert len(isrc) == 12

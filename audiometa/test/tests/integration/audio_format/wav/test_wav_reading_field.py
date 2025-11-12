import pytest

from audiometa import get_unified_metadata_field
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2.id3v2_header_verifier import ID3v2HeaderVerifier
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestWavReading:
    def test_all_metadata_format_reading_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            ID3v1MetadataSetter.set_metadata(test_file, {"title": "Title ID3v1"})

            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE)
            assert title == "Title ID3v1"

    def test_riff_metadata_reading_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            RIFFMetadataSetter.set_title(test_file, "RIFF Small Title")

            title = get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.RIFF)
            assert title == "RIFF Small Title"

    def test_id3v2_3_metadata_reading_wav(self):
        with temp_file_with_metadata({}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_title(test_file, "ID3v2.3 Long Title That Exceeds RIFF Limits", version="2.3")

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 3, 0)

            title = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0)
            )
            assert title == "ID3v2.3 Long Title That Exceeds RIFF Limits"

    def test_id3v2_4_metadata_reading_wav(self):
        with temp_file_with_metadata({}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2.4 Long Title That Exceeds RIFF Limits"})

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            title = get_unified_metadata_field(
                test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0)
            )
            assert title == "ID3v2.4 Long Title That Exceeds RIFF Limits"

    def test_vorbis_metadata_reading_wav(self):
        with (
            temp_file_with_metadata({}, "wav") as test_file,
            pytest.raises(MetadataFormatNotSupportedByAudioFormatError),
        ):
            get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE, metadata_format=MetadataFormat.VORBIS)

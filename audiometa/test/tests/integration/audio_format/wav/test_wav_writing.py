import pytest

from audiometa import update_metadata
from audiometa.exceptions import MetadataFormatNotSupportedByAudioFormatError
from audiometa.test.helpers.id3v2.id3v2_header_verifier import ID3v2HeaderVerifier
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestWavWriting:
    def test_writing_default_format_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title Default"}
            update_metadata(test_file, metadata)

            title = RIFFMetadataGetter.get_title(test_file)
            assert title == "Test Title Default"

    def test_riff_metadata_writing_wav(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title RIFF"}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.RIFF)

            title = RIFFMetadataGetter.get_title(test_file)
            assert title == "Test Title RIFF"

    def test_id3v2_3_metadata_writing_wav(self):
        with temp_file_with_metadata({}, "id3v2.3") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.3"}
            update_metadata(
                test_file, unified_metadata=metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0)
            )

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 3, 0)

            title = ID3v2MetadataGetter.get_title(test_file)
            assert title == "Test Title ID3v2.3"

    def test_id3v2_4_metadata_writing_wav(self):
        with temp_file_with_metadata({}, "id3v2.4") as test_file:
            metadata = {UnifiedMetadataKey.TITLE: "Test Title ID3v2.4"}
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))

            assert ID3v2HeaderVerifier.get_id3v2_version(test_file) == (2, 4, 0)

            title = ID3v2MetadataGetter.get_title(test_file)
            assert title == "Test Title ID3v2.4"

    def test_vorbis_metadata_writing_wav(self):
        with (
            temp_file_with_metadata({}, "wav") as test_file,
            pytest.raises(MetadataFormatNotSupportedByAudioFormatError),
        ):
            update_metadata(
                test_file,
                {UnifiedMetadataKey.TITLE: "Test Title Vorbis"},
                metadata_format=MetadataFormat.VORBIS,
            )

import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestDiscNumberReading:
    def test_id3v2_with_total(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"disc_number": "1/2"})
            disc_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER)
            disc_total = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL)
            assert disc_number == 1
            assert disc_total == 2

    def test_id3v2_without_total(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"disc_number": "1"})
            disc_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER)
            disc_total = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL)
            assert disc_number == 1
            assert disc_total is None

    def test_id3v2_max_value(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_metadata(test_file, {"disc_number": "99/99"})
            disc_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER)
            disc_total = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL)
            assert disc_number == 99
            assert disc_total == 99

    def test_vorbis_with_total(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_metadata(test_file, {"disc_number": "1", "disc_total": "2"})
            disc_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER)
            disc_total = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL)
            assert disc_number == 1
            assert disc_total == 2

    def test_vorbis_without_total(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_metadata(test_file, {"disc_number": "2"})
            disc_number = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_NUMBER)
            disc_total = get_unified_metadata_field(test_file, UnifiedMetadataKey.DISC_TOTAL)
            assert disc_number == 2
            assert disc_total is None

    def test_id3v1_not_supported(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
        from audiometa.utils.metadata_format import MetadataFormat

        with temp_file_with_metadata({}, "id3v1") as test_file:
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.DISC_NUMBER metadata not supported by ID3v1 format",
            ):
                get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.DISC_NUMBER, metadata_format=MetadataFormat.ID3V1
                )

            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.DISC_TOTAL metadata not supported by ID3v1 format",
            ):
                get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.DISC_TOTAL, metadata_format=MetadataFormat.ID3V1
                )

    def test_riff_not_supported(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
        from audiometa.utils.metadata_format import MetadataFormat

        with temp_file_with_metadata({}, "wav") as test_file:
            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.DISC_NUMBER metadata not supported by RIFF format",
            ):
                get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.DISC_NUMBER, metadata_format=MetadataFormat.RIFF
                )

            with pytest.raises(
                MetadataFieldNotSupportedByMetadataFormatError,
                match="UnifiedMetadataKey.DISC_TOTAL metadata not supported by RIFF format",
            ):
                get_unified_metadata_field(
                    test_file, UnifiedMetadataKey.DISC_TOTAL, metadata_format=MetadataFormat.RIFF
                )

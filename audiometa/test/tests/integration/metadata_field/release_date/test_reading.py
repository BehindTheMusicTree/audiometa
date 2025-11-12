import pytest

from audiometa import get_unified_metadata_field
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestReleaseDateReading:
    def test_id3v1(self):
        with temp_file_with_metadata({"title": "Test Song"}, "id3v1") as test_file:
            ID3v1MetadataSetter.set_max_metadata(test_file)

            release_date = get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == "9999"

    def test_id3v2_3(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_release_date(test_file, "9999-12-31", version="2.3")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TDAT"] == ["3112"]
            assert raw_metadata["TYER"] == ["9999"]

            release_date = get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == "9999-12-31"

    def test_id3v2_4(self):
        with temp_file_with_metadata({"title": "Test Song"}, "mp3") as test_file:
            ID3v2MetadataSetter.set_release_date(test_file, "9999-12-31", version="2.4")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata["TDRC"] == ["9999-12-31"]

            release_date = get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == "9999-12-31"

    def test_vorbis(self):
        with temp_file_with_metadata({"title": "Test Song"}, "flac") as test_file:
            VorbisMetadataSetter.set_release_date(test_file, "9999-12-31")
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file)
            assert "DATE=9999-12-31" in raw_metadata

            release_date = get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == "9999-12-31"

    def test_riff(self):
        with temp_file_with_metadata({"title": "Test Song"}, "wav") as test_file:
            RIFFMetadataSetter.set_release_date(test_file, "9999-12-31")
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:date=9999-12-31" in raw_metadata

            release_date = get_unified_metadata_field(test_file, UnifiedMetadataKey.RELEASE_DATE)
            assert release_date == "9999-12-31"

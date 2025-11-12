import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestGenreWriting:
    def test_id3v1(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_genre = "Rock"
            test_metadata = {UnifiedMetadataKey.GENRES_NAMES: [test_genre]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V1)

            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file)
            assert raw_metadata["genre"] == 17

    def test_id3v2_3(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_genre = "Test Genre ID3v2"
            test_metadata = {UnifiedMetadataKey.GENRES_NAMES: [test_genre]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.3")
            assert raw_metadata["TCON"] == [test_genre]

    def test_id3v2_4(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            test_genre = "Test Genre ID3v2"
            test_metadata = {UnifiedMetadataKey.GENRES_NAMES: [test_genre]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))

            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file, version="2.4")
            assert raw_metadata["TCON"] == [test_genre]

    def test_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            test_genre = "Rock"
            test_metadata = {UnifiedMetadataKey.GENRES_NAMES: [test_genre]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.RIFF)

            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "TAG:genre=Rock" in raw_metadata

    def test_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            test_genre = "Test Genre Vorbis"
            test_metadata = {UnifiedMetadataKey.GENRES_NAMES: [test_genre]}
            update_metadata(test_file, test_metadata, metadata_format=MetadataFormat.VORBIS)
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.GENRES_NAMES) == [test_genre]

    def test_invalid_type_raises(self):
        from audiometa.exceptions import InvalidMetadataFieldTypeError

        with temp_file_with_metadata({}, "mp3") as test_file:
            bad_metadata = {UnifiedMetadataKey.GENRES_NAMES: 123}
            with pytest.raises(InvalidMetadataFieldTypeError):
                update_metadata(test_file, bad_metadata)


from audiometa import update_metadata
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


class TestMultipleValuesDuplicateValues:
    def test_write_duplicate_values(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            duplicate_values = ["Artist One", "Artist Two", "Artist One", "Artist Three", "Artist Two"]
            metadata = {
                UnifiedMetadataKey.ARTISTS: duplicate_values
            }
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.VORBIS)
            
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file.path)
            assert "ARTIST=Artist One" in raw_metadata
            assert "ARTIST=Artist Two" in raw_metadata
            assert "ARTIST=Artist Three" in raw_metadata
        
        
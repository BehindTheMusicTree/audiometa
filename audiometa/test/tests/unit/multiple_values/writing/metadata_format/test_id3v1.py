from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
from audiometa.test.helpers.id3v1.id3v1_metadata_setter import ID3v1MetadataSetter


class TestMultipleValuesId3v1:
    def test_id3v1_artists_concatenation_default_comma(self):
        initial_metadata = {"title": "Test Song"}
        with TempFileWithMetadata(initial_metadata, "mp3") as test_file:
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2"]
            }
            
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V1)
            
            # Use helper to check the created ID3v1 artist field directly
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file.path)
            artists = raw_metadata.get("artist", "")
            assert "Artist 1,Artist 2" in artists or "Artist 2,Artist 1" in artists
            
    
    def test_with_existing_artists_field(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v1MetadataSetter.set_artist(test_file.path, "Existing 1; Existing 2")
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file.path)
            assert "Existing 1; Existing 2" in raw_metadata.get("artist", "")
            
            # Now update with multiple artists
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Existing 1", "New 2"]
            }
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V1)
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file.path)
            artists = raw_metadata.get("artist", "")
            assert "Existing 1" in artists
            assert "New 2" in artists
            assert "Existing 2" not in artists
    
    def test_id3v1_separator_priority(self):
        # Each test case: values, expected separator
        test_cases = [
            (['A1', 'A2', 'A3'], ','),
            (['A,1', 'A2', 'A3'], ';'),
            (['A,1', 'A;2', 'A3'], '|'),
            (['A,1', 'A;2', 'A|3'], '·'),
            (['A,1', 'A;2', 'A|3', 'A·4'], '/'),
            (['A,1', 'A;2', 'A|3', 'A·4', 'A/5'], ','),
        ]
        for values, expected_sep in test_cases:
            initial_metadata = {"title": "Test Song"}
            with TempFileWithMetadata(initial_metadata, "mp3") as test_file:
                metadata = {
                    UnifiedMetadataKey.ARTISTS: values
                }
                update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V1)
                raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file.path)
                artists = raw_metadata.get("artist", "")
                
                # Check that the expected separator is used
                assert expected_sep in artists
                # Check that all values are present as substrings
                for v in values:
                    assert v in artists
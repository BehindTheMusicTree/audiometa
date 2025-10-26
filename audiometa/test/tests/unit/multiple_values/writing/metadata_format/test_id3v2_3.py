
from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter


class TestMultipleValuesId3v2_3:
        
    def test_artists_concatenation(self):
        initial_metadata = {"title": "Test Song"}
        with TempFileWithMetadata(initial_metadata, "id3v2.3") as test_file:
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Artist 1", "Artist 2", "Artist 3"]
            }
            
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.3')
            assert ["Artist 1//Artist 2//Artist 3"] == raw_metadata['TPE1']
    
    def test_with_existing_artists_field(self):
        # Start with an existing artist field
        initial_metadata = {"artist": "Existing Artist"}
        with TempFileWithMetadata(initial_metadata, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_artists(test_file.path, "Existing 1; Existing 2", version="2.3")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.3')
            assert ["Existing 1; Existing 2"] == raw_metadata['TPE1']

            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Existing 1", "New 2"]
            }
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.3')

            assert ["Existing 1//New 2"] == raw_metadata['TPE1']

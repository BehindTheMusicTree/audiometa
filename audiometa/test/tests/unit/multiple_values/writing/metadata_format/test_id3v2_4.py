from pathlib import Path

from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter


class TestMultipleValuesId3v2_4:
    def test_write_multiple_artists(self):
        with TempFileWithMetadata({"title": "Test Song"}, "id3v2.4") as test_file:
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Artist One", "Artist Two"]
            }
            
            update_metadata(test_file, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.4')
            
            assert ["Artist One\x00Artist Two"] == raw_metadata['TPE1']

    def test_write_on_existing_artists_field(self):
        with TempFileWithMetadata({}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_artists(test_file.path,["Existing A\x00Existing B"], version="2.4")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.4')
            
            assert ["Existing A\x00Existing B"] == raw_metadata['TPE1']
            
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Existing A", "New B"]
            }
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.4')
            assert ["Existing A\x00New B"] == raw_metadata['TPE1']
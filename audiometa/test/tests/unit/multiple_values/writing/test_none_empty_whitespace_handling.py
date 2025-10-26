
from audiometa import update_metadata, get_unified_metadata, get_unified_metadata_field
from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


class TestNoneEmptyWhitespaceHandling:
    def test_none_removes_fields(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # First write some metadata
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Artist One", "Artist Two"]
            }
            update_metadata(test_file.path, metadata)
            
            # Verify it was written
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists is not None
            
            # Now write None (should remove the field)
            metadata = {
                UnifiedMetadataKey.ARTISTS: None
            }
            update_metadata(test_file.path, metadata)
            
            # Verify field was removed
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists is None
        
    def test_write_empty_list_removes_field(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # First write some metadata
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["Artist One", "Artist Two"]
            }
            update_metadata(test_file.path, metadata)
            
            # Verify it was written
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists is not None
            
            # Now write empty list (should remove the field)
            metadata = {
                UnifiedMetadataKey.ARTISTS: []
            }
            update_metadata(test_file.path, metadata)
            
            # Verify field was removed
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists is None

    def test_write_empty_strings_in_list(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # Write list with empty strings
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["", "Valid Artist", ""]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            
            # Should filter out empty strings
            assert isinstance(artists, list)
            assert len(artists) == 1
            assert "Valid Artist" in artists

    def test_write_whitespace_only_strings(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
        # Write list with whitespace-only strings
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["   ", "Valid Artist", "\t\n"]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            
            # Should filter out whitespace-only strings
            assert isinstance(artists, list)
            assert len(artists) == 1
            assert "Valid Artist" in artists
            
    def test_write_mixed_empty_and_valid_entries(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # Write list with mix of empty, whitespace, and valid entries
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["", "   ", "Valid Artist 1", "\t", "Valid Artist 2", "\n"]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            
            # Should filter out empty and whitespace-only strings
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Valid Artist 1" in artists
            assert "Valid Artist 2" in artists
            
    def test_write_mixed_empty_and_valid_entries_id3v1(self):
        with TempFileWithMetadata({"title": "Test Song"}, "mp3") as test_file:
            # Write list with mix of empty, whitespace, and valid entries
            # Use shorter names to fit within ID3v1's 30-character limit
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["", "   ", "Artist1", "\t", "Artist2", "\n"]
            }
            update_metadata(test_file.path, metadata, metadata_format=MetadataFormat.ID3V1)
            
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file.path)
            assert "Artist1" in raw_metadata.get("artist", "")
            assert "Artist2" in raw_metadata.get("artist", "")
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS, metadata_format=MetadataFormat.ID3V1)
            
            # Should filter out empty and whitespace-only strings
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Artist1" in artists
            assert "Artist2" in artists

    def test_write_all_empty_strings_removes_field(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["", "   ", "\t\n"]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            
            assert artists == None

    def test_write_single_empty_string_removes_field(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # Write single empty string
            metadata = {
                UnifiedMetadataKey.ARTISTS: [""]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            
            # Should remove the field entirely (None for single empty string)
            assert artists is None

    def test_write_single_whitespace_string_removes_field(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
        # Write single whitespace string
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["   "]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            assert artists is None

    def test_write_trimmed_whitespace_preserved(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # Write strings with leading/trailing whitespace that should be preserved
            metadata = {
                UnifiedMetadataKey.ARTISTS: ["  Artist with spaces  ", "Another Artist"]
            }
            update_metadata(test_file.path, metadata)
            
            artists = get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS)
            
            # Whitespace is trimmed by the implementation
            assert isinstance(artists, list)
            assert len(artists) == 2
            assert "Artist with spaces" in artists
            assert "Another Artist" in artists

    def test_write_empty_metadata_dict(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # Write empty metadata dictionary
            metadata = {}
            update_metadata(test_file.path, metadata)
            
            # Should not raise an error
            unified_metadata = get_unified_metadata(test_file.path)
            assert isinstance(unified_metadata, dict)

    def test_write_metadata_with_all_none_values(self):
        with TempFileWithMetadata({"title": "Test Song"}, "flac") as test_file:
            # Write metadata with all None values
            metadata = {
                UnifiedMetadataKey.TITLE: None,
                UnifiedMetadataKey.ARTISTS: None,
                UnifiedMetadataKey.ALBUM: None
            }   
            update_metadata(test_file.path, metadata)
            
            # Should not raise an error
            unified_metadata = get_unified_metadata(test_file.path)
            assert isinstance(unified_metadata, dict)

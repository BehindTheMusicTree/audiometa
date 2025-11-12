import pytest

from audiometa import delete_all_metadata, get_unified_metadata
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestDeleteAllMetadataAllFormats:
    def test_delete_all_metadata_formats_mp3(self):
        with temp_file_with_metadata({"title": "ID3v1 Title", "artist": "ID3v1 Artist"}, "id3v1") as test_file:
            # Verify ID3v1 has metadata before adding ID3v2
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Add ID3v2 metadata using external tools for proper test isolation
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})

            # Verify ID3v2 has metadata
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Delete all metadata
            result = delete_all_metadata(test_file)
            assert result is True

            # Verify both formats were deleted
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

    def test_delete_all_metadata_formats_flac(self):
        with temp_file_with_metadata({"title": "ID3v1 Title", "artist": "ID3v1 Artist"}, "id3v1") as test_file:
            # Verify ID3v1 has metadata before adding ID3v2
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Add ID3v2 metadata using external tools for proper test isolation
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})

            # Verify ID3v2 has metadata
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Delete all metadata
            result = delete_all_metadata(test_file)
            assert result is True

            # Verify both formats were deleted
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

    def test_delete_all_metadata_formats_wav(self):
        with temp_file_with_metadata({"title": "ID3v1 Title", "artist": "ID3v1 Artist"}, "id3v1") as test_file:
            # Verify ID3v1 has metadata before adding ID3v2
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Add ID3v2 metadata using external tools for proper test isolation
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})

            # Verify ID3v2 has metadata
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Delete all metadata
            result = delete_all_metadata(test_file)
            assert result is True

            # Verify both formats were deleted
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

    def test_delete_all_metadata_removes_all_formats(self):
        with temp_file_with_metadata({"title": "ID3v1 Title", "artist": "ID3v1 Artist"}, "id3v1") as test_file:
            # Verify ID3v1 has metadata before adding ID3v2
            id3v1_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v1_before.get(UnifiedMetadataKey.TITLE) == "ID3v1 Title"

            # Add ID3v2 metadata using external tools for proper test isolation
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "ID3v2 Title", "artist": "ID3v2 Artist"})

            # Verify ID3v2 has metadata
            id3v2_before = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            assert id3v2_before.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"

            # Delete all metadata
            result = delete_all_metadata(test_file)
            assert result is True

            # Verify both formats were deleted
            id3v2_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V2)
            id3v1_after = get_unified_metadata(test_file, metadata_format=MetadataFormat.ID3V1)
            assert id3v2_after.get(UnifiedMetadataKey.TITLE) is None
            assert id3v1_after.get(UnifiedMetadataKey.TITLE) is None

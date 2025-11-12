"""End-to-end tests for metadata deletion workflows.

These tests verify complete deletion workflows that real users would perform, including full metadata deletion, partial
deletion, and cross-format deletion.
"""

import pytest

from audiometa import delete_all_metadata, get_unified_metadata, update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.e2e
class TestDeletionWorkflows:
    def test_complete_metadata_deletion_workflow_mp3(self):
        # Complete e2e deletion workflow for MP3
        initial_metadata = {
            "title": "Original Title",
            "artist": "Original Artist",
            "album": "Original Album",
            "year": "2023",
            "genre": "Rock",
            "comment": "Original comment",
        }

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Original Title"
            assert initial_metadata_result.get(UnifiedMetadataKey.ARTISTS) == ["Original Artist"]
            assert initial_metadata_result.get(UnifiedMetadataKey.ALBUM) == "Original Album"

            # 2. Add more metadata using app's function
            additional_metadata = {
                UnifiedMetadataKey.RATING: 80,
                UnifiedMetadataKey.BPM: 120,
                UnifiedMetadataKey.COMMENT: "Updated comment",
            }
            update_metadata(test_file, additional_metadata, normalized_rating_max_value=100)

            # 3. Verify metadata was added
            updated_metadata = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert updated_metadata.get(UnifiedMetadataKey.RATING) == 80
            assert updated_metadata.get(UnifiedMetadataKey.BPM) == 120

            # 4. Delete all metadata
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 5. Verify all metadata was deleted
            deleted_metadata = get_unified_metadata(test_file)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Original Title"
            )
            assert deleted_metadata.get(UnifiedMetadataKey.ARTISTS) is None or deleted_metadata.get(
                UnifiedMetadataKey.ARTISTS
            ) != ["Original Artist"]
            assert (
                deleted_metadata.get(UnifiedMetadataKey.ALBUM) is None
                or deleted_metadata.get(UnifiedMetadataKey.ALBUM) != "Original Album"
            )
            assert deleted_metadata.get(UnifiedMetadataKey.RATING) is None
            assert deleted_metadata.get(UnifiedMetadataKey.BPM) is None

    def test_complete_metadata_deletion_workflow_flac(self):
        # Complete e2e deletion workflow for FLAC
        initial_metadata = {
            "title": "FLAC Original Title",
            "artist": "FLAC Original Artist",
            "album": "FLAC Original Album",
        }

        with temp_file_with_metadata(initial_metadata, "flac") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "FLAC Original Title"

            # 2. Add more metadata
            additional_metadata = {
                UnifiedMetadataKey.RATING: 90,
                UnifiedMetadataKey.BPM: 140,
                UnifiedMetadataKey.COMMENT: "FLAC comment",
            }
            update_metadata(test_file, additional_metadata, normalized_rating_max_value=100)

            # 3. Delete all metadata
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 4. Verify all metadata was deleted
            deleted_metadata = get_unified_metadata(test_file)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "FLAC Original Title"
            )
            assert deleted_metadata.get(UnifiedMetadataKey.RATING) is None

    def test_complete_metadata_deletion_workflow_wav(self):
        # Complete e2e deletion workflow for WAV
        initial_metadata = {
            "title": "WAV Original Title",
            "artist": "WAV Original Artist",
            "album": "WAV Original Album",
        }

        with temp_file_with_metadata(initial_metadata, "wav") as test_file:
            # 1. Verify initial metadata exists
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "WAV Original Title"

            # 2. Add more metadata (WAV doesn't support rating/BPM)
            additional_metadata = {UnifiedMetadataKey.COMMENT: "WAV comment"}
            update_metadata(test_file, additional_metadata)

            # 3. Delete all metadata
            delete_result = delete_all_metadata(test_file)
            assert delete_result is True

            # 4. Verify all metadata was deleted
            deleted_metadata = get_unified_metadata(test_file)
            assert (
                deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "WAV Original Title"
            )

    def test_partial_metadata_deletion_workflow(self):
        # E2e test for deleting specific metadata fields
        initial_metadata = {
            "title": "Partial Deletion Title",
            "artist": "Partial Deletion Artist",
            "album": "Partial Deletion Album",
            "year": "2023",
            "genre": "Jazz",
        }

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Verify initial metadata
            initial_metadata_result = get_unified_metadata(test_file)
            assert initial_metadata_result.get(UnifiedMetadataKey.TITLE) == "Partial Deletion Title"
            assert initial_metadata_result.get(UnifiedMetadataKey.ARTISTS) == ["Partial Deletion Artist"]
            assert initial_metadata_result.get(UnifiedMetadataKey.ALBUM) == "Partial Deletion Album"

            # 2. Delete specific fields by setting them to None
            deletion_metadata = {UnifiedMetadataKey.TITLE: None, UnifiedMetadataKey.ARTISTS: None}
            update_metadata(test_file, deletion_metadata)

            # 3. Verify specific fields were deleted while others remain
            updated_metadata = get_unified_metadata(test_file)
            assert updated_metadata.get(UnifiedMetadataKey.TITLE) is None
            assert updated_metadata.get(UnifiedMetadataKey.ARTISTS) is None
            assert updated_metadata.get(UnifiedMetadataKey.ALBUM) == "Partial Deletion Album"  # Should remain

            # 4. Delete remaining metadata
            remaining_deletion = {
                UnifiedMetadataKey.ALBUM: None,
                UnifiedMetadataKey.RELEASE_DATE: None,
                UnifiedMetadataKey.GENRES_NAMES: None,
            }
            update_metadata(test_file, remaining_deletion)

            # 5. Verify all metadata is now deleted
            final_metadata = get_unified_metadata(test_file)
            assert final_metadata.get(UnifiedMetadataKey.ALBUM) is None
            assert final_metadata.get(UnifiedMetadataKey.RELEASE_DATE) is None
            assert final_metadata.get(UnifiedMetadataKey.GENRES_NAMES) is None

    def test_cross_format_deletion_consistency(self, sample_mp3_file, sample_flac_file, sample_wav_file):
        # E2e test for deletion consistency across formats
        test_metadata = {
            UnifiedMetadataKey.TITLE: "Cross Format Deletion Test",
            UnifiedMetadataKey.ARTISTS: ["Test Artist"],
            UnifiedMetadataKey.ALBUM: "Test Album",
        }

        sample_files = [(sample_mp3_file, "mp3"), (sample_flac_file, "flac"), (sample_wav_file, "wav")]

        for _file_path, format_type in sample_files:
            # Set up metadata using external script
            initial_metadata = {"title": "Original Title", "artist": "Original Artist"}
            with temp_file_with_metadata(initial_metadata, format_type) as test_file:
                # Add metadata using app's function
                update_metadata(test_file, test_metadata)

                # Verify metadata was added
                added_metadata = get_unified_metadata(test_file)
                assert added_metadata.get(UnifiedMetadataKey.TITLE) == "Cross Format Deletion Test"

                # Delete all metadata
                delete_result = delete_all_metadata(test_file)
                assert delete_result is True

                # Verify metadata was deleted consistently across formats
                deleted_metadata = get_unified_metadata(test_file)
                assert (
                    deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                    or deleted_metadata.get(UnifiedMetadataKey.TITLE) != "Cross Format Deletion Test"
                )

    def test_format_specific_deletion_workflow(self):
        # E2e test for deleting specific metadata formats
        initial_metadata = {"title": "Format Specific Deletion", "artist": "Format Specific Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Add metadata in different formats
            id3v2_metadata = {UnifiedMetadataKey.TITLE: "ID3v2 Title", UnifiedMetadataKey.ARTISTS: ["ID3v2 Artist"]}
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            id3v1_metadata = {UnifiedMetadataKey.ALBUM: "ID3v1 Album"}
            update_metadata(test_file, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # 2. Verify both formats have metadata
            combined_metadata = get_unified_metadata(test_file)
            assert combined_metadata.get(UnifiedMetadataKey.TITLE) == "ID3v2 Title"
            assert combined_metadata.get(UnifiedMetadataKey.ALBUM) == "ID3v1 Album"

            # 3. Delete only ID3v2 metadata
            id3v2_deletion = {UnifiedMetadataKey.TITLE: None, UnifiedMetadataKey.ARTISTS: None}
            update_metadata(test_file, id3v2_deletion, metadata_format=MetadataFormat.ID3V2)

            # 4. Verify ID3v2 metadata is deleted but ID3v1 remains
            after_id3v2_deletion = get_unified_metadata(test_file)
            assert (
                after_id3v2_deletion.get(UnifiedMetadataKey.TITLE) is None
                or after_id3v2_deletion.get(UnifiedMetadataKey.TITLE) != "ID3v2 Title"
            )
            assert after_id3v2_deletion.get(UnifiedMetadataKey.ALBUM) == "ID3v1 Album"  # Should remain

            # 5. Delete ID3v1 metadata
            id3v1_deletion = {UnifiedMetadataKey.ALBUM: None}
            update_metadata(test_file, id3v1_deletion, metadata_format=MetadataFormat.ID3V1)

            # 6. Verify all metadata is now deleted
            final_metadata = get_unified_metadata(test_file)
            assert final_metadata.get(UnifiedMetadataKey.ALBUM) is None

    def test_deletion_error_handling_workflow(self):
        # E2e test for deletion error scenarios
        # Create a file with unsupported extension
        with temp_file_with_metadata({}, "mp3") as temp_audio_file_path:
            test_file = temp_audio_file_path.with_suffix(".txt")
            test_file.write_bytes(b"fake audio content")

            # All deletion operations should raise appropriate errors
            from audiometa.exceptions import FileTypeNotSupportedError

            with pytest.raises(FileTypeNotSupportedError):
                delete_all_metadata(str(test_file))

            with pytest.raises(FileTypeNotSupportedError):
                update_metadata(str(test_file), {UnifiedMetadataKey.TITLE: None})

    def test_deletion_with_rating_normalization_workflow(self):
        # E2e test for deletion with rating normalization
        initial_metadata = {"title": "Rating Deletion Test", "artist": "Rating Artist"}

        with temp_file_with_metadata(initial_metadata, "mp3") as test_file:
            # 1. Add rating with normalization
            rating_metadata = {UnifiedMetadataKey.RATING: 80}
            update_metadata(test_file, rating_metadata, normalized_rating_max_value=100)

            # 2. Verify rating was added
            metadata_with_rating = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert metadata_with_rating.get(UnifiedMetadataKey.RATING) == 80

            # 3. Delete rating
            rating_deletion = {UnifiedMetadataKey.RATING: None}
            update_metadata(test_file, rating_deletion, normalized_rating_max_value=100)

            # 4. Verify rating was deleted
            metadata_after_deletion = get_unified_metadata(test_file, normalized_rating_max_value=100)
            assert metadata_after_deletion.get(UnifiedMetadataKey.RATING) is None

    def test_batch_deletion_workflow(self, sample_mp3_file, sample_flac_file, sample_wav_file):
        # E2e test for batch deletion operations
        sample_files = [(sample_mp3_file, "mp3"), (sample_flac_file, "flac"), (sample_wav_file, "wav")]

        results = []

        for _file_path, format_type in sample_files:
            try:
                # Set up metadata using external script
                initial_metadata = {"title": f"Batch Deletion Test {format_type.upper()}", "artist": "Batch Artist"}
                with temp_file_with_metadata(initial_metadata, format_type) as test_file:
                    # Add more metadata using app's function
                    additional_metadata = {
                        UnifiedMetadataKey.ALBUM: f"Batch Album {format_type.upper()}",
                        UnifiedMetadataKey.COMMENT: f"Batch comment for {format_type}",
                    }
                    update_metadata(test_file, additional_metadata)

                    # Verify metadata was added
                    added_metadata = get_unified_metadata(test_file)
                    assert added_metadata.get(UnifiedMetadataKey.TITLE) == f"Batch Deletion Test {format_type.upper()}"

                    # Delete all metadata
                    delete_result = delete_all_metadata(test_file)
                    assert delete_result is True

                    # Verify deletion worked
                    deleted_metadata = get_unified_metadata(test_file)
                    assert (
                        deleted_metadata.get(UnifiedMetadataKey.TITLE) is None
                        or deleted_metadata.get(UnifiedMetadataKey.TITLE)
                        != f"Batch Deletion Test {format_type.upper()}"
                    )

                    results.append(("success", format_type))

            except Exception as e:
                results.append(("error", format_type, str(e)))

        # Verify all files were processed successfully
        assert len(results) == len(sample_files)
        success_count = sum(1 for result in results if result[0] == "success")
        assert success_count == len(sample_files)  # All should succeed

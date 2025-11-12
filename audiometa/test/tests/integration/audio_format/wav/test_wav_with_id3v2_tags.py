import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestWavWithId3v2Tags:
    """Test WAV files that have ID3v2 tags, which are placed at the beginning of the file."""

    def test_wav_with_id3v2_tags_audiofile_instantiation(self):
        # Create a WAV file and add ID3v2 metadata (which places ID3v2 tags at the start)
        with temp_file_with_metadata({}, "wav") as test_file:
            # Write ID3v2 metadata to create the problematic file structure
            id3v2_metadata = {UnifiedMetadataKey.TITLE: "ID3v2 Title"}
            update_metadata(test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            # The key test: _AudioFile instantiation should not fail
            from audiometa._audio_file import _AudioFile

            audio_file = _AudioFile(test_file)  # Should not raise FileCorruptedError

            # Verify the file is properly recognized as a WAV
            assert audio_file.file_extension == ".wav"
            assert audio_file.get_audio_format_name() == "WAV"

    def test_wav_with_id3v2_tags_validation_and_reading(self):
        # Create a WAV file with some initial RIFF metadata
        with temp_file_with_metadata(
            {"title": "Original RIFF Title", "artist": "Original RIFF Artist"}, "wav"
        ) as test_file:
            # Verify initial RIFF metadata
            initial_metadata = get_unified_metadata(test_file)
            assert initial_metadata.get(UnifiedMetadataKey.TITLE) == "Original RIFF Title"
            assert initial_metadata.get(UnifiedMetadataKey.ARTISTS) == ["Original RIFF Artist"]

            # Now write metadata using SYNC strategy (writes to all formats including ID3v2)
            # This will add ID3v2 tags at the beginning of the file while preserving RIFF
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Sync Title",
                UnifiedMetadataKey.ARTISTS: ["Sync Artist"],
                UnifiedMetadataKey.ALBUM: "Sync Album",
            }
            update_metadata(test_file, sync_metadata)

            # Verify that the file can still be validated (_AudioFile creation doesn't fail)
            # and that metadata can be read
            final_metadata = get_unified_metadata(test_file)
            assert final_metadata.get(UnifiedMetadataKey.TITLE) == "Sync Title"
            assert final_metadata.get(UnifiedMetadataKey.ARTISTS) == ["Sync Artist"]
            assert final_metadata.get(UnifiedMetadataKey.ALBUM) == "Sync Album"

            # Verify both ID3v2 and RIFF metadata exist
            id3v2_title = ID3v2MetadataGetter.get_title(test_file)
            riff_title = RIFFMetadataGetter.get_title(test_file)
            assert id3v2_title == "Sync Title"
            assert riff_title == "Sync Title"

    def test_wav_sync_strategy_with_id3v2_and_riff(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            # Use SYNC strategy (default) to write to all supported formats
            sync_metadata = {
                UnifiedMetadataKey.TITLE: "Sync Title",
                UnifiedMetadataKey.ARTISTS: ["Sync Artist"],
                UnifiedMetadataKey.ALBUM: "Sync Album",
            }
            update_metadata(test_file, sync_metadata)

            # File should be valid and readable
            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Sync Title"
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Sync Artist"]
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "Sync Album"

            # Both formats should have the metadata
            id3v2_title = ID3v2MetadataGetter.get_title(test_file)
            riff_title = RIFFMetadataGetter.get_title(test_file)
            assert id3v2_title == "Sync Title"
            assert riff_title == "Sync Title"

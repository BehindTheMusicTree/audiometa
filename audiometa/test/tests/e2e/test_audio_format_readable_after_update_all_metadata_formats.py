"""
End-to-end tests for audio format readability after metadata updates.

These tests verify that audio files remain playable after metadata operations.
"""
import pytest

from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.e2e
class TestAudioFormatReadableAfterUpdate:

    def test_mp3_playable_after_id3v1_and_id3v2_updates(self):
        """Test that MP3 file remains playable after updating with ID3v1 and ID3v2 tags."""
        sf = pytest.importorskip("soundfile")
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Update with ID3v2 metadata first
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Test Album",
                UnifiedMetadataKey.RATING: 85
            }
            update_metadata(test_file.path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100)

            # Update with ID3v1 metadata
            id3v1_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v1 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v1 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v1 Test Album"
            }
            update_metadata(test_file.path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(test_file.path) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file.path} could not be opened or decoded: {e}")

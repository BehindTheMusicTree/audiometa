"""
End-to-end tests for audio format readability after metadata updates.

These tests verify that audio files remain playable after metadata operations.
"""
import pytest

from audiometa import update_metadata
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata


@pytest.mark.integration
class TestAudioFormatReadableAfterUpdate:

    def test_mp3_playable_after_id3v1_and_id3v2_updates(self):
        """Test that MP3 file remains playable after updating with ID3v1 and ID3v2 tags."""
        sf = pytest.importorskip("soundfile")
        
        with temp_file_with_metadata({}, "mp3") as test_file_path:
            # Update with ID3v2 metadata first
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Test Album",
                UnifiedMetadataKey.RATING: 85
            }
            update_metadata(test_file_path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100)

            # Update with ID3v1 metadata
            id3v1_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v1 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v1 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v1 Test Album"
            }
            update_metadata(test_file_path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(test_file_path) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file_path} could not be opened or decoded: {e}")
                
    def test_flac_playable_after_id3v1_id3v2_vorbis_update(self):
        """Test that FLAC file remains playable after updating with ID3v1, ID3v2, and Vorbis comments."""
        sf = pytest.importorskip("soundfile")
        
        with temp_file_with_metadata({}, "flac") as test_file_path:
            # Update with ID3v2 metadata first
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Test Album",
                UnifiedMetadataKey.RATING: 90
            }
            update_metadata(test_file_path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100)

            # Update with ID3v1 metadata
            id3v1_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v1 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v1 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v1 Test Album"
            }
            update_metadata(test_file_path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Finally, update with Vorbis comments
            vorbis_metadata = {
                UnifiedMetadataKey.TITLE: "Vorbis Test Title",
                UnifiedMetadataKey.ARTISTS: ["Vorbis Test Artist"],
                UnifiedMetadataKey.ALBUM: "Vorbis Test Album"
            }
            update_metadata(test_file_path, vorbis_metadata, metadata_format=MetadataFormat.VORBIS)

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(test_file_path) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file_path} could not be opened or decoded: {e}")

    def test_wav_playable_after_id3v1_id3v2_riff_updates(self):
        """Test that WAV file remains playable after updating with ID3v1, ID3v2, and RIFF INFO tags."""
        sf = pytest.importorskip("soundfile")
        
        with temp_file_with_metadata({}, "wav") as test_file_path:
            # Update with ID3v2 metadata first
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Test Album",
                UnifiedMetadataKey.RATING: 75
            }
            update_metadata(test_file_path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100)

            # Update with ID3v1 metadata
            id3v1_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v1 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v1 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v1 Test Album"
            }
            update_metadata(test_file_path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Finally, update with RIFF INFO tags
            riff_metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Test Title",
                UnifiedMetadataKey.ARTISTS: ["RIFF Test Artist"],
                UnifiedMetadataKey.ALBUM: "RIFF Test Album"
            }
            update_metadata(test_file_path, riff_metadata, metadata_format=MetadataFormat.RIFF)

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(test_file_path) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file_path} could not be opened or decoded: {e}")
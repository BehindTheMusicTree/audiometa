import pytest

from audiometa import update_metadata
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestAudioFormatReadableAfterUpdate:
    def test_mp3_playable_after_id3v1_and_id3v2_updates(self):
        """Test that MP3 file remains playable after updating with ID3v1 and ID3v2 tags."""
        sf = pytest.importorskip("soundfile")

        with temp_file_with_metadata({}, "mp3") as test_file:
            # Update with ID3v2 metadata first
            id3v2_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v2 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v2 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v2 Test Album",
                UnifiedMetadataKey.RATING: 80,
            }
            update_metadata(
                test_file, id3v2_metadata, metadata_format=MetadataFormat.ID3V2, normalized_rating_max_value=100
            )

            # Update with ID3v1 metadata
            id3v1_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v1 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v1 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v1 Test Album",
            }
            update_metadata(test_file, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(str(test_file)) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file} could not be opened or decoded: {e}")

    def test_flac_playable_after_vorbis_updates(self):
        """Test that FLAC file remains playable after updating with Vorbis tags."""
        sf = pytest.importorskip("soundfile")

        with temp_file_with_metadata({}, "flac") as test_file:
            # Update with Vorbis metadata
            vorbis_metadata = {
                UnifiedMetadataKey.TITLE: "Vorbis Test Title",
                UnifiedMetadataKey.ARTISTS: ["Vorbis Test Artist"],
                UnifiedMetadataKey.ALBUM: "Vorbis Test Album",
                UnifiedMetadataKey.RATING: 80,
            }
            update_metadata(
                test_file, vorbis_metadata, metadata_format=MetadataFormat.VORBIS, normalized_rating_max_value=100
            )

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(str(test_file)) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file} could not be opened or decoded: {e}")

    def test_wav_playable_after_riff_updates(self):
        """Test that WAV file remains playable after updating with RIFF tags."""
        sf = pytest.importorskip("soundfile")

        with temp_file_with_metadata({}, "wav") as test_file:
            # Update with RIFF metadata
            riff_metadata = {
                UnifiedMetadataKey.TITLE: "RIFF Test Title",
                UnifiedMetadataKey.ARTISTS: ["RIFF Test Artist"],
                UnifiedMetadataKey.ALBUM: "RIFF Test Album",
            }
            update_metadata(test_file, riff_metadata, metadata_format=MetadataFormat.RIFF)

            # Verify the track is still playable by trying to read audio frames
            try:
                with sf.SoundFile(str(test_file)) as f:
                    # Just try reading a few frames
                    frames = f.read(frames=1024)
                    assert f.samplerate > 0
                    assert f.channels > 0
                    assert len(frames) > 0
            except RuntimeError as e:
                pytest.fail(f"Audio file {test_file} could not be opened or decoded: {e}")

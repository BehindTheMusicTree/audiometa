"""End-to-end tests using real audio files for writing metadata."""

from pathlib import Path
import shutil

from audiometa import get_unified_metadata, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


class TestRealAudioFilesWriting:
    """Test cases for writing metadata to real audio files."""

    test_metadata = {
        UnifiedMetadataKey.TITLE: "Test Writing Title",
        UnifiedMetadataKey.ARTISTS: ["Test Writing Artist"],
        UnifiedMetadataKey.ALBUM: "Test Writing Album",
        UnifiedMetadataKey.RELEASE_DATE: "2023-01-01",
        UnifiedMetadataKey.TRACK_NUMBER: 1,
        UnifiedMetadataKey.BPM: 120,
    }

    def test_writing_allumerlefeu(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Allumerlefeu_2 matches one with more release groups.mp3."""
        real_file = test_files_dir / "recording=Allumerlefeu_2 matches one with more release groups.mp3"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_celinekin_park(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Celinekin Park - no musicbrainz recording duration.mp3."""
        real_file = test_files_dir / "recording=Celinekin Park - no musicbrainz recording duration.mp3"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_dans_la_legende(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Dans la legende.flac."""
        real_file = test_files_dir / "recording=Dans la legende.flac"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_kemar_france(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Kemar - France.mp3."""
        real_file = test_files_dir / "recording=Kemar - France.mp3"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_tokyo_drift(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Tokyo Drift_no mb recording.mp3."""
        real_file = test_files_dir / "recording=Tokyo Drift_no mb recording.mp3"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_y_do_i_carmina_burana_mp3(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Y do i - Carmina Burana Remix - 7m52.mp3."""
        real_file = test_files_dir / "recording=Y do i - Carmina Burana Remix - 7m52.mp3"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_y_do_i_carmina_burana_wav(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=Y do i - Carmina Burana Remix - 7m52.wav."""
        real_file = test_files_dir / "recording=Y do i - Carmina Burana Remix - 7m52.wav"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_california_gurls(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=california gurls_id3v2 tags.flac."""
        real_file = test_files_dir / "recording=california gurls_id3v2 tags.flac"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_juan_hansen_drown_flac(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=juan hansen oostil - drown (massano remix) - 7m20.flac."""
        real_file = test_files_dir / "recording=juan hansen oostil - drown (massano remix) - 7m20.flac"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_juan_hansen_drown_mp3(self, test_files_dir: Path, temp_audio_file: Path):
        """Test writing metadata to recording=juan hansen oostil - drown (massano remix) - 7m21.mp3."""
        real_file = test_files_dir / "recording=juan hansen oostil - drown (massano remix) - 7m21.mp3"
        shutil.copy2(real_file, temp_audio_file)

        update_metadata(temp_audio_file, self.test_metadata)

        read_back = get_unified_metadata(temp_audio_file)
        assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
        assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
        assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
        assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
        assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == 1
        assert read_back[UnifiedMetadataKey.BPM] == 120
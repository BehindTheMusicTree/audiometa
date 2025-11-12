"""End-to-end tests using real audio files for writing metadata."""

import shutil
import tempfile
from pathlib import Path
from typing import ClassVar

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestRealAudioFilesWriting:
    """Test cases for writing metadata to real audio files."""

    test_metadata: ClassVar = {
        UnifiedMetadataKey.TITLE: "Test Writing Title",
        UnifiedMetadataKey.ARTISTS: ["Test Writing Artist"],
        UnifiedMetadataKey.ALBUM: "Test Writing Album",
        UnifiedMetadataKey.RELEASE_DATE: "2023-01-01",
        UnifiedMetadataKey.TRACK_NUMBER: 1,  # Can write as int, but returns string
        UnifiedMetadataKey.BPM: 120,
    }

    def test_writing_allumerlefeu(self, assets_dir: Path):
        """Test writing metadata to recording=Allumerlefeu_2 matches one with more release groups.mp3."""
        real_file = assets_dir / "recording=Allumerlefeu_2 matches one with more release groups.mp3"
        temp_audio_file_path = Path(tempfile.mktemp(suffix=".mp3"))
        try:
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120
        finally:
            if temp_audio_file_path.exists():
                temp_audio_file_path.unlink()

    def test_writing_celinekin_park(self, assets_dir: Path):
        """Test writing metadata to recording=Celinekin Park - no musicbrainz recording duration.mp3."""
        real_file = assets_dir / "recording=Celinekin Park - no musicbrainz recording duration.mp3"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_dans_la_legende(self, assets_dir: Path):
        """Test writing metadata to recording=Dans la legende.flac."""
        real_file = assets_dir / "recording=Dans la legende.flac"
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_kemar_france(self, assets_dir: Path):
        """Test writing metadata to recording=Kemar - France.mp3."""
        real_file = assets_dir / "recording=Kemar - France.mp3"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_tokyo_drift(self, assets_dir: Path):
        """Test writing metadata to recording=Tokyo Drift_no mb recording.mp3."""
        real_file = assets_dir / "recording=Tokyo Drift_no mb recording.mp3"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_y_do_i_carmina_burana_mp3(self, assets_dir: Path):
        """Test writing metadata to recording=Y do i - Carmina Burana Remix - 7m52.mp3."""
        real_file = assets_dir / "recording=Y do i - Carmina Burana Remix - 7m52.mp3"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_y_do_i_carmina_burana_wav(self, assets_dir: Path):
        """Test writing metadata to recording=Y do i - Carmina Burana Remix - 7m52.wav."""
        real_file = assets_dir / "recording=Y do i - Carmina Burana Remix - 7m52.wav"
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_california_gurls(self, assets_dir: Path):
        """Test writing metadata to recording=california gurls_id3v2 tags.flac."""
        real_file = assets_dir / "recording=california gurls_id3v2 tags.flac"
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_juan_hansen_drown_flac(self, assets_dir: Path):
        """Test writing metadata to recording=juan hansen oostil - drown (massano remix) - 7m20.flac."""
        real_file = assets_dir / "recording=juan hansen oostil - drown (massano remix) - 7m20.flac"
        with tempfile.NamedTemporaryFile(suffix=".flac", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

    def test_writing_juan_hansen_drown_mp3(self, assets_dir: Path):
        """Test writing metadata to recording=juan hansen oostil - drown (massano remix) - 7m21.mp3."""
        real_file = assets_dir / "recording=juan hansen oostil - drown (massano remix) - 7m21.mp3"
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_audio_file_path = Path(temp_file.name)
            shutil.copy2(real_file, temp_audio_file_path)

            update_metadata(temp_audio_file_path, self.test_metadata)

            read_back = get_unified_metadata(temp_audio_file_path)
            assert read_back[UnifiedMetadataKey.TITLE] == "Test Writing Title"
            assert read_back[UnifiedMetadataKey.ARTISTS] == ["Test Writing Artist"]
            assert read_back[UnifiedMetadataKey.ALBUM] == "Test Writing Album"
            assert read_back[UnifiedMetadataKey.RELEASE_DATE] == "2023-01-01"
            assert read_back[UnifiedMetadataKey.TRACK_NUMBER] == "1"
            assert read_back[UnifiedMetadataKey.BPM] == 120

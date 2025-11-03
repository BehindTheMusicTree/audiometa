import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.manager.rating_supporting.RiffManager import RiffManager


@pytest.mark.integration
class TestHeaderInfoWithRealFiles:
    
    def test_header_info_with_different_file_types(self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path):
        # Test MP3
        mp3_audio_file = AudioFile(sample_mp3_file)
        mp3_manager = Id3v2Manager(mp3_audio_file)
        mp3_header = mp3_manager.get_header_info()
        assert isinstance(mp3_header, dict)

        # Test FLAC
        flac_audio_file = AudioFile(sample_flac_file)
        flac_manager = VorbisManager(flac_audio_file)
        flac_header = flac_manager.get_header_info()
        assert isinstance(flac_header, dict)

        # Test WAV
        wav_audio_file = AudioFile(sample_wav_file)
        wav_manager = RiffManager(wav_audio_file)
        wav_header = wav_manager.get_header_info()
        assert isinstance(wav_header, dict)

    def test_raw_metadata_info_with_different_file_types(self, sample_mp3_file: Path, sample_flac_file: Path, sample_wav_file: Path):
        # Test MP3
        mp3_audio_file = AudioFile(sample_mp3_file)
        mp3_manager = Id3v2Manager(mp3_audio_file)
        mp3_raw = mp3_manager.get_raw_metadata_info()
        assert isinstance(mp3_raw, dict)

        # Test FLAC
        flac_audio_file = AudioFile(sample_flac_file)
        flac_manager = VorbisManager(flac_audio_file)
        flac_raw = flac_manager.get_raw_metadata_info()
        assert isinstance(flac_raw, dict)

        # Test WAV
        wav_audio_file = AudioFile(sample_wav_file)
        wav_manager = RiffManager(wav_audio_file)
        wav_raw = wav_manager.get_raw_metadata_info()
        assert isinstance(wav_raw, dict)
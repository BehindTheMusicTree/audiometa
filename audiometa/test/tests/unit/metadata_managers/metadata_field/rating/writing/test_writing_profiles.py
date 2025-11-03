import pytest
from unittest.mock import MagicMock

from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.manager.rating_supporting.RiffManager import RiffManager
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager


@pytest.mark.unit
class TestWritingProfiles:
    
    @pytest.mark.parametrize("normalized_rating, expected_raw_rating", [
        (0, 0),
        (1, 13),
        (2, 1),
        (3, 54),
        (4, 64),
        (5, 118),
        (6, 128),
        (7, 186),
        (8, 196),
        (9, 242),
        (10, 255),
    ])
    def test_base_255_non_proportional(self, normalized_rating, expected_raw_rating):
        id3v2_audio_file = MagicMock()
        id3v2_manager = Id3v2Manager(audio_file=id3v2_audio_file, normalized_rating_max_value=10)
        raw_rating = id3v2_manager._convert_normalized_rating_to_file_rating(normalized_rating=normalized_rating)
        assert raw_rating == expected_raw_rating
        
        wave_audio_file = MagicMock()
        wave_audio_file.file_extension = '.wav'
        riff_manager = RiffManager(audio_file=wave_audio_file, normalized_rating_max_value=10)
        raw_rating = riff_manager._convert_normalized_rating_to_file_rating(normalized_rating=normalized_rating)
        assert raw_rating == expected_raw_rating

    @pytest.mark.parametrize("normalized_rating, expected_raw_rating", [
        (0, 0),
        (1, 10),
        (2, 20),
        (3, 30),
        (4, 40),
        (5, 50),
        (6, 60),
        (7, 70),
        (8, 80),
        (9, 90),
        (10, 100),
    ])
    def test_base_100_proportional(self, normalized_rating, expected_raw_rating):
        flac_audio_file = MagicMock()
        flac_audio_file.file_extension = '.flac'
        vorbis_manager = VorbisManager(audio_file=flac_audio_file, normalized_rating_max_value=10)
        raw_rating = vorbis_manager._convert_normalized_rating_to_file_rating(normalized_rating=normalized_rating)
        assert raw_rating == expected_raw_rating
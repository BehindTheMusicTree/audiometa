from unittest.mock import MagicMock

import pytest

from audiometa.exceptions import ConfigurationError
from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager
from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager
from audiometa.manager._rating_supporting.vorbis._VorbisManager import _VorbisManager as VorbisManager


@pytest.mark.unit
class TestConfigurationError:
    def test_convert_normalized_rating_raises_config_error_when_max_value_none(
        self,
    ):
        id3v2_audio_file = MagicMock()
        id3v2_manager = Id3v2Manager(audio_file=id3v2_audio_file, normalized_rating_max_value=None)

        with pytest.raises(ConfigurationError) as exc_info:
            id3v2_manager._convert_normalized_rating_to_file_rating(normalized_rating=5.0)
        assert "normalized_rating_max_value must be set" in str(exc_info.value)

    def test_convert_normalized_rating_to_file_rating_raises_configuration_error_for_riff_manager(
        self,
    ):
        wave_audio_file = MagicMock()
        wave_audio_file.file_extension = ".wav"
        riff_manager = RiffManager(audio_file=wave_audio_file, normalized_rating_max_value=None)

        with pytest.raises(ConfigurationError) as exc_info:
            riff_manager._convert_normalized_rating_to_file_rating(normalized_rating=5.0)
        assert "normalized_rating_max_value must be set" in str(exc_info.value)

    def test_convert_normalized_rating_to_file_rating_raises_configuration_error_for_vorbis_manager(
        self,
    ):
        flac_audio_file = MagicMock()
        flac_audio_file.file_extension = ".flac"
        vorbis_manager = VorbisManager(audio_file=flac_audio_file, normalized_rating_max_value=None)

        with pytest.raises(ConfigurationError) as exc_info:
            vorbis_manager._convert_normalized_rating_to_file_rating(normalized_rating=5.0)
        assert "normalized_rating_max_value must be set" in str(exc_info.value)

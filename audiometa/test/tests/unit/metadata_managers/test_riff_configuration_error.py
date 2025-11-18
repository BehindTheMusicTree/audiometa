from unittest.mock import MagicMock

import pytest

from audiometa.exceptions import ConfigurationError
from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestRiffManagerConfigurationError:
    def test_update_not_using_mutagen_metadata_raises_configuration_error_when_metadata_keys_direct_map_write_is_none(
        self,
    ):
        wave_audio_file = MagicMock()
        wave_audio_file.file_extension = ".wav"
        riff_manager = RiffManager(audio_file=wave_audio_file, normalized_rating_max_value=10)

        # Manually set metadata_keys_direct_map_write to None to test the error condition
        riff_manager.metadata_keys_direct_map_write = None

        unified_metadata = {UnifiedMetadataKey.TITLE: "Test Title"}

        with pytest.raises(ConfigurationError) as exc_info:
            riff_manager._update_not_using_mutagen_metadata(unified_metadata)
        assert "metadata_keys_direct_map_write must be set" in str(exc_info.value)

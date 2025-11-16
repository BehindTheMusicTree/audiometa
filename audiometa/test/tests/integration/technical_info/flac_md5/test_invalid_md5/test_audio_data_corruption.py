import pytest

from audiometa import is_flac_md5_valid
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_audio_data, ensure_flac_has_md5


@pytest.mark.integration
class TestAudioDataCorruption:
    def test_is_flac_md5_valid_with_audio_data_corruption(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_audio_data(test_file)

            # Audio data corruption should invalidate MD5
            assert not is_flac_md5_valid(test_file), "Audio data corruption should invalidate MD5"

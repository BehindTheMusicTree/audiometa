from unittest.mock import MagicMock

import pytest

from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager
from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager
from audiometa.manager._rating_supporting.vorbis._VorbisManager import _VorbisManager as VorbisManager
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestNormalization:
    @pytest.mark.parametrize(
        ("metadata_rating_read", "expected_normalized_value"),
        [
            (0, 0),
            (13, 1),
            (1, 2),
            (54, 3),
            (64, 4),
            (118, 5),
            (128, 6),
            (186, 7),
            (196, 8),
            (242, 9),
            (255, 10),
        ],
    )
    def test_base_255_non_proportional(self, metadata_rating_read, expected_normalized_value):
        id3v2_audio_file = MagicMock()
        id3v2_manager = Id3v2Manager(audio_file=id3v2_audio_file, normalized_rating_max_value=10)
        id3v2_normalized_rating = id3v2_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={
                Id3v2Manager.Id3TextFrame.RATING: [id3v2_manager.ID3_RATING_APP_EMAIL, metadata_rating_read]
            },
        )
        assert id3v2_normalized_rating == expected_normalized_value

        wave_audio_file = MagicMock()
        wave_audio_file.file_extension = ".wav"
        riff_manager = RiffManager(audio_file=wave_audio_file, normalized_rating_max_value=10)
        riff_normalized_rating = riff_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={RiffManager.RiffTagKey.RATING: [str(metadata_rating_read)]},
        )
        assert riff_normalized_rating == expected_normalized_value

        flac_audio_file = MagicMock()
        flac_audio_file.file_extension = ".flac"
        vorbis_manager = VorbisManager(audio_file=flac_audio_file, normalized_rating_max_value=10)
        vorbis_normalized_rating = vorbis_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={VorbisManager.VorbisKey.RATING: [metadata_rating_read]},
        )
        assert vorbis_normalized_rating == expected_normalized_value

    @pytest.mark.parametrize(
        ("metadata_rating_read", "expected_normalized_value"),
        [
            (0, 0),
            (10, 1),
            (20, 2),
            (30, 3),
            (40, 4),
            (50, 5),
            (60, 6),
            (70, 7),
            (80, 8),
            (90, 9),
            (100, 10),
        ],
    )
    def test_base_100_proportional(self, metadata_rating_read, expected_normalized_value):
        # ID3v2
        id3v2_manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=10)
        id3v2_normalized_rating = id3v2_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={
                Id3v2Manager.Id3TextFrame.RATING: [id3v2_manager.ID3_RATING_APP_EMAIL, metadata_rating_read]
            },
        )
        assert id3v2_normalized_rating == expected_normalized_value

        # RIFF / WAV
        wave_audio_file = MagicMock()
        wave_audio_file.file_extension = ".wav"
        riff_manager = RiffManager(audio_file=wave_audio_file, normalized_rating_max_value=10)
        riff_normalized_rating = riff_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={RiffManager.RiffTagKey.RATING: [str(metadata_rating_read)]},
        )
        assert riff_normalized_rating == expected_normalized_value

        # VORBIS / FLAC
        flac_audio_file = MagicMock()
        flac_audio_file.file_extension = ".flac"
        vorbis_manager = VorbisManager(audio_file=flac_audio_file, normalized_rating_max_value=10)
        vorbis_normalized_rating = vorbis_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={VorbisManager.VorbisKey.RATING: [metadata_rating_read]},
        )
        assert vorbis_normalized_rating == expected_normalized_value

    @pytest.mark.parametrize(
        ("metadata_rating_read", "expected_normalized_value"),
        [
            (51, 1),
            (102, 2),
            (153, 3),
            (204, 4),
            (255, 5),
        ],
    )
    def test_base_255_proportional(self, metadata_rating_read, expected_normalized_value):
        # ID3v2
        id3v2_manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=5)
        id3v2_normalized_rating = id3v2_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={
                Id3v2Manager.Id3TextFrame.RATING: [id3v2_manager.ID3_RATING_APP_EMAIL, metadata_rating_read]
            },
        )
        assert id3v2_normalized_rating == expected_normalized_value

        # RIFF / WAV
        wave_audio_file = MagicMock()
        wave_audio_file.file_extension = ".wav"
        riff_manager = RiffManager(audio_file=wave_audio_file, normalized_rating_max_value=5)
        riff_normalized_rating = riff_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={RiffManager.RiffTagKey.RATING: [str(metadata_rating_read)]},
        )
        assert riff_normalized_rating == expected_normalized_value

        # VORBIS / FLAC
        flac_audio_file = MagicMock()
        flac_audio_file.file_extension = ".flac"
        vorbis_manager = VorbisManager(audio_file=flac_audio_file, normalized_rating_max_value=5)
        vorbis_normalized_rating = vorbis_manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={VorbisManager.VorbisKey.RATING: [metadata_rating_read]},
        )
        assert vorbis_normalized_rating == expected_normalized_value

    def test_invalid_value(self):
        manager = Id3v2Manager(audio_file=MagicMock(), normalized_rating_max_value=10)
        normalized_rating = manager._get_undirectly_mapped_metadata_value_from_raw_clean_metadata(
            unified_metadata_key=UnifiedMetadataKey.RATING,
            raw_clean_metadata_uppercase_keys={Id3v2Manager.Id3TextFrame.RATING: [manager.ID3_RATING_APP_EMAIL, 300]},
        )
        assert normalized_rating is None

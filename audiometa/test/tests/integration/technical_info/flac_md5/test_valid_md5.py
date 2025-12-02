from pathlib import Path

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa.exceptions import FileTypeNotSupportedError


@pytest.mark.integration
class TestValidFlacMd5:
    def test_is_flac_md5_valid_works_with_path_string(self, sample_flac_file: Path):
        state = is_flac_md5_valid(str(sample_flac_file))
        assert isinstance(state, FlacMd5State)
        assert state in [
            FlacMd5State.VALID,
            FlacMd5State.UNSET,
            FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1,
            FlacMd5State.INVALID,
        ]

    def test_is_flac_md5_valid_works_with_pathlib_path(self, sample_flac_file: Path):
        state = is_flac_md5_valid(sample_flac_file)
        assert isinstance(state, FlacMd5State)
        assert state in [
            FlacMd5State.VALID,
            FlacMd5State.UNSET,
            FlacMd5State.UNCHECKABLE_DUE_TO_ID3V1,
            FlacMd5State.INVALID,
        ]

    def test_is_flac_md5_valid_non_flac(self, sample_mp3_file: Path):
        with pytest.raises(FileTypeNotSupportedError):
            is_flac_md5_valid(sample_mp3_file)

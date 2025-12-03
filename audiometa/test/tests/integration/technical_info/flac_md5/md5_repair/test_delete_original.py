"""Test delete_original parameter behavior in get_file_with_corrected_md5."""

from pathlib import Path
from unittest.mock import patch

import pytest

from audiometa import FlacMd5State, is_flac_md5_valid
from audiometa._audio_file import _AudioFile
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import corrupt_md5, ensure_flac_has_md5


@pytest.mark.integration
class TestDeleteOriginalParameter:
    """Test the delete_original parameter in get_file_with_corrected_md5."""

    def test_delete_original_false_preserves_original_file(self):
        """Test that delete_original=False (default) preserves the original file."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "flip_all")

            # Verify initial state
            assert Path(test_file).exists(), "Original file should exist before repair"
            initial_state = is_flac_md5_valid(test_file)
            assert initial_state == FlacMd5State.INVALID, "File should have invalid MD5 needing repair"

            # Repair with delete_original=False (default)
            audio_file = _AudioFile(test_file)
            corrected_file_path = audio_file.get_file_with_corrected_md5(delete_original=False)

            # Verify results
            assert Path(test_file).exists(), "Original file should still exist after repair"
            assert Path(corrected_file_path).exists(), "Corrected file should exist"

            # Verify corrected file has valid MD5
            final_state = is_flac_md5_valid(corrected_file_path)
            assert final_state == FlacMd5State.VALID, "Corrected file should have valid MD5"

    def test_delete_original_true_deletes_original_file(self):
        """Test that delete_original=True deletes the original file."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "flip_all")

            # Verify initial state
            assert Path(test_file).exists(), "Original file should exist before repair"
            initial_state = is_flac_md5_valid(test_file)
            assert initial_state == FlacMd5State.INVALID, "File should have invalid MD5 needing repair"

            # Repair with delete_original=True
            audio_file = _AudioFile(test_file)
            corrected_file_path = audio_file.get_file_with_corrected_md5(delete_original=True)

            # Verify results
            assert not Path(test_file).exists(), "Original file should be deleted after repair"
            assert Path(corrected_file_path).exists(), "Corrected file should exist"

            # Verify corrected file has valid MD5
            final_state = is_flac_md5_valid(corrected_file_path)
            assert final_state == FlacMd5State.VALID, "Corrected file should have valid MD5"

    def test_delete_original_handles_deletion_error(self):
        """Test that OSError is raised when original file deletion fails."""
        with temp_file_with_metadata({}, "flac") as test_file:
            ensure_flac_has_md5(test_file)
            corrupt_md5(test_file, "flip_all")

            # Verify initial state
            assert Path(test_file).exists(), "Original file should exist before repair"

            # Mock Path.unlink to raise OSError
            with patch.object(Path, "unlink") as mock_unlink:
                mock_unlink.side_effect = OSError("Permission denied")

                # Attempt repair with delete_original=True
                audio_file = _AudioFile(test_file)
                with pytest.raises(RuntimeError) as exc_info:
                    audio_file.get_file_with_corrected_md5(delete_original=True)

                assert "Failed to execute FLAC command" in str(exc_info.value)
                assert "Failed to delete original file" in str(exc_info.value)
                assert "Permission denied" in str(exc_info.value)

                # Verify unlink was called (indicating the deletion attempt was made)
                mock_unlink.assert_called_once()

                # Original file should still exist since deletion failed (mocked)
                assert Path(test_file).exists(), "Original file should still exist when deletion fails"

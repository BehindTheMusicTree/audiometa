"""Tests for MD5 validation on FLAC files with ID3 tags.

These tests verify that the library correctly handles FLAC files that have
ID3v2 tags prepended to the file, which is non-standard but occurs in practice.
"""

from pathlib import Path

import pytest

from audiometa._audio_file import _AudioFile
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.tests.integration.technical_info.flac_md5.conftest import ensure_flac_has_md5


def get_md5_position_without_id3_skip() -> int:
    """Get MD5 position assuming file starts with fLaC marker (no ID3 skip).

    This is the NAIVE approach that would fail if ID3v2 tags are prepended.
    """
    # Naive approach: assume fLaC is at position 0
    # MD5 is at: fLaC (4 bytes) + block header (1 byte) + STREAMINFO data before MD5 (18 bytes)
    return 4 + 1 + 18


def get_md5_position_with_id3_skip(file_path: Path) -> int:
    """Get MD5 position by searching for fLaC marker (handles ID3 tags).

    This is the CORRECT approach used by the library.
    """
    with file_path.open("rb") as f:
        data = f.read()
        flac_marker_pos = data.find(b"fLaC")
        if flac_marker_pos == -1:
            msg = "Could not find FLAC marker in file"
            raise RuntimeError(msg)
        return flac_marker_pos + 4 + 1 + 18


def read_md5_at_position(file_path: Path, position: int) -> bytes:
    """Read 16 bytes (MD5) at the given position."""
    with file_path.open("rb") as f:
        f.seek(position)
        return f.read(16)


@pytest.mark.integration
class TestFlacWithId3TagsMd5:
    """Tests verifying that ID3 tag skipping is necessary for correct MD5 reading."""

    def test_naive_approach_fails_with_id3v2_tags(self):
        """Verify that NOT skipping ID3v2 tags causes incorrect MD5 reading.

        This test proves why the library needs to search for the fLaC marker
        rather than assuming it's at the start of the file.
        """
        with temp_file_with_metadata({}, "flac") as test_file:
            # Ensure we have a valid FLAC with MD5
            ensure_flac_has_md5(test_file)

            # Read the correct MD5 position BEFORE adding ID3 tags
            correct_md5_pos = get_md5_position_with_id3_skip(test_file)
            original_md5 = read_md5_at_position(test_file, correct_md5_pos)

            # Verify the file starts with fLaC (no ID3 tags yet)
            with test_file.open("rb") as f:
                assert f.read(4) == b"fLaC", "File should start with fLaC marker before adding ID3"

            # Add ID3v2 tags to the FLAC file
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "Test Title", "artist": "Test Artist"})

            # Verify the file now starts with ID3 (ID3v2 header)
            with test_file.open("rb") as f:
                header = f.read(3)
                assert header == b"ID3", "File should now start with ID3v2 header"

            # The naive approach (assuming fLaC at position 0) reads garbage
            naive_md5_pos = get_md5_position_without_id3_skip()
            naive_md5 = read_md5_at_position(test_file, naive_md5_pos)

            # The correct approach (searching for fLaC) reads the actual MD5
            correct_md5_pos_after = get_md5_position_with_id3_skip(test_file)
            correct_md5_after = read_md5_at_position(test_file, correct_md5_pos_after)

            # The naive approach reads different bytes (inside the ID3 tag data)
            assert naive_md5 != correct_md5_after, (
                "Naive approach should read different bytes than the actual MD5. "
                "If they're equal, the ID3 tag wasn't added or is smaller than expected."
            )

            # The correct approach still reads the same MD5 as before
            assert (
                correct_md5_after == original_md5
            ), "The correct approach should read the same MD5 before and after adding ID3 tags"

    def test_library_correctly_detects_unset_md5_with_id3v2_tags(self):
        """Verify that _is_md5_unset works correctly when ID3v2 tags are present."""
        with temp_file_with_metadata({}, "flac") as test_file:
            # Ensure we have a valid FLAC with MD5
            ensure_flac_has_md5(test_file)

            # Add ID3v2 tags
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "Test Title"})

            # Verify file starts with ID3
            with test_file.open("rb") as f:
                assert f.read(3) == b"ID3"

            # The library should still be able to check if MD5 is unset
            audio_file = _AudioFile(test_file)

            # MD5 should NOT be detected as unset (it has a valid MD5)
            assert (
                audio_file._is_md5_unset() is False
            ), "Library should correctly detect that MD5 is NOT unset, even with ID3v2 tags present"

    def test_library_detects_unset_md5_with_id3v2_tags_when_actually_unset(self):
        """Verify that _is_md5_unset correctly detects unset MD5 when ID3v2 tags are present."""
        with temp_file_with_metadata({}, "flac") as test_file:
            # Ensure we have a valid FLAC with MD5
            ensure_flac_has_md5(test_file)

            # Add ID3v2 tags FIRST
            ID3v2MetadataSetter.set_metadata(test_file, {"title": "Test Title"})

            # Now set MD5 to all zeros (unset) - need to find correct position
            md5_pos = get_md5_position_with_id3_skip(test_file)
            with test_file.open("r+b") as f:
                f.seek(md5_pos)
                f.write(b"\x00" * 16)

            # The library should detect that MD5 is unset
            audio_file = _AudioFile(test_file)
            assert (
                audio_file._is_md5_unset() is True
            ), "Library should correctly detect unset MD5 even with ID3v2 tags present"

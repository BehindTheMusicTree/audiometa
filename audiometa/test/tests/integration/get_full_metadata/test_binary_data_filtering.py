"""Tests for binary data filtering in get_full_metadata function output."""

import pytest

from audiometa import get_full_metadata
from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager


@pytest.mark.integration
class TestGetFullMetadataBinaryDataFiltering:
    """Test that get_full_metadata function properly filters binary data from raw metadata output."""

    def test_get_full_metadata_id3v2_binary_frames_filtered(self, sample_mp3_file):
        """Test that get_full_metadata filters ID3v2 binary frames and replaces with size info."""
        result = get_full_metadata(sample_mp3_file)
        raw_metadata = result.get("raw_metadata", {})
        id3v2_frames = raw_metadata.get("id3v2", {}).get("frames", {})

        # Check that all frames have reasonable text content
        for frame_id, frame_data in id3v2_frames.items():
            text = frame_data.get("text", "")

            # Text should not contain binary data patterns
            assert not any(
                ord(c) < 32 and c not in "\t\n\r" for c in text
            ), f"Frame {frame_id} contains binary data in text: {text[:50]!r}"

            # If it's a binary frame type, should have placeholder text
            binary_frame_types = {
                "APIC:",
                "GEOB:",
                "AENC:",
                "RVA2:",
                "RVRB:",
                "EQU2:",
                "PCNT:",
                "POPM:",
                "RBUF:",
                "LINK:",
                "POSS:",
                "SYLT:",
                "USLT:",
                "SYTC:",
                "ETCO:",
                "MLLT:",
                "OWNE:",
                "COMR:",
                "ENCR:",
                "GRID:",
                "PRIV:",
                "SIGN:",
                "SEEK:",
                "ASPI:",
            }

            if frame_id in binary_frame_types:
                assert text.startswith(
                    "<Binary data:"
                ), f"Binary frame {frame_id} should have placeholder text, got: {text}"
                assert text.endswith(" bytes>"), f"Binary frame {frame_id} should end with ' bytes>', got: {text}"

    def test_id3v2_manager_binary_filtering(self, sample_mp3_file):
        """Test Id3v2Manager directly filters binary frames."""
        from audiometa._audio_file import _AudioFile

        audio_file = _AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        raw_info = manager.get_raw_metadata_info()

        frames = raw_info.get("frames", {})
        binary_frame_types = {
            "APIC:",
            "GEOB:",
            "AENC:",
            "RVA2:",
            "RVRB:",
            "EQU2:",
            "PCNT:",
            "POPM:",
            "RBUF:",
            "LINK:",
            "POSS:",
            "SYLT:",
            "USLT:",
            "SYTC:",
            "ETCO:",
            "MLLT:",
            "OWNE:",
            "COMR:",
            "ENCR:",
            "GRID:",
            "PRIV:",
            "SIGN:",
            "SEEK:",
            "ASPI:",
        }

        for frame_id, frame_data in frames.items():
            text = frame_data.get("text", "")

            if frame_id in binary_frame_types:
                # Binary frames should have placeholder text
                assert text.startswith("<Binary data:"), f"Binary frame {frame_id} should have placeholder text"
                assert text.endswith(" bytes>"), f"Binary frame {frame_id} should end with ' bytes>'"
            else:
                # Text frames should not contain binary data
                assert not any(
                    ord(c) < 32 and c not in "\t\n\r" for c in text
                ), f"Text frame {frame_id} contains binary data: {text[:50]!r}"

    def test_get_full_metadata_vorbis_no_binary_data(self, sample_flac_file):
        """Test that get_full_metadata Vorbis comments don't contain binary data."""
        result = get_full_metadata(sample_flac_file)
        raw_metadata = result.get("raw_metadata", {})
        vorbis_comments = raw_metadata.get("vorbis", {}).get("comments", {})

        # Vorbis comments should only contain text
        for key, values in vorbis_comments.items():
            assert isinstance(values, list), f"Vorbis comment {key} should be a list"
            for value in values:
                assert isinstance(value, str), f"Vorbis comment {key} value should be string"
                # Check for binary data patterns
                assert not any(
                    ord(c) < 32 and c not in "\t\n\r" for c in value
                ), f"Vorbis comment {key} contains binary data: {value[:50]!r}"

    def test_get_full_metadata_riff_no_binary_data(self, sample_wav_file):
        """Test that get_full_metadata RIFF metadata doesn't contain binary data."""
        result = get_full_metadata(sample_wav_file)
        raw_metadata = result.get("raw_metadata", {})
        riff_fields = raw_metadata.get("riff", {}).get("parsed_fields", {})

        # RIFF parsed fields should only contain text
        for key, value in riff_fields.items():
            assert isinstance(value, str), f"RIFF field {key} should be string"
            # Check for binary data patterns
            assert not any(
                ord(c) < 32 and c not in "\t\n\r" for c in value
            ), f"RIFF field {key} contains binary data: {value[:50]!r}"

    def test_get_full_metadata_id3v1_no_binary_data(self, sample_mp3_file):
        """Test that get_full_metadata ID3v1 metadata doesn't contain binary data."""
        result = get_full_metadata(sample_mp3_file)
        raw_metadata = result.get("raw_metadata", {})
        id3v1_fields = raw_metadata.get("id3v1", {}).get("parsed_fields", {})

        # ID3v1 parsed fields should only contain text
        for key, value in id3v1_fields.items():
            assert isinstance(value, str), f"ID3v1 field {key} should be string"
            # Check for binary data patterns
            assert not any(
                ord(c) < 32 and c not in "\t\n\r" for c in value
            ), f"ID3v1 field {key} contains binary data: {value[:50]!r}"

    def test_cli_output_no_binary_data(self, sample_mp3_file):
        """Test that CLI output doesn't contain binary data."""
        import subprocess
        import sys

        # Test JSON output
        result = subprocess.run(
            [sys.executable, "-m", "audiometa", "read", str(sample_mp3_file), "--format", "json"],
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, f"CLI failed: {result.stderr}"

        # Check for binary data patterns in output
        output = result.stdout
        binary_patterns = ["\\xff", "\\x00", "\\x01", "\\x02", "\\x03"]

        for pattern in binary_patterns:
            assert pattern not in output, f"CLI output contains binary pattern {pattern}"

        # Should be valid JSON
        import json

        data = json.loads(output)
        assert isinstance(data, dict)

    def test_binary_frame_size_preserved(self, sample_mp3_file):
        """Test that binary frame sizes are still reported correctly."""
        from audiometa._audio_file import _AudioFile

        audio_file = _AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        raw_info = manager.get_raw_metadata_info()

        frames = raw_info.get("frames", {})
        binary_frame_types = {
            "APIC:",
            "GEOB:",
            "AENC:",
            "RVA2:",
            "RVRB:",
            "EQU2:",
            "PCNT:",
            "POPM:",
            "RBUF:",
            "LINK:",
            "POSS:",
            "SYLT:",
            "USLT:",
            "SYTC:",
            "ETCO:",
            "MLLT:",
            "OWNE:",
            "COMR:",
            "ENCR:",
            "GRID:",
            "PRIV:",
            "SIGN:",
            "SEEK:",
            "ASPI:",
        }

        for frame_id, frame_data in frames.items():
            if frame_id in binary_frame_types:
                size = frame_data.get("size")
                flags = frame_data.get("flags")

                # Size and flags should still be present
                assert isinstance(size, int), f"Binary frame {frame_id} size should be int"
                assert isinstance(flags, int), f"Binary frame {frame_id} flags should be int"

                # Size should be reasonable (not negative)
                assert size >= 0, f"Binary frame {frame_id} size should be non-negative"

    def test_text_frames_unchanged(self, sample_mp3_file):
        """Test that text frames are not affected by binary filtering."""
        from audiometa._audio_file import _AudioFile

        audio_file = _AudioFile(sample_mp3_file)
        manager = Id3v2Manager(audio_file)
        raw_info = manager.get_raw_metadata_info()

        frames = raw_info.get("frames", {})
        text_frame_types = {"TIT2", "TALB", "TPE1", "TDRC", "COMM", "TENC", "TSSE"}

        for frame_id, frame_data in frames.items():
            if any(frame_id.startswith(prefix) for prefix in text_frame_types):
                text = frame_data.get("text", "")

                # Text frames should have actual content, not placeholder
                assert not text.startswith("<Binary data:"), f"Text frame {frame_id} should not have binary placeholder"

                # Should have reasonable content
                assert len(text) > 0, f"Text frame {frame_id} should have content"

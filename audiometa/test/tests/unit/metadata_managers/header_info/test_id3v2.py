from unittest.mock import patch

import pytest

from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager


@pytest.mark.unit
class TestId3v2HeaderMethods:
    @patch("audiometa.manager._rating_supporting.id3v2._Id3v2Manager.ID3")
    def test_id3v2_manager_header_info(self, mock_id3_class, mock_audio_file_mp3, mock_id3_with_metadata):
        mock_id3_class.return_value = mock_id3_with_metadata

        manager = Id3v2Manager(mock_audio_file_mp3)
        header_info = manager.get_header_info()

        assert "present" in header_info
        assert "version" in header_info
        assert "header_size_bytes" in header_info
        assert "flags" in header_info
        assert "extended_header" in header_info

        assert isinstance(header_info["present"], bool)
        assert isinstance(header_info["version"], str)
        assert header_info["version"] == "2.3.0"
        assert isinstance(header_info["header_size_bytes"], int)
        assert isinstance(header_info["flags"], dict)
        assert isinstance(header_info["extended_header"], dict)

    @patch("audiometa.manager._rating_supporting.id3v2._Id3v2Manager.ID3")
    def test_id3v2_manager_header_info_empty(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty

        manager = Id3v2Manager(mock_audio_file_mp3)
        header_info = manager.get_header_info()

        assert "present" in header_info
        assert "version" in header_info
        assert "header_size_bytes" in header_info
        assert "flags" in header_info
        assert "extended_header" in header_info

        assert isinstance(header_info["present"], bool)
        assert isinstance(header_info["version"], str)
        assert isinstance(header_info["header_size_bytes"], int)
        assert isinstance(header_info["flags"], dict)
        assert isinstance(header_info["extended_header"], dict)

    @patch("audiometa.manager._rating_supporting.id3v2._Id3v2Manager.ID3")
    def test_id3v2_manager_raw_metadata_info(self, mock_id3_class, mock_audio_file_mp3, mock_id3_empty):
        mock_id3_class.return_value = mock_id3_empty

        manager = Id3v2Manager(mock_audio_file_mp3)
        raw_info = manager.get_raw_metadata_info()

        assert "raw_data" in raw_info
        assert "parsed_fields" in raw_info
        assert "frames" in raw_info
        assert "comments" in raw_info
        assert "chunk_structure" in raw_info

        assert raw_info["raw_data"] is None or isinstance(raw_info["raw_data"], bytes)
        assert isinstance(raw_info["parsed_fields"], dict)
        assert isinstance(raw_info["frames"], dict)
        assert isinstance(raw_info["comments"], dict)
        assert isinstance(raw_info["chunk_structure"], dict)

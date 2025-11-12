import pytest

from audiometa._audio_file import _AudioFile
from audiometa.manager._rating_supporting.id3v2._Id3v2Manager import _Id3v2Manager as Id3v2Manager
from audiometa.manager._rating_supporting.riff._RiffManager import _RiffManager as RiffManager
from audiometa.manager._rating_supporting.vorbis._VorbisManager import _VorbisManager as VorbisManager
from audiometa.manager.id3v1._Id3v1Manager import _Id3v1Manager as Id3v1Manager
from audiometa.manager.id3v1.id3v1_raw_metadata_key import Id3v1RawMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.unit
class TestMetadataFormatManagersWriteAndRead:
    def test_id3v1_manager_write_and_read(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            audio_file = _AudioFile(test_file)
            manager = Id3v1Manager(audio_file)

            manager.update_metadata(
                {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.ARTISTS: ["Test Artist"]}
            )

            raw_metadata = manager._extract_mutagen_metadata()

            assert raw_metadata.tags.get(Id3v1RawMetadataKey.TITLE) == ["Test Title"]
            assert raw_metadata.tags.get(Id3v1RawMetadataKey.ARTISTS_NAMES_STR) == ["Test Artist"]

    def test_id3v2_manager_write_and_read(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            audio_file = _AudioFile(test_file)
            manager = Id3v2Manager(audio_file)

            manager.update_metadata(
                {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.ARTISTS: ["Test Artist"]}
            )

            raw_metadata = manager._extract_mutagen_metadata()

            assert Id3v2Manager.Id3TextFrame.TITLE in raw_metadata
            assert str(raw_metadata[Id3v2Manager.Id3TextFrame.TITLE][0]) == "Test Title"
            assert Id3v2Manager.Id3TextFrame.ARTISTS in raw_metadata
            artists_text = str(raw_metadata[Id3v2Manager.Id3TextFrame.ARTISTS][0])
            assert "Test Artist" in artists_text

    def test_riff_manager_write_and_read(self):
        with temp_file_with_metadata({}, "wav") as test_file:
            audio_file = _AudioFile(test_file)
            manager = RiffManager(audio_file)

            manager.update_metadata(
                {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.ARTISTS: ["Test Artist"]}
            )

            raw_metadata = manager._extract_mutagen_metadata()

            assert hasattr(raw_metadata, "info")
            info_tags = getattr(raw_metadata, "info", {})
            assert info_tags.get(RiffManager.RiffTagKey.TITLE) == ["Test Title"]
            assert info_tags.get(RiffManager.RiffTagKey.ARTIST) == ["Test Artist"]

    def test_vorbis_manager_write_and_read(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            audio_file = _AudioFile(test_file)
            manager = VorbisManager(audio_file)

            manager.update_metadata(
                {UnifiedMetadataKey.TITLE: "Test Title", UnifiedMetadataKey.ARTISTS: ["Test Artist"]}
            )

            raw_metadata = manager._extract_mutagen_metadata()

            assert raw_metadata.get(VorbisManager.VorbisKey.TITLE) == ["Test Title"]
            assert raw_metadata.get(VorbisManager.VorbisKey.ARTIST) == ["Test Artist"]

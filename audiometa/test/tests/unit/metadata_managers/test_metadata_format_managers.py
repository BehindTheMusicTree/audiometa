
import pytest

from audiometa import AudioFile
from audiometa.manager.id3v1.Id3v1Manager import Id3v1Manager
from audiometa.manager.rating_supporting.Id3v2Manager import Id3v2Manager
from audiometa.manager.rating_supporting.RiffManager import RiffManager
from audiometa.manager.rating_supporting.VorbisManager import VorbisManager
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestMetadataFormatManagers:

    def test_id3v1_manager_write_and_read(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v1Manager(audio_file)
            
            manager.update_metadata({
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            })
            
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert title == "Test Title"
            assert artists == ["Test Artist"]

    def test_id3v2_manager_write_and_read(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v2Manager(audio_file)
            
            manager.update_metadata({
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            })
            
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert title == "Test Title"
            assert artists == ["Test Artist"]

    def test_riff_manager_write_and_read(self):
        with TempFileWithMetadata({}, "wav") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = RiffManager(audio_file)
            
            manager.update_metadata({
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            })
            
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert title == "Test Title"
            assert artists == ["Test Artist"]

    def test_vorbis_manager_write_and_read(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = VorbisManager(audio_file)
            
            manager.update_metadata({
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.ARTISTS: ["Test Artist"]
            })
            
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert title == "Test Title"
            assert artists == ["Test Artist"]


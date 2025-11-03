

import pytest
from pathlib import Path

from audiometa import AudioFile
from audiometa.manager.id3v1.Id3v1Manager import Id3v1Manager
from audiometa.manager.id3v1.Id3v1RawMetadataKey import Id3v1RawMetadataKey
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata


@pytest.mark.unit
class TestId3v1Manager:

    def test_id3v1_manager_mp3(self, mocker, sample_mp3_file: Path):
        # Mock the metadata extraction to avoid file I/O
        mock_raw_metadata = mocker.MagicMock()
        mock_raw_metadata.tags = {}  # Simulate no metadata present
        mocker.patch.object(Id3v1Manager, '_extract_mutagen_metadata', return_value=mock_raw_metadata)
        
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v1Manager(audio_file)
        
        metadata = manager.get_unified_metadata()
        assert isinstance(metadata, dict)

    def test_id3v1_manager_flac(self, mocker, sample_flac_file: Path):
        # Mock the metadata extraction to avoid file I/O
        mock_raw_metadata = mocker.MagicMock()
        mock_raw_metadata.tags = {}  # Simulate no metadata present
        mocker.patch.object(Id3v1Manager, '_extract_mutagen_metadata', return_value=mock_raw_metadata)
        
        audio_file = AudioFile(sample_flac_file)
        manager = Id3v1Manager(audio_file)
        
        metadata = manager.get_unified_metadata()
        assert isinstance(metadata, dict)

    def test_id3v1_manager_wav(self, mocker, sample_wav_file: Path):
        # Mock the metadata extraction to avoid file I/O
        mock_raw_metadata = mocker.MagicMock()
        mock_raw_metadata.tags = {}  # Simulate no metadata present
        mocker.patch.object(Id3v1Manager, '_extract_mutagen_metadata', return_value=mock_raw_metadata)
        
        audio_file = AudioFile(sample_wav_file)
        manager = Id3v1Manager(audio_file)
        
        metadata = manager.get_unified_metadata()
        assert isinstance(metadata, dict)

    def test_id3v1_manager_get_specific_metadata(self, mocker, sample_mp3_file: Path):
        # Mock the metadata extraction to avoid file I/O
        mock_raw_metadata = mocker.MagicMock()
        mock_raw_metadata.tags = {}  # Simulate no metadata present
        mocker.patch.object(Id3v1Manager, '_extract_mutagen_metadata', return_value=mock_raw_metadata)
        
        audio_file = AudioFile(sample_mp3_file)
        manager = Id3v1Manager(audio_file)
        
        title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
        assert title is None or isinstance(title, str)

    def test_id3v1_manager_write_support(self):
        from audiometa.test.helpers.id3v1.id3v1_metadata_getter import ID3v1MetadataGetter
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v1Manager(audio_file)
            
            test_metadata = {
                UnifiedMetadataKey.TITLE: "ID3v1 Test Title",
                UnifiedMetadataKey.ARTISTS: ["ID3v1 Test Artist"],
                UnifiedMetadataKey.ALBUM: "ID3v1 Test Album"
            }
            
            manager.update_metadata(test_metadata)
            
            raw_metadata = ID3v1MetadataGetter.get_raw_metadata(test_file.path)
            
            assert raw_metadata.get('title') == "ID3v1 Test Title"
            assert raw_metadata.get('artist') == "ID3v1 Test Artist"
            assert raw_metadata.get('album') == "ID3v1 Test Album"

    def test_id3v1_manager_write_unsupported_fields_raises_error(self, mocker):
        # Mock AudioFile to avoid real file operations
        mock_audio_file = mocker.MagicMock()
        mocker.patch('audiometa.AudioFile', return_value=mock_audio_file)
        mocker.patch('os.path.exists', return_value=True)
        
        audio_file = AudioFile('dummy.mp3')
        manager = Id3v1Manager(audio_file)
        
        # Test unsupported fields that should raise MetadataFieldNotSupportedByMetadataFormatError
        unsupported_metadata = {
            UnifiedMetadataKey.BPM: 120,  # BPM not supported by ID3v1
            UnifiedMetadataKey.RATING: 85,  # Rating not supported by ID3v1
            UnifiedMetadataKey.ALBUM_ARTISTS: ["Album Artist"],  # Album artist not supported by ID3v1
        }
        
        # ID3v1 manager should raise error when trying to write unsupported fields
        with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError):
            manager.update_metadata(unsupported_metadata)

    def test_id3v1_manager_read_title(self):
        from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v1MetadataSetter.set_title(test_file.path, "Test Title ID3v1")
            
            audio_file = AudioFile(test_file.path)
            manager = Id3v1Manager(audio_file)
            title = manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            
            assert title == "Test Title ID3v1"

    def test_id3v1_manager_read_artists(self):
        from audiometa.test.helpers.id3v1 import ID3v1MetadataSetter
        
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v1MetadataSetter.set_artists(test_file.path, "Artist 1")
            
            audio_file = AudioFile(test_file.path)
            manager = Id3v1Manager(audio_file)
            artists = manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            
            assert artists == "Artist 1"

    def test_id3v1_manager_write_title(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v1Manager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.TITLE: "Written Title"})
            
            new_manager = Id3v1Manager(AudioFile(test_file.path))
            title = new_manager.get_unified_metadata_field(UnifiedMetadataKey.TITLE)
            assert title == "Written Title"

    def test_id3v1_manager_write_artists(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            audio_file = AudioFile(test_file.path)
            manager = Id3v1Manager(audio_file)
            manager.update_metadata({UnifiedMetadataKey.ARTISTS: ["Written Artist"]})
            
            new_manager = Id3v1Manager(AudioFile(test_file.path))
            artists = new_manager.get_unified_metadata_field(UnifiedMetadataKey.ARTISTS)
            assert artists == "Written Artist"

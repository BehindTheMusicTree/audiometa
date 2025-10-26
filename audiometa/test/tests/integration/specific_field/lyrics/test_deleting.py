import pytest

from audiometa import update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2.id3v2_metadata_getter import ID3v2MetadataGetter
from audiometa.test.helpers.id3v2.id3v2_metadata_setter import ID3v2MetadataSetter
from audiometa.test.helpers.vorbis.vorbis_metadata_getter import VorbisMetadataGetter
from audiometa.utils.MetadataFormat import MetadataFormat


@pytest.mark.integration
class TestLyricsDeleting:
    def test_delete_lyrics_id3v1(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError, match="UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS metadata not supported by this format"):
                update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: "Test lyrics"}, metadata_format=MetadataFormat.ID3V1)
    
    def test_delete_lyrics_id3v2_3(self):        
        with TempFileWithMetadata({}, "id3v2.3") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file.path, "Test lyrics", version='2.3')
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.3')
            # 4 null bytes because of missing language
            assert raw_metadata['USLT'] == ["\x00\x00\x00\x00Test lyrics"]
        
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 3, 0))
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.3')
            assert raw_metadata.get('USLT') is None
            
    def test_delete_lyrics_id3v2_4(self):        
        with TempFileWithMetadata({}, "id3v2.4") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file.path, "Test lyrics", version='2.4')
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.4')
            assert raw_metadata['USLT'] == ["eng\x00Test lyrics"]
        
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.ID3V2, id3v2_version=(2, 4, 0))
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path, version='2.4')
            assert raw_metadata.get('USLT') is None

    def test_delete_lyrics_riff(self):        
        with TempFileWithMetadata({}, "wav") as test_file:
            from audiometa.test.helpers.riff.riff_metadata_setter import RIFFMetadataSetter
            from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
            
            RIFFMetadataSetter.set_lyrics(test_file.path, "Test lyrics")
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "TAG:lyrics=Test lyrics" in raw_metadata
        
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.RIFF)
            
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "TAG:lyrics=" not in raw_metadata

    def test_delete_lyrics_vorbis(self):        
        with TempFileWithMetadata({}, "flac") as test_file:
            from audiometa.test.helpers.vorbis.vorbis_metadata_setter import VorbisMetadataSetter
            VorbisMetadataSetter.set_lyrics(test_file.path, "Test lyrics")
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file.path)
            assert "LYRICS=Test lyrics" in raw_metadata
        
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.VORBIS)
            
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file.path)
            assert "LYRICS=" not in raw_metadata

    def test_delete_lyrics_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            # Set multiple metadata fields using helper methods
            ID3v2MetadataSetter.set_lyrics(test_file.path, "Test lyrics")
            ID3v2MetadataSetter.set_title(test_file.path, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file.path, "Test Artist")

            # Delete only lyrics using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.ID3V2)
            
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path)
            assert raw_metadata is None

    def test_delete_lyrics_already_none(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            # Try to delete lyrics that don't exist
            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file.path)
            assert "LYRICS=" not in raw_metadata
            
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.VORBIS)

            raw_metadata = VorbisMetadataGetter.get_raw_metadata(test_file.path)
            assert "LYRICS=" not in raw_metadata
            
    def test_delete_lyrics_empty_string(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_lyrics(test_file.path, " ")
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path)
            assert 'USLT' in raw_metadata  # Lyrics field exists
            
            update_metadata(test_file.path, {UnifiedMetadataKey.UNSYNCHRONIZED_LYRICS: None}, metadata_format=MetadataFormat.ID3V2)
            raw_metadata = ID3v2MetadataGetter.get_raw_metadata(test_file.path)
            assert raw_metadata is None or 'USLT' not in raw_metadata

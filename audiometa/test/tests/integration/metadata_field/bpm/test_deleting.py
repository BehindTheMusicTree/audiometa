import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.test.helpers.temp_file_with_metadata import TempFileWithMetadata
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter


@pytest.mark.integration
class TestBpmDeleting:
    def test_delete_bpm_id3v2(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_bpm(test_file.path, 120)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM) == 120
        
            # Delete metadata using library API
            update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM) is None

    def test_delete_bpm_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
        
        with TempFileWithMetadata({}, "mp3") as test_file:            
            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError):
                update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V1)

    def test_delete_bpm_riff(self):
        with TempFileWithMetadata({'bpm': 120}, "wav") as test_file:         
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "ibpm=120" in raw_metadata
                
            update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.RIFF)
            raw_metadata_after = RIFFMetadataGetter.get_raw_metadata(test_file.path)
            assert "ibpm=120" not in raw_metadata_after

    def test_delete_bpm_vorbis(self):
        with TempFileWithMetadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_bpm(test_file.path, 120)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.VORBIS) == 120
        
            update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM) is None

    def test_delete_bpm_preserves_other_fields(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_bpm(test_file.path, 120)
            ID3v2MetadataSetter.set_title(test_file.path, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file.path, "Test Artist")
        
            update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
        
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM) is None
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_bpm_already_none(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM) is None

    def test_delete_bpm_zero(self):
        with TempFileWithMetadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_bpm(test_file.path, 0)

            update_metadata(test_file.path, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file.path, UnifiedMetadataKey.BPM) is None

import pytest

from audiometa import get_unified_metadata_field, update_metadata
from audiometa.test.helpers.id3v2 import ID3v2MetadataSetter
from audiometa.test.helpers.riff.riff_metadata_getter import RIFFMetadataGetter
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis import VorbisMetadataSetter
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestBpmDeleting:
    def test_delete_bpm_id3v2(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_bpm(test_file, 120)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) == 120

            # Delete metadata using library API
            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) is None

    def test_delete_bpm_id3v1(self):
        from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError

        with (
            temp_file_with_metadata({}, "mp3") as test_file,
            pytest.raises(MetadataFieldNotSupportedByMetadataFormatError),
        ):
            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V1)

    def test_delete_bpm_riff(self):
        with temp_file_with_metadata({"bpm": 120}, "wav") as test_file:
            raw_metadata = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "ibpm=120" in raw_metadata

            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.RIFF)
            raw_metadata_after = RIFFMetadataGetter.get_raw_metadata(test_file)
            assert "ibpm=120" not in raw_metadata_after

    def test_delete_bpm_vorbis(self):
        with temp_file_with_metadata({}, "flac") as test_file:
            VorbisMetadataSetter.set_bpm(test_file, 120)
            assert (
                get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM, metadata_format=MetadataFormat.VORBIS)
                == 120
            )

            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.VORBIS)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) is None

    def test_delete_bpm_preserves_other_fields(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_bpm(test_file, 120)
            ID3v2MetadataSetter.set_title(test_file, "Test Title")
            ID3v2MetadataSetter.set_artists(test_file, "Test Artist")

            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)

            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) is None
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.TITLE) == "Test Title"
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.ARTISTS) == ["Test Artist"]

    def test_delete_bpm_already_none(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) is None

    def test_delete_bpm_zero(self):
        with temp_file_with_metadata({}, "mp3") as test_file:
            ID3v2MetadataSetter.set_bpm(test_file, 0)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) == 0

            update_metadata(test_file, {UnifiedMetadataKey.BPM: None}, metadata_format=MetadataFormat.ID3V2)
            assert get_unified_metadata_field(test_file, UnifiedMetadataKey.BPM) is None

import pytest

from audiometa import delete_all_metadata, update_metadata
from audiometa.test.helpers.id3v1.id3v1_header_verifier import ID3v1HeaderVerifier
from audiometa.test.helpers.id3v2.id3v2_header_verifier import ID3v2HeaderVerifier
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.test.helpers.vorbis.vorbis_header_verifier import VorbisHeaderVerifier
from audiometa.utils.MetadataFormat import MetadataFormat
from audiometa.utils.UnifiedMetadataKey import UnifiedMetadataKey


@pytest.mark.integration
class TestAudioFormatHeaderDeletion:
    def test_header_detection_flac(self):
        with temp_file_with_metadata({"title": "FLAC Test"}, "flac") as flac_file:
            vorbis_metadata = {UnifiedMetadataKey.TITLE: "FLAC Vorbis Title"}
            update_metadata(flac_file.path, vorbis_metadata, metadata_format=MetadataFormat.VORBIS)

            id3v2_metadata = {UnifiedMetadataKey.ARTISTS: ["FLAC ID3v2 Artist"]}
            update_metadata(flac_file.path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            id3v1_metadata = {UnifiedMetadataKey.ALBUM: "FLAC ID3v1 Album"}
            update_metadata(flac_file.path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            assert VorbisHeaderVerifier.has_vorbis_comments(flac_file.path)
            assert ID3v1HeaderVerifier.has_id3v1_header(flac_file.path)
            assert ID3v2HeaderVerifier.has_id3v2_header(flac_file.path)

            # Test header removal
            result = delete_all_metadata(flac_file.path)
            assert result is True

            # After deletion, headers should be removed
            assert not VorbisHeaderVerifier.has_vorbis_comments(flac_file.path)
            assert not ID3v1HeaderVerifier.has_id3v1_header(flac_file.path)
            assert not ID3v2HeaderVerifier.has_id3v2_header(flac_file.path)

    def test_header_detection_wav(self):
        with temp_file_with_metadata({"title": "WAV Test"}, "wav") as wav_file:
            riff_metadata = {UnifiedMetadataKey.TITLE: "WAV RIFF Title"}
            update_metadata(wav_file.path, riff_metadata, metadata_format=MetadataFormat.RIFF)

            id3v2_metadata = {UnifiedMetadataKey.ARTISTS: ["WAV ID3v2 Artist"]}
            update_metadata(wav_file.path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            id3v1_metadata = {UnifiedMetadataKey.ALBUM: "WAV ID3v1 Album"}
            update_metadata(wav_file.path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            assert ID3v1HeaderVerifier.has_id3v1_header(wav_file.path)
            assert ID3v2HeaderVerifier.has_id3v2_header(wav_file.path)

            # Test header removal
            result = delete_all_metadata(wav_file.path)
            assert result is True

            # After deletion, headers should be removed
            assert not ID3v1HeaderVerifier.has_id3v1_header(wav_file.path)
            assert not ID3v2HeaderVerifier.has_id3v2_header(wav_file.path)

    def test_header_detection_mp3(self):
        with temp_file_with_metadata({"title": "MP3 Test"}, "mp3") as mp3_file:
            id3v2_metadata = {UnifiedMetadataKey.TITLE: "MP3 ID3v2 Title"}
            update_metadata(mp3_file.path, id3v2_metadata, metadata_format=MetadataFormat.ID3V2)

            id3v1_metadata = {UnifiedMetadataKey.ALBUM: "MP3 ID3v1 Album"}
            update_metadata(mp3_file.path, id3v1_metadata, metadata_format=MetadataFormat.ID3V1)

            assert ID3v1HeaderVerifier.has_id3v1_header(mp3_file.path)
            assert ID3v2HeaderVerifier.has_id3v2_header(mp3_file.path)

            # Test header removal
            result = delete_all_metadata(mp3_file.path)
            assert result is True

            # After deletion, headers should be removed
            assert not ID3v1HeaderVerifier.has_id3v1_header(mp3_file.path)
            assert not ID3v2HeaderVerifier.has_id3v2_header(mp3_file.path)

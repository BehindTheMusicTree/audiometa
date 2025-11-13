"""End-to-end tests using real audio files from data/audio_files."""

from pathlib import Path

import pytest

from audiometa import get_unified_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestRealAudioFilesReading:
    """Test cases using real audio files for end-to-end validation."""

    def test_recording_allumerlefeu_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Allumerlefeu_2 matches one with more release groups.mp3"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "Allumer le feu"
        assert metadata[UnifiedMetadataKey.ARTISTS] == ["Johnny Hallyday"]
        assert metadata[UnifiedMetadataKey.ALBUM] == "Les Années 80-90-2000, C'Etait Mieux Avant"
        assert metadata[UnifiedMetadataKey.GENRES_NAMES] == ["Variétés Internationales"]
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2018-09-28"
        assert metadata[UnifiedMetadataKey.TRACK_NUMBER] == "39"
        assert metadata[UnifiedMetadataKey.BPM] == 139
        assert metadata[UnifiedMetadataKey.COMPOSERS] == ["Pascal Obispo", "Pierre Jaconelli"]
        assert metadata[UnifiedMetadataKey.PUBLISHER] == ""
        assert metadata[UnifiedMetadataKey.COPYRIGHT] == "© 2018 Mercury Music Group"

    def test_recording_celinekin_park_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Celinekin Park - no musicbrainz recording duration.mp3"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "Celinekin Park (Linkin Park vs. Celine Dion)"
        assert metadata[UnifiedMetadataKey.ARTISTS] == ["The Table"]
        assert metadata[UnifiedMetadataKey.ALBUM] == "Bootie Top 10 – November/December 2018"  # noqa: RUF001
        assert metadata[UnifiedMetadataKey.ALBUM_ARTISTS] == ["A Plus D"]
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2018-11-30"
        assert metadata[UnifiedMetadataKey.TRACK_NUMBER] == "9/10"
        assert metadata[UnifiedMetadataKey.BPM] == 99
        assert metadata[UnifiedMetadataKey.PUBLISHER] == "[no label]"
        assert metadata[UnifiedMetadataKey.COMMENT] == "BootieMashup.com"

    def test_recording_dans_la_legende_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Dans la legende.flac"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "DA"
        assert metadata[UnifiedMetadataKey.ARTISTS] == ["PNL"]
        assert metadata[UnifiedMetadataKey.ALBUM] == "Dans La Légende"
        assert metadata[UnifiedMetadataKey.ALBUM_ARTISTS] == ["PNL"]
        assert metadata[UnifiedMetadataKey.GENRES_NAMES] == ["French cloud rap"]
        assert metadata[UnifiedMetadataKey.RATING] == 10
        assert metadata[UnifiedMetadataKey.LANGUAGE] == "French"
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2016"
        assert metadata[UnifiedMetadataKey.TRACK_NUMBER] == "01"

    def test_recording_kemar_france_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Kemar - France.mp3"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "Kemar - France"
        assert metadata[UnifiedMetadataKey.BPM] == 140

    def test_recording_tokyo_drift_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Tokyo Drift_no mb recording.mp3"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "Tokyo Drift x Temperature x You Little Beauty (BENNE BOOM Mashup)"
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2021"
        assert metadata[UnifiedMetadataKey.BPM] == 128

    def test_recording_y_do_i_carmina_burana_mp3_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Y do i - Carmina Burana Remix - 7m52.mp3"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert len(metadata) == 0  # No metadata

    def test_recording_y_do_i_carmina_burana_wav_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=Y do i - Carmina Burana Remix - 7m52.wav"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata.get(UnifiedMetadataKey.TITLE) == "Y do i - Carmina Burana Remix (Techno of the Opera)"
        # Additional metadata fields that should be present if added:
        if UnifiedMetadataKey.ARTISTS in metadata:
            assert metadata.get(UnifiedMetadataKey.ARTISTS) == ["Y do I"]
        if UnifiedMetadataKey.ALBUM_ARTISTS in metadata:
            assert metadata.get(UnifiedMetadataKey.ALBUM_ARTISTS) == ["Y do I"]
        if UnifiedMetadataKey.COMPOSERS in metadata:
            assert metadata.get(UnifiedMetadataKey.COMPOSERS) == ["Carl Orff"]
        if UnifiedMetadataKey.ALBUM in metadata:
            assert metadata.get(UnifiedMetadataKey.ALBUM) == "Remixes"

    def test_recording_california_gurls_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=california gurls_id3v2 tags.flac"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "California Gurls"
        assert metadata[UnifiedMetadataKey.ARTISTS] == ["Katy Perry feat. Snoop Dogg"]
        assert metadata[UnifiedMetadataKey.ALBUM] == "Now That's What I Call Music! 76"
        assert metadata[UnifiedMetadataKey.ALBUM_ARTISTS] == ["Various"]
        assert metadata[UnifiedMetadataKey.GENRES_NAMES] == ["Pop Rock", "Euro House"]
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2010"
        assert metadata[UnifiedMetadataKey.TRACK_NUMBER] == "1"
        assert metadata[UnifiedMetadataKey.BPM] == 125
        assert (
            metadata[UnifiedMetadataKey.COPYRIGHT]
            == "© EMI Records Ltd. © Virgin Records Ltd. © Universal Music Operations Ltd."
        )

    def test_recording_juan_hansen_drown_flac_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=juan hansen oostil - drown (massano remix) - 7m20.flac"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "Drown (Massano Remix)"
        assert metadata[UnifiedMetadataKey.ARTISTS] == ["Øostil & Juan Hansen"]
        assert metadata[UnifiedMetadataKey.ALBUM] == "In My System EP"
        assert metadata[UnifiedMetadataKey.ALBUM_ARTISTS] == ["Massano"]
        assert metadata[UnifiedMetadataKey.GENRES_NAMES] == ["Techno"]
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2022"
        assert metadata[UnifiedMetadataKey.TRACK_NUMBER] == "2"
        assert metadata[UnifiedMetadataKey.BPM] == 122

    def test_recording_juan_hansen_drown_mp3_metadata(self, assets_dir: Path):
        file_path = assets_dir / "recording=juan hansen oostil - drown (massano remix) - 7m21.mp3"

        metadata = get_unified_metadata(file_path)
        assert isinstance(metadata, dict)
        assert metadata[UnifiedMetadataKey.TITLE] == "Drown (Massano Remix)"
        assert metadata[UnifiedMetadataKey.ARTISTS] == ["Øostil"]
        assert metadata[UnifiedMetadataKey.ALBUM] == "In My System EP"
        assert metadata[UnifiedMetadataKey.ALBUM_ARTISTS] == ["Massano"]
        assert metadata[UnifiedMetadataKey.GENRES_NAMES] == ["Electro"]
        assert metadata[UnifiedMetadataKey.RELEASE_DATE] == "2022-04-15"
        assert metadata[UnifiedMetadataKey.TRACK_NUMBER] == "2"
        assert metadata[UnifiedMetadataKey.BPM] == 122
        assert metadata[UnifiedMetadataKey.PUBLISHER] == "Afterlife"

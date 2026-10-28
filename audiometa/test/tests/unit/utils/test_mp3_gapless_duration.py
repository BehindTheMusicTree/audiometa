from pathlib import Path

import pytest

from audiometa.utils.mp3_gapless_duration import read_mp3_gapless_duration

MPEG1_STEREO_44100_HEADER = bytes([0xFF, 0xFB, 0x90, 0x00])
MPEG2_STEREO_22050_HEADER = bytes([0xFF, 0xF3, 0x90, 0x00])
MPEG1_SIDE_INFO_STEREO = 32
MPEG2_SIDE_INFO_STEREO = 17
FRAMES_FLAG = 0x1
BYTES_FLAG = 0x2


def _xing_frame(
    header: bytes,
    side_info: int,
    frames: int,
    encoder: bytes = b"Lavc59.37",
    delay: int = 0,
    padding: int = 0,
    flags: int = FRAMES_FLAG,
) -> bytes:
    body = header + bytes(side_info) + b"Info" + flags.to_bytes(4, "big")
    if flags & FRAMES_FLAG:
        body += frames.to_bytes(4, "big")
    if flags & BYTES_FLAG:
        body += bytes(4)
    delay_padding = bytes([delay >> 4, ((delay & 0xF) << 4) | (padding >> 8), padding & 0xFF])
    return body + encoder.ljust(21, b"\0") + delay_padding + bytes(64)


def _id3v2_header(size: int, flags: int = 0) -> bytes:
    syncsafe = bytes([(size >> 21) & 0x7F, (size >> 14) & 0x7F, (size >> 7) & 0x7F, size & 0x7F])
    return b"ID3\x04\x00" + bytes([flags]) + syncsafe


@pytest.mark.unit
class TestReadMp3GaplessDuration:
    @pytest.mark.parametrize(
        ("relative_path", "expected"),
        [
            ("sample.mp3", 1.0),
            ("shared/duration=277s.mp3", 277.839433),
            ("shared/recording=Y do i - Carmina Burana Remix - 7m52.mp3", 472.594286),
            ("shared/duration=182.mp3", 181.696145),
        ],
    )
    def test_fixture_matches_ffprobe(self, assets_dir: Path, relative_path: str, expected: float):
        assert read_mp3_gapless_duration(assets_dir / relative_path) == pytest.approx(expected, abs=1e-6)

    def test_file_without_xing_frame_returns_none(self, assets_dir: Path):
        assert read_mp3_gapless_duration(assets_dir / "size_small=0.01mo.mp3") is None

    @pytest.mark.parametrize("encoder", [b"LAME3.100", b"Lavc59.37", b"Lavf60.16", b"L3.99r1"])
    def test_known_encoder_subtracts_delay_and_padding(self, tmp_path: Path, encoder: bytes):
        path = tmp_path / "a.mp3"
        path.write_bytes(_xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, encoder, 576, 1105))
        assert read_mp3_gapless_duration(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

    def test_unknown_encoder_ignores_delay_and_padding(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(_xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, b"Other1.0", 576, 1105))
        assert read_mp3_gapless_duration(path) == pytest.approx(100 * 1152 / 44100)

    def test_mpeg2_uses_576_samples_per_frame(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(_xing_frame(MPEG2_STEREO_22050_HEADER, MPEG2_SIDE_INFO_STEREO, 100, b"LAME3.100", 528, 0))
        assert read_mp3_gapless_duration(path) == pytest.approx((100 * 576 - 528) / 22050)

    def test_missing_frame_count_flag_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(_xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, flags=0))
        assert read_mp3_gapless_duration(path) is None

    def test_bytes_field_is_skipped_before_encoder(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(
            _xing_frame(
                MPEG1_STEREO_44100_HEADER,
                MPEG1_SIDE_INFO_STEREO,
                100,
                b"LAME3.100",
                576,
                1105,
                FRAMES_FLAG | BYTES_FLAG,
            )
        )
        assert read_mp3_gapless_duration(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

    def test_delay_and_padding_exceeding_samples_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(_xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 1, b"LAME3.100", 1000, 1000))
        assert read_mp3_gapless_duration(path) is None

    def test_truncated_xing_header_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(_xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100)[:42])
        assert read_mp3_gapless_duration(path) is None

    def test_empty_file_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        path.write_bytes(b"")
        assert read_mp3_gapless_duration(path) is None

    @pytest.mark.parametrize(("flags", "tag_padding"), [(0, 0), (0x10, 10)])
    def test_id3v2_tag_is_skipped(self, tmp_path: Path, flags: int, tag_padding: int):
        tag_body = bytes(300)
        footer = b"3DI" + bytes(7) if flags else b""
        path = tmp_path / "a.mp3"
        path.write_bytes(
            _id3v2_header(len(tag_body), flags)
            + tag_body
            + footer
            + _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, b"LAME3.100", 576, 1105)
        )
        assert tag_padding == len(footer)
        assert read_mp3_gapless_duration(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

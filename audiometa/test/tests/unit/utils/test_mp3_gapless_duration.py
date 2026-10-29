from pathlib import Path

import pytest
from mutagen.mp3 import MP3

from audiometa.utils.mp3_gapless_duration import read_mp3_gapless_duration

MPEG1_STEREO_44100_HEADER = bytes([0xFF, 0xFB, 0x90, 0x00])
MPEG2_STEREO_22050_HEADER = bytes([0xFF, 0xF3, 0x90, 0x00])
MPEG1_FRAME_SIZE = 417
MPEG2_FRAME_SIZE = 261
MPEG1_LAYER2_FRAME_SIZE = 522
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


def _stream(first_frame: bytes, header: bytes, frame_size: int, prefix: bytes = b"") -> bytes:
    padded = first_frame.ljust(frame_size, b"\0")
    silent_frame = (header + bytes(frame_size))[:frame_size]
    return prefix + padded + silent_frame * 4


def _gapless(path: Path) -> float | None:
    return read_mp3_gapless_duration(path, MP3(path).info)


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
        assert _gapless(assets_dir / relative_path) == pytest.approx(expected, abs=1e-6)

    def test_file_without_xing_frame_returns_none(self, assets_dir: Path):
        assert _gapless(assets_dir / "size_small=0.01mo.mp3") is None

    @pytest.mark.parametrize("encoder", [b"LAME3.100", b"Lavc59.37", b"Lavf60.16", b"L3.99r1"])
    def test_known_encoder_subtracts_delay_and_padding(self, tmp_path: Path, encoder: bytes):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, encoder, 576, 1105)
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE))
        assert _gapless(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

    def test_unknown_encoder_ignores_delay_and_padding(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, b"Other1.0", 576, 1105)
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE))
        assert _gapless(path) == pytest.approx(100 * 1152 / 44100)

    def test_mpeg2_uses_576_samples_per_frame(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(MPEG2_STEREO_22050_HEADER, MPEG2_SIDE_INFO_STEREO, 100, b"LAME3.100", 528, 0)
        path.write_bytes(_stream(frame, MPEG2_STEREO_22050_HEADER, MPEG2_FRAME_SIZE))
        assert _gapless(path) == pytest.approx((100 * 576 - 528) / 22050)

    def test_missing_frame_count_flag_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, flags=0)
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE))
        assert _gapless(path) is None

    def test_bytes_field_is_skipped_before_encoder(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(
            MPEG1_STEREO_44100_HEADER,
            MPEG1_SIDE_INFO_STEREO,
            100,
            b"LAME3.100",
            576,
            1105,
            FRAMES_FLAG | BYTES_FLAG,
        )
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE))
        assert _gapless(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

    def test_delay_and_padding_exceeding_samples_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 1, b"LAME3.100", 1000, 1000)
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE))
        assert _gapless(path) is None

    def test_truncated_xing_header_returns_none(self, tmp_path: Path):
        path = tmp_path / "a.mp3"
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100)[:42]
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE))
        assert _gapless(path) is None

    @pytest.mark.parametrize("tag_count", [1, 2])
    def test_stacked_id3v2_tags_are_skipped(self, tmp_path: Path, tag_count: int):
        tag = _id3v2_header(300) + bytes(300)
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, b"LAME3.100", 576, 1105)
        path = tmp_path / "a.mp3"
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE, tag * tag_count))
        assert _gapless(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

    def test_false_sync_in_junk_before_first_frame_is_ignored(self, tmp_path: Path):
        junk = bytes([0xFF, 0xFB, 0x90, 0x00]) + bytes(20)
        frame = _xing_frame(MPEG1_STEREO_44100_HEADER, MPEG1_SIDE_INFO_STEREO, 100, b"LAME3.100", 576, 1105)
        path = tmp_path / "a.mp3"
        path.write_bytes(_stream(frame, MPEG1_STEREO_44100_HEADER, MPEG1_FRAME_SIZE, junk))
        assert _gapless(path) == pytest.approx((100 * 1152 - 576 - 1105) / 44100)

    def test_non_layer3_stream_returns_none(self, tmp_path: Path):
        layer2_header = bytes([0xFF, 0xFD, 0x90, 0x00])
        path = tmp_path / "a.mp3"
        path.write_bytes((layer2_header + bytes(MPEG1_LAYER2_FRAME_SIZE - 4)) * 6)
        assert _gapless(path) is None

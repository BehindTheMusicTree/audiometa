"""Gapless MP3 duration from the Xing/Info frame and its LAME or ffmpeg (Lavc/Lavf) extension.

mutagen only subtracts encoder delay and padding when the LAME extension's encoder string starts with
"LAME"; ffmpeg writes the same extension with "Lavc"/"Lavf", so mutagen over-reports those files.
Frame sync is taken from mutagen's MPEGInfo.
"""

from pathlib import Path

from mutagen.mp3 import MPEGInfo

_MPEG1_VERSION = 1.0
_LAYER3 = 3
_MONO_MODE = 3
_MPEG1_SAMPLES_PER_FRAME = 1152
_MPEG2_SAMPLES_PER_FRAME = 576
_FRAME_HEADER_SIZE = 4
_READ_SIZE = 512
_XING_TAGS = (b"Xing", b"Info")
_XING_FRAMES_FLAG = 0x1
_XING_BYTES_FLAG = 0x2
_XING_TOC_FLAG = 0x4
_XING_SCALE_FLAG = 0x8
_XING_TOC_SIZE = 100

_LAME_ENCODER_PREFIXES = (b"LAME", b"L3.99", b"Lavc", b"Lavf")
_LAME_DELAY_PADDING_OFFSET = 21
_LAME_DELAY_PADDING_SIZE = 3


def read_mp3_gapless_duration(path: str | Path, info: MPEGInfo) -> float | None:
    """Return the gapless duration in seconds, or None if the first frame has no Xing/Info frame count."""
    if info.layer != _LAYER3:
        return None

    with Path(path).open("rb") as f:
        f.seek(info.frame_offset)
        buf = f.read(_READ_SIZE)

    mono = info.mode == _MONO_MODE
    if info.version == _MPEG1_VERSION:
        side_info_size = 17 if mono else 32
        samples_per_frame = _MPEG1_SAMPLES_PER_FRAME
    else:
        side_info_size = 9 if mono else 17
        samples_per_frame = _MPEG2_SAMPLES_PER_FRAME

    xing = _FRAME_HEADER_SIZE + side_info_size
    if buf[xing : xing + 4] not in _XING_TAGS or len(buf) < xing + 12:
        return None
    flags = int.from_bytes(buf[xing + 4 : xing + 8], "big")
    if not flags & _XING_FRAMES_FLAG:
        return None
    frames = int.from_bytes(buf[xing + 8 : xing + 12], "big")

    pos = xing + 12
    if flags & _XING_BYTES_FLAG:
        pos += 4
    if flags & _XING_TOC_FLAG:
        pos += _XING_TOC_SIZE
    if flags & _XING_SCALE_FLAG:
        pos += 4

    delay = padding = 0
    delay_padding = buf[pos + _LAME_DELAY_PADDING_OFFSET : pos + _LAME_DELAY_PADDING_OFFSET + _LAME_DELAY_PADDING_SIZE]
    if buf[pos:].startswith(_LAME_ENCODER_PREFIXES) and len(delay_padding) == _LAME_DELAY_PADDING_SIZE:
        delay = (delay_padding[0] << 4) | (delay_padding[1] >> 4)
        padding = ((delay_padding[1] & 0x0F) << 8) | delay_padding[2]

    samples = frames * samples_per_frame - delay - padding
    if samples <= 0:
        return None
    return float(samples / info.sample_rate)

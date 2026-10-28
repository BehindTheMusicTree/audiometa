"""Gapless MP3 duration from the Xing/Info frame and its LAME extension.

mutagen only subtracts encoder delay and padding when the LAME extension's encoder string starts with
"LAME"; ffmpeg writes the same extension with "Lavc"/"Lavf", so mutagen over-reports those files.
"""

from pathlib import Path

from audiometa.manager._rating_supporting.id3v2._id3v2_constants import ID3V2_HEADER_SIZE

_SCAN_SIZE = 64 * 1024
_ID3V2_FOOTER_FLAG = 0x10
_ID3V2_FOOTER_SIZE = 10

_MPEG1 = 3
_MPEG2 = 2
_MPEG25 = 0
_LAYER3 = 1
_RESERVED_SAMPLE_RATE_INDEX = 3
_FREE_BITRATE_INDEX = 0
_BAD_BITRATE_INDEX = 15
_MONO_CHANNEL_MODE = 3
_SAMPLE_RATES = {
    _MPEG1: (44100, 48000, 32000),
    _MPEG2: (22050, 24000, 16000),
    _MPEG25: (11025, 12000, 8000),
}
_MPEG1_SAMPLES_PER_FRAME = 1152
_MPEG2_SAMPLES_PER_FRAME = 576

_FRAME_HEADER_SIZE = 4
_SYNC_BYTE = 0xFF
_SYNC_MASK = 0xE0
_XING_TAGS = (b"Xing", b"Info")
_XING_FRAMES_FLAG = 0x1
_XING_BYTES_FLAG = 0x2
_XING_TOC_FLAG = 0x4
_XING_SCALE_FLAG = 0x8
_XING_TOC_SIZE = 100

_LAME_ENCODER_PREFIXES = (b"LAME", b"L3.99", b"Lavc", b"Lavf")
_LAME_DELAY_PADDING_OFFSET = 21
_LAME_DELAY_PADDING_SIZE = 3


def _audio_start(path: Path) -> int:
    with path.open("rb") as f:
        header = f.read(ID3V2_HEADER_SIZE)
    if len(header) < ID3V2_HEADER_SIZE or not header.startswith(b"ID3"):
        return 0
    size = ((header[6] & 0x7F) << 21) | ((header[7] & 0x7F) << 14) | ((header[8] & 0x7F) << 7) | (header[9] & 0x7F)
    footer = _ID3V2_FOOTER_SIZE if header[5] & _ID3V2_FOOTER_FLAG else 0
    return ID3V2_HEADER_SIZE + size + footer


def _find_layer3_frame(buf: bytes) -> int | None:
    for i in range(len(buf) - _FRAME_HEADER_SIZE + 1):
        if buf[i] != _SYNC_BYTE or (buf[i + 1] & _SYNC_MASK) != _SYNC_MASK:
            continue
        version = (buf[i + 1] >> 3) & 0x3
        layer = (buf[i + 1] >> 1) & 0x3
        bitrate_index = buf[i + 2] >> 4
        sample_rate_index = (buf[i + 2] >> 2) & 0x3
        if (
            version in _SAMPLE_RATES
            and layer == _LAYER3
            and sample_rate_index != _RESERVED_SAMPLE_RATE_INDEX
            and bitrate_index not in (_FREE_BITRATE_INDEX, _BAD_BITRATE_INDEX)
        ):
            return i
    return None


def read_mp3_gapless_duration(path: str | Path) -> float | None:
    """Return the gapless duration in seconds, or None if the first frame has no Xing/Info frame count."""
    path = Path(path)
    with path.open("rb") as f:
        f.seek(_audio_start(path))
        buf = f.read(_SCAN_SIZE)

    frame = _find_layer3_frame(buf)
    if frame is None:
        return None

    version = (buf[frame + 1] >> 3) & 0x3
    sample_rate = _SAMPLE_RATES[version][(buf[frame + 2] >> 2) & 0x3]
    mono = (buf[frame + 3] >> 6) == _MONO_CHANNEL_MODE
    if version == _MPEG1:
        side_info_size = 17 if mono else 32
        samples_per_frame = _MPEG1_SAMPLES_PER_FRAME
    else:
        side_info_size = 9 if mono else 17
        samples_per_frame = _MPEG2_SAMPLES_PER_FRAME

    xing = frame + _FRAME_HEADER_SIZE + side_info_size
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
    return samples / sample_rate

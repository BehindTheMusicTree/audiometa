# Lyrics Support

Two types of lyrics are supported: synchronized lyrics (synchronized with music, for karaoke) and unsynchronized lyrics (plain text).

## Synchronized Lyrics

TODO: Implement synchronized lyrics support in future versions.

Synchronized lyrics (SYLT frames in ID3v2) are not currently supported by the library.

## Unsynchronized Lyrics

Unsynchronized lyrics are supported differently across formats:

### ID3v1 Unsynchronized Lyrics

ID3v1 does not support unsynchronized lyrics due to its limited structure.

### ID3v2 Unsynchronized Lyrics

ID3v2 supports unsynchronized lyrics through the `USLT` (Unsynchronized Lyrics/Text transcription) frame. Multiple `USLT` frames can be used to store lyrics in different languages or formats within the same file.

The library does not currently support language codes or multiple lyrics entries and will write only a single `USLT` frame with default language code `eng`.

TODO: Implement full multi-language support in future versions.

### RIFF Unsynchronized Lyrics

RIFF INFO chunks do not have native support for lyrics. The library supports storing unsynchronized lyrics in the `UNSYNCHRONIZED_LYRICS` chunk.

It does not support language codes or multiple lyrics entries due to lack of standardization.

### Vorbis Unsynchronized Lyrics

Vorbis comments support lyrics through the `UNSYNCHRONIZED_LYRICS` field.
It does not support language codes or multiple lyrics entries due to lack of standardization.

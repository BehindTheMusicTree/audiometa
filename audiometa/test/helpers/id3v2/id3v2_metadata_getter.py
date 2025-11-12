"""id3v2_metadata_getter.py Helper for extracting ID3v2 metadata from audio files."""


class ID3v2MetadataGetter:
    """Helper class to get ID3v2 metadata from audio files using manual parsing."""

    @staticmethod
    def _syncsafe_decode(data: bytes) -> int:
        """Decode a 4-byte syncsafe integer."""
        return ((data[0] & 0x7F) << 21) | ((data[1] & 0x7F) << 14) | ((data[2] & 0x7F) << 7) | (data[3] & 0x7F)

    @staticmethod
    def _decode_text(encoding: int, data: bytes) -> str:
        """Decode text based on encoding."""
        if encoding == 0:  # ISO-8859-1
            return data.decode("latin1", errors="ignore")
        if encoding == 1:  # UTF-16 with BOM
            return data.decode("utf-16", errors="ignore")
        if encoding == 2:  # UTF-16BE without BOM
            return data.decode("utf-16be", errors="ignore")
        if encoding == 3:  # UTF-8
            return data.decode("utf-8", errors="ignore")
        return data.decode("latin1", errors="ignore")  # fallback

    @staticmethod
    def get_raw_metadata(file_path, version=None):
        """Get the raw metadata from the audio file using manual ID3v2 parsing, returning a string with frame IDs and
        values.

        Args:
            file_path: Path to the audio file.
            version: The ID3v2 version to parse ("2.3" for ID3v2.3, "2.4" for ID3v2.4). Defaults to "2.4".

        Returns:
            String with metadata in 'frame_id=value' format, one per line, or error string if parsing fails.
        """
        try:
            with file_path.open("rb") as f:
                # Read ID3v2 header (10 bytes)
                header = f.read(10)
                if len(header) < 10 or header[:3] != b"ID3":
                    return "No ID3v2 tag found"

                # Parse header
                file_version = (header[3], header[4])
                if version is None:
                    version = "2.4"  # Default to 2.4
                if version == "2.3":
                    expected_major = 3
                    expected_minor = 0
                elif version == "2.4":
                    expected_major = 4
                    expected_minor = 0
                else:
                    msg = "Version must be '2.3' or '2.4'"
                    raise ValueError(msg)
                if file_version[0] != expected_major or file_version[1] != expected_minor:
                    return None
                header[5]
                tag_size = ID3v2MetadataGetter._syncsafe_decode(header[6:10])

                # Read tag data
                tag_data = f.read(tag_size)
                if len(tag_data) != tag_size:
                    return "Incomplete ID3v2 tag"

                metadata: dict[str, list[str]] = {}
                pos = 0
                while pos < len(tag_data) - 10:
                    # Parse frame header (10 bytes)
                    frame_id = tag_data[pos : pos + 4]
                    if frame_id == b"\x00\x00\x00\x00":
                        break  # Padding or end
                    try:
                        frame_id_str = frame_id.decode("ascii")
                    except UnicodeDecodeError:
                        break

                    if expected_minor == 4:
                        frame_size = ID3v2MetadataGetter._syncsafe_decode(tag_data[pos + 4 : pos + 8])
                    else:
                        frame_size = int.from_bytes(tag_data[pos + 4 : pos + 8], "big")

                    if pos + 10 + frame_size > len(tag_data):
                        break

                    frame_data = tag_data[pos + 10 : pos + 10 + frame_size]

                    # Parse text frames (those starting with encoding byte)
                    if frame_data and len(frame_data) > 1:
                        encoding = frame_data[0]
                        text_data = frame_data[1:]
                        # Decode the entire text_data first
                        decoded_text = ID3v2MetadataGetter._decode_text(encoding, text_data).rstrip("\x00")
                        if frame_id_str == "USLT":
                            # Parse USLT: language (3 bytes) + descriptor (null-terminated) + lyrics (null-terminated)
                            text_data_bytes = text_data
                            if len(text_data_bytes) > 3:
                                language = text_data_bytes[:3].decode("ascii", errors="ignore")
                                uslt_pos = 3  # after language
                                while uslt_pos < len(text_data_bytes) and text_data_bytes[uslt_pos] != 0:
                                    uslt_pos += 1
                                uslt_pos += 1  # skip null
                                lyrics_bytes = text_data_bytes[uslt_pos:].rstrip(b"\x00")
                                lyrics = ID3v2MetadataGetter._decode_text(encoding, lyrics_bytes)
                                text = f"{language}\x00{lyrics}"
                            else:
                                text = decoded_text
                        else:
                            text = decoded_text
                        if frame_id_str not in metadata:
                            metadata[frame_id_str] = []
                        metadata[frame_id_str].append(text)
                    else:
                        # Non-text frame, just show size
                        if frame_id_str not in metadata:
                            metadata[frame_id_str] = []
                        metadata[frame_id_str].append(f"<{frame_size} bytes>")

                    pos += 10 + frame_size

                return metadata
        except Exception as e:
            return f"Error parsing ID3v2: {e!s}"

    @staticmethod
    def get_artists(file_path, version=None):
        metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, version)
        if not isinstance(metadata, dict) or not metadata:
            return None
        tpe1_values: list[str] = metadata.get("TPE1", [])
        return tpe1_values[0] if tpe1_values else None

    @staticmethod
    def get_title(file_path, version=None):
        try:
            versions_to_try = [version] if version else ["2.3", "2.4"]
            for v in versions_to_try:
                metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, v)
                if isinstance(metadata, dict) and metadata:
                    tit2_values = metadata.get("TIT2", [])
                    if tit2_values:
                        return tit2_values[0]
        except Exception:
            return None
        else:
            return None

    @staticmethod
    def get_album(file_path, version=None):
        metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, version)
        if not isinstance(metadata, dict) or not metadata:
            return None
        talb_values = metadata.get("TALB", [])
        return talb_values[0] if talb_values else None

    @staticmethod
    def get_year(file_path, version=None):
        metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, version)
        if not isinstance(metadata, dict) or not metadata:
            return None
        tyer_values = metadata.get("TYER", [])
        tdrc_values = metadata.get("TDRC", [])
        return (tyer_values + tdrc_values)[0] if tyer_values or tdrc_values else None

    @staticmethod
    def get_genres(file_path, version=None):
        metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, version)
        if not isinstance(metadata, dict) or not metadata:
            return None
        tcon_values = metadata.get("TCON", [])
        return tcon_values[0] if tcon_values else None

    @staticmethod
    def get_comment(file_path, version=None):
        metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, version)
        if not isinstance(metadata, dict) or not metadata:
            return None
        comm_values = metadata.get("COMM", [])
        return comm_values[0] if comm_values else None

    @staticmethod
    def get_track(file_path, version=None):
        metadata = ID3v2MetadataGetter.get_raw_metadata(file_path, version)
        if not isinstance(metadata, dict) or not metadata:
            return None
        trck_values = metadata.get("TRCK", [])
        return trck_values[0] if trck_values else None

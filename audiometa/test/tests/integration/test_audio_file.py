from pathlib import Path

import pytest

from audiometa import get_unified_metadata, get_unified_metadata_field
from audiometa.utils.metadata_format import MetadataFormat
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestAudioFileIntegration:
    def test_functional_api_with_file_path(self, sample_mp3_file: Path):
        # Test that functional APIs work with file paths (string)
        metadata = get_unified_metadata(str(sample_mp3_file))
        assert isinstance(metadata, dict)

        # Test single format with file path
        id3v2_metadata = get_unified_metadata(str(sample_mp3_file), metadata_format=MetadataFormat.ID3V2)
        assert isinstance(id3v2_metadata, dict)

        # Test specific metadata with file path
        title = get_unified_metadata_field(str(sample_mp3_file), UnifiedMetadataKey.TITLE)
        assert title is None or isinstance(title, str)

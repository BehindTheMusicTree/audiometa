import warnings

import pytest

from audiometa import get_unified_metadata, update_metadata
from audiometa.exceptions import MetadataFieldNotSupportedByMetadataFormatError
from audiometa.test.helpers.temp_file_with_metadata import temp_file_with_metadata
from audiometa.utils.unified_metadata_key import UnifiedMetadataKey


@pytest.mark.integration
class TestFailBehavior:
    def test_fail_on_unsupported_field_enabled(self):
        with temp_file_with_metadata({"title": "Test"}, "wav") as test_file:
            test_metadata = {
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.REPLAYGAIN: "89 dB",  # REPLAYGAIN is not supported by RIFF format
            }

            with pytest.raises(MetadataFieldNotSupportedByMetadataFormatError) as exc_info:
                update_metadata(test_file, test_metadata, fail_on_unsupported_field=True)

            assert "Fields not supported by riff format" in str(exc_info.value)
            assert "REPLAYGAIN" in str(exc_info.value)

    def test_fail_on_unsupported_field_disabled_graceful_default(self):
        with temp_file_with_metadata({"title": "Test"}, "wav") as test_file:
            test_metadata = {
                UnifiedMetadataKey.TITLE: "Test Title",
                UnifiedMetadataKey.REPLAYGAIN: "89 dB",  # REPLAYGAIN is not supported by RIFF format
            }

            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                update_metadata(test_file, test_metadata)  # fail_on_unsupported_field=False by default

                assert len(w) > 0
                warning_messages = [str(warning.message) for warning in w]
                assert any("unsupported" in msg.lower() or "not supported" in msg.lower() for msg in warning_messages)

            metadata = get_unified_metadata(test_file)
            assert metadata.get(UnifiedMetadataKey.TITLE) == "Test Title"

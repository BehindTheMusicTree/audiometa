import pytest
from unittest.mock import MagicMock

from audiometa.manager.MetadataManager import MetadataManager


@pytest.mark.unit
class TestMultipleValuesEdgeCases:
    
    def test_only_empty_values_returns_empty(self):
        audio_file = MagicMock()
        manager = MetadataManager(audio_file, {}, {})
        
        values = ["", "", ""]
        result = MetadataManager._filter_valid_values(values)
        assert result == []
        
        result = manager._apply_smart_parsing(values)
        assert result == []


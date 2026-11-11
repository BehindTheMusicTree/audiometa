import pytest


@pytest.mark.e2e
def test_temporary_gate_check():
    raise AssertionError("temporary: verify gates fail when a test fails")

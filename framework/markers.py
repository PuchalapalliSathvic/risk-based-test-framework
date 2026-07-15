"""Helper for tagging a test with the risk area it exercises."""
import pytest


def risk(area):
    """Decorator: attach a risk-area label to a test.

    Usage:
        @risk("authentication")
        def test_login(...): ...
    """
    return pytest.mark.risk(area)

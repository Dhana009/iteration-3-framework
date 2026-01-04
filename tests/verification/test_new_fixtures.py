"""
Test new delete_user_items fixture
"""

import pytest


def test_delete_user_items_fixture_exists(delete_user_items):
    """Verify delete_user_items fixture is available"""
    assert delete_user_items is not None
    assert callable(delete_user_items)
    print("✓ delete_user_items fixture is callable")

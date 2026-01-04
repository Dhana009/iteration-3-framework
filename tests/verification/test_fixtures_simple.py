"""
Simple test to verify MongoDB fixtures work
"""

import pytest


def test_mongodb_fixture_works(create_seed_for_user):
    """Test that create_seed_for_user fixture works"""
    # This test just verifies the fixture can be called
    # We won't actually create data, just check it's available
    assert create_seed_for_user is not None
    assert callable(create_seed_for_user)
    print("✓ create_seed_for_user fixture is callable")


def test_api_fixture_works(create_test_item):
    """Test that create_test_item fixture works"""
    # This test just verifies the fixture can be called
    assert create_test_item is not None
    assert callable(create_test_item)
    print("✓ create_test_item fixture is callable")

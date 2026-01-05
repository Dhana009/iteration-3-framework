"""
Unit tests for ItemBuilder

Tests the Test Data Builder pattern implementation to ensure
proper transformation and validation of item documents.
"""

import pytest
from datetime import datetime, timezone
from bson import ObjectId
from lib.builders.item_builder import ItemBuilder
from lib.seed import SEED_ITEMS


class TestItemBuilderBasic:
    """Test basic ItemBuilder functionality"""
    
    def test_builder_initialization(self):
        """Test that builder initializes with correct defaults"""
        user_id = "695b747b17d17d21e8ae8baa"
        builder = ItemBuilder(user_id)
        
        assert builder.user_id == user_id
        assert builder.user_id_suffix == "8baa"
        assert isinstance(builder.now, datetime)
        assert builder._data['created_by'] == ObjectId(user_id)
        assert builder._data['is_active'] is True
        assert builder._data['tags'] == []
    
    def test_builder_fluent_api(self):
        """Test that builder methods return self for chaining"""
        user_id = "695b747b17d17d21e8ae8baa"
        builder = ItemBuilder(user_id)
        
        result = builder.with_name("Test")
        assert result is builder  # Should return self
        
        result = builder.with_category("Cat")
        assert result is builder
    
    def test_builder_with_name(self):
        """Test name transformation with suffix"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test Item")
                .with_category("Test")  # Required for build()
                .build())
        
        assert item['name'] == "Test Item - 8baa"
        assert item['normalizedName'] == "test item - 8baa"
    
    def test_builder_with_category(self):
        """Test category normalization"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Electronics")
                .build())
        
        assert item['category'] == "Electronics"
        assert item['normalizedCategory'] == "Electronics"  # Title Case, not lowercase
    
    def test_builder_with_price(self):
        """Test price setting"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Test")
                .with_price(99.99)
                .build())
        
        assert item['price'] == 99.99
    
    def test_builder_with_tags(self):
        """Test tag merging with defaults"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Test")
                .with_tags(["custom", "test"])
                .build())
        
        # Should include custom tags + defaults
        assert 'custom' in item['tags']
        assert 'test' in item['tags']
        assert 'seed' in item['tags']
        assert 'v1.0' in item['tags']
    
    def test_builder_with_active_status(self):
        """Test active status setting"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Test")
                .with_active_status(False)
                .build())
        
        assert item['is_active'] is False


class TestItemBuilderFromTemplate:
    """Test building from SEED_ITEMS templates"""
    
    def test_from_template_basic(self):
        """Test building from a template"""
        user_id = "695b747b17d17d21e8ae8baa"
        template = SEED_ITEMS[0]
        
        item = ItemBuilder(user_id).from_template(template).build()
        
        # Verify transformations
        assert item['name'].endswith(" - 8baa")
        assert item['normalizedName'] == item['name'].lower()
        assert item['created_by'] == ObjectId(user_id)
        assert 'normalizedCategory' in item
        assert 'seed' in item['tags']
        assert 'v1.0' in item['tags']
    
    def test_from_template_preserves_fields(self):
        """Test that template fields are preserved"""
        user_id = "695b747b17d17d21e8ae8baa"
        template = {
            'name': 'Test Item',
            'category': 'Electronics',
            'price': 99.99,
            'description': 'Test description',
            'item_type': 'PHYSICAL'
        }
        
        item = ItemBuilder(user_id).from_template(template).build()
        
        assert item['price'] == 99.99
        assert item['description'] == 'Test description'
        assert item['item_type'] == 'PHYSICAL'
    
    def test_from_template_overrides_is_active(self):
        """Test that template can override is_active"""
        user_id = "695b747b17d17d21e8ae8baa"
        template = {
            'name': 'Inactive Item',
            'category': 'Test',
            'is_active': False
        }
        
        item = ItemBuilder(user_id).from_template(template).build()
        
        assert item['is_active'] is False
    
    def test_from_template_merges_tags(self):
        """Test that template tags are merged with defaults"""
        user_id = "695b747b17d17d21e8ae8baa"
        template = {
            'name': 'Tagged Item',
            'category': 'Test',
            'tags': ['custom', 'special']
        }
        
        item = ItemBuilder(user_id).from_template(template).build()
        
        assert 'custom' in item['tags']
        assert 'special' in item['tags']
        assert 'seed' in item['tags']
        assert 'v1.0' in item['tags']


class TestItemBuilderValidation:
    """Test builder validation"""
    
    def test_build_without_name_fails(self):
        """Test that building without name raises error"""
        user_id = "695b747b17d17d21e8ae8baa"
        builder = ItemBuilder(user_id)
        
        with pytest.raises(ValueError, match="Missing required fields"):
            builder.build()
    
    def test_build_with_all_required_succeeds(self):
        """Test that building with required fields succeeds"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Test")
                .build())
        
        assert 'name' in item
        assert 'created_by' in item
        assert 'normalizedName' in item


class TestItemBuilderBatch:
    """Test batch building functionality"""
    
    def test_build_many(self):
        """Test building multiple items at once"""
        user_id = "695b747b17d17d21e8ae8baa"
        templates = SEED_ITEMS[:3]
        
        items = ItemBuilder.build_many(templates, user_id)
        
        assert len(items) == 3
        assert all('normalizedName' in item for item in items)
        assert all(item['created_by'] == ObjectId(user_id) for item in items)
    
    def test_build_many_empty_list(self):
        """Test building from empty list"""
        user_id = "695b747b17d17d21e8ae8baa"
        items = ItemBuilder.build_many([], user_id)
        
        assert items == []
    
    def test_build_many_all_seed_items(self):
        """Test building all SEED_ITEMS"""
        user_id = "695b747b17d17d21e8ae8baa"
        items = ItemBuilder.build_many(SEED_ITEMS, user_id)
        
        assert len(items) == len(SEED_ITEMS)
        # Verify each has unique name suffix
        names = [item['name'] for item in items]
        assert all(" - 8baa" in name for name in names)


class TestItemBuilderTimestamps:
    """Test timestamp handling"""
    
    def test_timestamps_are_utc(self):
        """Test that timestamps are timezone-aware UTC"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Test")
                .build())
        
        assert isinstance(item['createdAt'], datetime)
        assert isinstance(item['updatedAt'], datetime)
        assert item['createdAt'].tzinfo is not None  # Timezone-aware
        assert item['updatedAt'].tzinfo is not None
    
    def test_timestamps_are_same(self):
        """Test that createdAt and updatedAt are the same"""
        user_id = "695b747b17d17d21e8ae8baa"
        item = (ItemBuilder(user_id)
                .with_name("Test")
                .with_category("Test")
                .build())
        
        # Should be the same timestamp
        assert item['createdAt'] == item['updatedAt']

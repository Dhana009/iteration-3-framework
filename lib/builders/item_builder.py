"""
Item Builder - Test Data Builder Pattern Implementation

This module provides a builder class for creating database-ready item documents.
It centralizes all schema knowledge and transformation logic, making tests more
maintainable and resilient to schema changes.

Usage:
    # Simple case - from template
    from lib.builders.item_builder import ItemBuilder
    from lib.seed import SEED_ITEMS
    
    item = ItemBuilder(user_id).from_template(SEED_ITEMS[0]).build()
    
    # Custom case - fluent API
    item = (ItemBuilder(user_id)
            .with_name("Custom Item")
            .with_category("Electronics")
            .with_price(99.99)
            .with_tags(["custom", "test"])
            .build())
    
    # Batch building
    items = ItemBuilder.build_many(SEED_ITEMS, user_id)
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from bson import ObjectId


class ItemBuilder:
    """
    Builder for creating database-ready item documents.
    
    This class implements the Test Data Builder pattern to centralize
    schema knowledge and transformation logic. It ensures all items
    have the required database fields and proper normalization.
    
    Attributes:
        user_id: MongoDB ObjectId as string
        user_id_suffix: Last 4 characters of user_id (for name suffix)
        now: Timestamp for createdAt/updatedAt (generated once)
    """
    
    def __init__(self, user_id: str):
        """
        Initialize builder with user context.
        
        Args:
            user_id: MongoDB ObjectId as string (e.g., "6958191...")
        """
        self.user_id = user_id
        self.user_id_suffix = user_id[-4:]
        
        # Generate timestamp once (shared for createdAt/updatedAt)
        self.now = datetime.now(timezone.utc)
        
        # Initialize with ALL required database fields
        # These fields match what the backend API creates via Mongoose
        self._data = {
            # User tracking (ObjectId for proper MongoDB reference)
            'created_by': ObjectId(user_id),
            
            # Timestamps
            'createdAt': self.now,
            'updatedAt': self.now,
            
            # Status and metadata
            'is_active': True,
            'tags': [],
            
            # Mongoose fields
            '__v': 0,                    # Mongoose version key
            'version': 1,                # Document version
            
            # Soft delete support
            'deleted_at': None,          # Soft delete timestamp
            
            # Audit trail
            'updated_by': None,          # Last updater (ObjectId or None)
            
            # Digital item fields (None for physical items)
            'embed_url': None,           # Embed URL for digital items
            'file_path': None,           # File path for digital items
        }
    
    def from_template(self, template: Dict[str, Any]) -> 'ItemBuilder':
        """
        Populate builder from a template (e.g., SEED_ITEMS).
        Applies all necessary transformations.
        
        Args:
            template: Dictionary with item data (name, category, price, etc.)
        
        Returns:
            self (for method chaining)
        """
        # Copy all template fields
        self._data.update(template)
        
        # Apply transformations
        if 'name' in template:
            self.with_name(template['name'])
        
        if 'category' in template:
            self.with_category(template['category'])
        
        # Convert weight to int (backend stores as int, not float)
        if 'weight' in template and template['weight'] is not None:
            self._data['weight'] = int(template['weight'])
        
        # Override is_active if specified in template
        if 'is_active' in template:
            self._data['is_active'] = template['is_active']
        
        # Merge tags (template tags + default tags)
        template_tags = template.get('tags', [])
        self._data['tags'] = list(set(template_tags + ['seed', 'v1.0']))
        
        return self
    
    def _title_case(self, text: str) -> str:
        """
        Convert text to Title Case (matches backend logic).
        
        Backend logic: category.trim().replace(/\w\S*/g, (txt) => 
            txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase())
        
        Args:
            text: Text to convert
        
        Returns:
            Title cased text
        """
        return ' '.join(word.capitalize() for word in text.strip().split())
    
    def _adaptive_prefix(self, name: str) -> str:
        """
        Generate adaptive prefix (matches backend logic).
        
        Backend logic:
        - 1-2 chars: entire name
        - 3-4 chars: all but last char
        - 5+ chars: first 5 chars
        
        Args:
            name: Name to generate prefix from
        
        Returns:
            Adaptive prefix in lowercase
        """
        length = len(name)
        if length <= 2:
            return name.lower()
        elif length <= 4:
            return name[:-1].lower()
        else:
            return name[:5].lower()
    
    def with_name(self, name: str) -> 'ItemBuilder':
        """
        Set item name with user suffix and generate normalizedName and normalizedNamePrefix.
        
        Args:
            name: Base item name
        
        Returns:
            self (for method chaining)
        """
        full_name = f"{name} - {self.user_id_suffix}"
        self._data['name'] = full_name
        
        # normalizedName: lowercase with normalized whitespace
        self._data['normalizedName'] = full_name.lower().strip().replace('\s+', ' ')
        
        # normalizedNamePrefix: adaptive prefix (matches backend logic)
        self._data['normalizedNamePrefix'] = self._adaptive_prefix(full_name)
        
        return self
    
    def with_category(self, category: str) -> 'ItemBuilder':
        """
        Set category and generate normalizedCategory.
        
        Args:
            category: Item category
        
        Returns:
            self (for method chaining)
        """
        self._data['category'] = category
        # normalizedCategory: Title Case (matches backend logic)
        self._data['normalizedCategory'] = self._title_case(category)
        return self
    
    def with_price(self, price: float) -> 'ItemBuilder':
        """
        Set item price.
        
        Args:
            price: Item price
        
        Returns:
            self (for method chaining)
        """
        self._data['price'] = price
        return self
    
    def with_tags(self, tags: List[str]) -> 'ItemBuilder':
        """
        Set custom tags (will be merged with default tags).
        
        Args:
            tags: List of tag strings
        
        Returns:
            self (for method chaining)
        """
        # Always include 'seed' and 'v1.0' tags
        self._data['tags'] = list(set(tags + ['seed', 'v1.0']))
        return self
    
    def with_active_status(self, is_active: bool) -> 'ItemBuilder':
        """
        Set active status.
        
        Args:
            is_active: Whether item is active
        
        Returns:
            self (for method chaining)
        """
        self._data['is_active'] = is_active
        return self
    
    def build(self) -> Dict[str, Any]:
        """
        Build and return the complete item document.
        
        Validates that all required fields are present before returning.
        
        Returns:
            Dictionary ready for MongoDB insertion
        
        Raises:
            ValueError: If required fields are missing
        """
        # Validation: Ensure required fields are present
        required_fields = ['name', 'created_by', 'normalizedName']
        missing = [f for f in required_fields if f not in self._data]
        if missing:
            raise ValueError(f"Missing required fields: {missing}")
        
        return self._data.copy()
    
    @classmethod
    def build_many(cls, templates: List[Dict[str, Any]], user_id: str) -> List[Dict[str, Any]]:
        """
        Convenience method to build multiple items from templates.
        
        Args:
            templates: List of template dictionaries
            user_id: User ID for all items
        
        Returns:
            List of complete item documents
        
        Example:
            from lib.seed import SEED_ITEMS
            items = ItemBuilder.build_many(SEED_ITEMS, user_id)
        """
        return [
            cls(user_id).from_template(template).build()
            for template in templates
        ]

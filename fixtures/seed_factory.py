"""
Seed Data Factory

Purpose: Generate user-specific seed data dynamically
Uses factory pattern to create test data for different users
"""

import random
from typing import List, Dict, Any, Optional
from lib.seed import SEED_ITEMS


class SeedDataFactory:
    """
    Factory class for generating user-specific seed data
    """
    
    def __init__(self, seed_value: Optional[int] = None):
        """
        Initialize factory with optional seed for reproducibility
        
        Args:
            seed_value: Random seed for deterministic generation
        """
        if seed_value is not None:
            random.seed(seed_value)
    
    def create_item(self, 
                   name: str,
                   category: str,
                   item_type: str,
                   price: float,
                   description: Optional[str] = None,
                   is_active: bool = True,
                   **kwargs) -> Dict[str, Any]:
        """
        Create a single item with specified attributes
        
        Args:
            name: Item name
            category: Item category (Electronics, Software, Home, Books)
            item_type: PHYSICAL or DIGITAL
            price: Item price
            description: Optional description
            is_active: Whether item is active
            **kwargs: Additional item attributes
        
        Returns:
            Dictionary representing an item
        """
        item = {
            "name": name,
            "description": description or f"{category} item for testing",
            "item_type": item_type,
            "price": price,
            "category": category,
            "is_active": is_active,
            **kwargs
        }
        
        # Add type-specific fields
        if item_type == "PHYSICAL":
            if "weight" not in item:
                item["weight"] = round(random.uniform(0.1, 10.0), 1)
            if "dimensions" not in item:
                item["dimensions"] = {
                    "length": random.randint(5, 50),
                    "width": random.randint(5, 50),
                    "height": random.randint(2, 30)
                }
        elif item_type == "DIGITAL":
            if "download_url" not in item:
                item["download_url"] = f"https://example.com/{name.lower().replace(' ', '_')}"
            if "file_size" not in item:
                item["file_size"] = random.randint(50, 1000)
        
        return item
    
    def create_admin_items(self, count: int = 15) -> List[Dict[str, Any]]:
        """
        Generate items specific to admin users
        
        Args:
            count: Number of items to generate
        
        Returns:
            List of item dictionaries
        """
        items = []
        categories = ["Electronics", "Software", "Home", "Books"]
        
        for i in range(count):
            category = random.choice(categories)
            item_type = "PHYSICAL" if category in ["Electronics", "Home", "Books"] else "DIGITAL"
            if category == "Electronics":
                item_type = "PHYSICAL"  # Electronics must be PHYSICAL
            
            items.append(self.create_item(
                name=f"Admin Item {i+1}",
                category=category,
                item_type=item_type,
                price=round(random.uniform(10.0, 500.0), 2),
                description=f"Admin-specific {category.lower()} item for testing"
            ))
        
        return items
    
    def create_editor_items(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Generate items specific to editor users
        
        Args:
            count: Number of items to generate
        
        Returns:
            List of item dictionaries
        """
        items = []
        categories = ["Books", "Software", "Home"]
        
        for i in range(count):
            category = random.choice(categories)
            item_type = "PHYSICAL" if category in ["Home", "Books"] else "DIGITAL"
            
            items.append(self.create_item(
                name=f"Editor Item {i+1}",
                category=category,
                item_type=item_type,
                price=round(random.uniform(5.0, 200.0), 2),
                description=f"Editor-specific {category.lower()} item for testing"
            ))
        
        return items
    
    def create_viewer_items(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate items specific to viewer users (read-only, so this is for seed data)
        
        Args:
            count: Number of items to generate
        
        Returns:
            List of item dictionaries
        """
        items = []
        categories = ["Books", "Software"]
        
        for i in range(count):
            category = random.choice(categories)
            item_type = "PHYSICAL" if category == "Books" else "DIGITAL"
            
            items.append(self.create_item(
                name=f"Viewer Item {i+1}",
                category=category,
                item_type=item_type,
                price=round(random.uniform(10.0, 100.0), 2),
                description=f"Viewer seed data {category.lower()} item"
            ))
        
        return items
    
    def create_user_specific_items(self, user_email: str, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate items based on user email/role
        
        Args:
            user_email: User email address
            count: Optional count override
        
        Returns:
            List of item dictionaries
        """
        # Determine role from email
        if "admin" in user_email.lower():
            return self.create_admin_items(count or 15)
        elif "editor" in user_email.lower():
            return self.create_editor_items(count or 10)
        elif "viewer" in user_email.lower():
            return self.create_viewer_items(count or 5)
        else:
            # Default: return standard seed items
            return SEED_ITEMS.copy()
    
    def create_custom_items(self, 
                           user_email: str,
                           item_configs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create custom items based on provided configurations
        
        Args:
            user_email: User email (for naming)
            item_configs: List of item configuration dictionaries
        
        Returns:
            List of item dictionaries
        """
        items = []
        user_prefix = user_email.split("@")[0]  # e.g., "admin1" from "admin1@test.com"
        
        for i, config in enumerate(item_configs):
            item = self.create_item(
                name=config.get("name", f"{user_prefix} Custom Item {i+1}"),
                category=config.get("category", "Electronics"),
                item_type=config.get("item_type", "PHYSICAL"),
                price=config.get("price", 50.0),
                description=config.get("description"),
                is_active=config.get("is_active", True),
                **{k: v for k, v in config.items() 
                   if k not in ["name", "category", "item_type", "price", "description", "is_active"]}
            )
            items.append(item)
        
        return items


# Global factory instance (can be customized per test if needed)
default_factory = SeedDataFactory(seed_value=42)  # Deterministic by default


def get_user_seed_data(user_email: str, 
                      use_factory: bool = True,
                      custom_config: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """
    Get seed data for a specific user
    
    Args:
        user_email: User email address
        use_factory: If True, use factory to generate data. If False, use default SEED_ITEMS
        custom_config: Optional list of custom item configurations
    
    Returns:
        List of item dictionaries
    """
    if custom_config:
        factory = SeedDataFactory()
        return factory.create_custom_items(user_email, custom_config)
    
    if use_factory:
        return default_factory.create_user_specific_items(user_email)
    else:
        return SEED_ITEMS.copy()

"""
Seed Data Definitions

This module contains the SEED_ITEMS constant that defines the baseline test data.
The actual seed data creation is handled by MongoDB fixtures in tests/plugins/mongodb_fixtures.py
"""

SEED_ITEMS = [
    # Item 1: Alpha - Electronics, PHYSICAL (was DIGITAL - FIXED), Active, $25
    {
        "name": "Seed Item Alpha",
        "description": "Electronics item for search and filter testing",
        "item_type": "PHYSICAL",  # FIXED: Electronics MUST be PHYSICAL
        "price": 25.00,
        "category": "Electronics",
        "weight": 1.0,
        "dimensions": {"length": 10, "width": 8, "height": 5}
    },
    # Item 2: Beta - Software, DIGITAL, Active, $50
    {
        "name": "Seed Item Beta",
        "description": "Software item for search and filter testing",
        "item_type": "DIGITAL",
        "price": 50.00,
        "category": "Software",
        "download_url": "https://www.dhanunjaya.space/assets/resume.pdf",
        "file_size": 200
    },
    # Item 3: Gamma - Home, PHYSICAL, Active, $75
    {
        "name": "Seed Item Gamma",
        "description": "Home item for category filter testing",
        "item_type": "PHYSICAL",
        "price": 75.00,
        "category": "Home",
        "weight": 2.5,
        "dimensions": {"length": 15, "width": 10, "height": 8}
    },
    # Item 4: Delta - Electronics, PHYSICAL, Active, $100
    {
        "name": "Seed Item Delta",
        "description": "Electronics physical item for testing",
        "item_type": "PHYSICAL",
        "price": 100.00,
        "category": "Electronics",
        "weight": 3.0,
        "dimensions": {"length": 20, "width": 15, "height": 10}
    },
    # Item 5: Epsilon - Books, DIGITAL, Active, $15
    {
        "name": "Seed Item Epsilon",
        "description": "Books category item for filter testing",
        "item_type": "DIGITAL",
        "price": 15.00,
        "category": "Books",
        "download_url": "https://www.dhanunjaya.space/",
        "file_size": 50
    },
    # Item 6: Zeta - Software, DIGITAL, Inactive, $200
    {
        "name": "Seed Item Zeta",
        "description": "Inactive software item for status filter testing",
        "item_type": "DIGITAL",
        "price": 200.00,
        "category": "Software",
        "download_url": "https://example.com/zeta",
        "file_size": 500,
        "is_active": False  # Inactive status
    },
    # Item 7: Eta - Home, PHYSICAL, Active, $30
    {
        "name": "Seed Item Eta",
        "description": "Home item for price sort testing",
        "item_type": "PHYSICAL",
        "price": 30.00,
        "category": "Home",
        "weight": 1.0,
        "dimensions": {"length": 12, "width": 8, "height": 6}
    },
    # Item 8: Theta - Electronics, PHYSICAL (was DIGITAL - FIXED), Active, $500 (Highest price)
    {
        "name": "Seed Item Theta",
        "description": "Premium electronics item for price sort testing",
        "item_type": "PHYSICAL",  # FIXED: Electronics MUST be PHYSICAL
        "price": 500.00,
        "category": "Electronics",
        "weight": 5.0,
        "dimensions": {"length": 40, "width": 30, "height": 20}
    },
    # Item 9: Iota - Books, PHYSICAL, Active, $10
    {
        "name": "Seed Item Iota",
        "description": "Books physical item for testing",
        "item_type": "PHYSICAL",
        "price": 10.00,
        "category": "Books",
        "weight": 0.5,
        "dimensions": {"length": 8, "width": 6, "height": 2}
    },
    # Item 10: Kappa - Software, DIGITAL, Active, $150
    {
        "name": "Seed Item Kappa",
        "description": "Software item for pagination testing",
        "item_type": "DIGITAL",
        "price": 150.00,
        "category": "Software",
        "download_url": "https://example.com/kappa",
        "file_size": 300
    },
    # Item 11: Lambda - Home, PHYSICAL, Inactive, $5 (Lowest price)
    {
        "name": "Seed Item Lambda",
        "description": "Inactive home item for status and price testing",
        "item_type": "PHYSICAL",
        "price": 5.00,
        "category": "Home",
        "weight": 0.3,
        "dimensions": {"length": 5, "width": 5, "height": 3},
        "is_active": False  # Inactive status
    }
]

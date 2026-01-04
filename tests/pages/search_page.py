from .base_page import BasePage, expect
import re

class SearchPage(BasePage):
    """
    Page Object for the Search & Discovery Page (/items).
    Handles searching, filtering, sorting, and pagination.
    """
    
    # --- Locators ---
    READY_STATE = '[data-test-ready="true"]'
    ITEMS_TABLE = "items-table"
    ITEMS_COUNT_ATTR = "[data-test-items-count]"
    
    SEARCH_INPUT = "item-search"
    SEARCH_READY = '[data-testid="item-search"][data-test-search-state="ready"]'
    
    FILTER_STATUS = "filter-status"
    FILTER_CATEGORY = "filter-category"
    SORT_PRICE = "sort-price"
    CLEAR_FILTERS = "clear-filters"
    
    PAGINATION_LIMIT = "pagination-limit"
    PAGINATION_INFO = "pagination-info"
    # Desktop selector for next button (more stable)
    PAGINATION_NEXT = '.hidden.sm\\:flex [data-testid="pagination-next"]'
    
    # Item Rows
    ITEM_ROW_PREFIX = '[data-testid^="item-row-"]'
    ITEM_NAME_PREFIX = '[data-testid^="item-name-"]'
    ITEM_PRICE_PREFIX = '[data-testid^="item-price-"]'
    ITEM_STATUS_PREFIX = '[data-testid^="item-status-"]'
    ITEM_CATEGORY_PREFIX = '[data-testid^="item-category-"]'

    # --- Actions ---

    def wait_for_ready(self):
        self.page.wait_for_selector(self.READY_STATE, timeout=10000)

    def get_items_count(self) -> int:
        attr = self.page.get_attribute(self.ITEMS_COUNT_ATTR, 'data-test-items-count')
        return int(attr) if attr else 0

    def search(self, term: str):
        self.get_by_test_id(self.SEARCH_INPUT).fill(term)
        # Wait for search state to become ready (debounce/api)
        self.page.wait_for_selector(self.SEARCH_READY, timeout=10000)

    def filter_by_status(self, status: str):
        self.get_by_test_id(self.FILTER_STATUS).select_option(status)
        self.wait_for_ready()

    def filter_by_category(self, category: str):
        self.get_by_test_id(self.FILTER_CATEGORY).select_option(category)
        self.wait_for_ready()

    def sort_by_price(self):
        self.get_by_test_id(self.SORT_PRICE).click()
        self.wait_for_ready()

    def clear_filters(self):
        self.get_by_test_id(self.CLEAR_FILTERS).click()
        self.wait_for_ready()

    # --- Pagination ---

    def set_pagination_limit(self, limit: str):
        self.get_by_test_id(self.PAGINATION_LIMIT).select_option(limit)
        self.wait_for_ready()

    def get_pagination_info(self) -> str:
        return self.get_by_test_id(self.PAGINATION_INFO).text_content()

    def go_to_next_page(self) -> bool:
        """
        Clicks next page if enabled. Returns True if clicked, False if disabled/hidden.
        """
        self.wait_for_ready()
        btn = self.page.locator(self.PAGINATION_NEXT)
        btn.wait_for(state="visible", timeout=5000)
        
        if btn.is_enabled():
            btn.click()
            self.wait_for_ready()
            return True
        return False

    # --- Data Retrieval for Validation ---

    def get_all_item_names(self):
        return [loc.text_content() for loc in self.page.locator(self.ITEM_NAME_PREFIX).all()]

    def get_all_item_statuses(self):
        return [loc.text_content() for loc in self.page.locator(self.ITEM_STATUS_PREFIX).all()]

    def get_all_item_categories(self):
        return [loc.text_content() for loc in self.page.locator(self.ITEM_CATEGORY_PREFIX).all()]

    def get_all_item_prices_float(self):
        prices = []
        for loc in self.page.locator(self.ITEM_PRICE_PREFIX).all():
            text = loc.text_content()
            # Extract number from "$123.45"
            match = re.search(r'[\d.]+', text)
            if match:
                prices.append(float(match.group()))
        return prices

    def is_edit_button_visible(self, item_id: str) -> bool:
        return self.get_by_test_id(f"edit-item-{item_id}").is_visible()

    def is_delete_button_visible(self, item_id: str) -> bool:
        return self.get_by_test_id(f"delete-item-{item_id}").is_visible()

from .base_page import BasePage, expect

class CreateItemPage(BasePage):
    """
    Page Object for the Create Item Page.
    Handles form interaction for all item schemas (Digital, Physical, Service).
    """
    
    # --- Locators ---
    # Common
    NAME_INPUT = "item-name"
    DESC_INPUT = "item-description"
    PRICE_INPUT = "item-price"
    CATEGORY_INPUT = "item-category"
    TYPE_SELECT = "item-type"
    SUBMIT_BTN = "create-item-submit"
    TOAST_SUCCESS = "toast-success"
    
    # Digital
    DIGITAL_SECTION = "digital-fields"
    DOWNLOAD_URL_INPUT = "item-download-url"
    FILE_SIZE_INPUT = "item-file-size"
    
    # Physical
    PHYSICAL_SECTION = "physical-fields"
    WEIGHT_INPUT = "item-weight"
    LENGTH_INPUT = "item-dimension-length"
    WIDTH_INPUT = "item-dimension-width"
    HEIGHT_INPUT = "item-dimension-height"
    
    # Service
    SERVICE_SECTION = "service-fields"
    DURATION_INPUT = "item-duration-hours"

    # --- Actions ---

    def wait_for_ready(self, timeout=10000):
        """Waits for the page to be ready (Name input visible)."""
        self.get_by_test_id(self.NAME_INPUT).wait_for(state="visible", timeout=timeout)

    def fill_common_fields(self, name: str, description: str, price: str, category: str):
        """Fills the fields common to all item types."""
        self.get_by_test_id(self.NAME_INPUT).fill(name)
        self.get_by_test_id(self.DESC_INPUT).fill(description)
        self.get_by_test_id(self.PRICE_INPUT).fill(price)
        self.get_by_test_id(self.CATEGORY_INPUT).fill(category)

    def select_type(self, item_type: str):
        """Selects the item type (DIGITAL, PHYSICAL, SERVICE) and waits for conditional fields."""
        self.get_by_test_id(self.TYPE_SELECT).select_option(item_type)
        
        # Wait for the corresponding section to appear
        if item_type == "DIGITAL":
            self.get_by_test_id(self.DIGITAL_SECTION).wait_for(state="visible")
        elif item_type == "PHYSICAL":
            self.get_by_test_id(self.PHYSICAL_SECTION).wait_for(state="visible")
        elif item_type == "SERVICE":
            # Note: Selector might be 'service-fields' or similar based on previous recon
            # Based on test_create_item.py: "service-fields"
            self.get_by_test_id(self.SERVICE_SECTION).wait_for(state="visible")

    def fill_digital_fields(self, url: str, size: str):
        self.get_by_test_id(self.DOWNLOAD_URL_INPUT).fill(url)
        self.get_by_test_id(self.FILE_SIZE_INPUT).fill(size)

    def fill_physical_fields(self, weight: str, length: str, width: str, height: str):
        self.get_by_test_id(self.WEIGHT_INPUT).fill(weight)
        self.get_by_test_id(self.LENGTH_INPUT).fill(length)
        self.get_by_test_id(self.WIDTH_INPUT).fill(width)
        self.get_by_test_id(self.HEIGHT_INPUT).fill(height)

    def fill_service_fields(self, duration: str):
        self.get_by_test_id(self.DURATION_INPUT).fill(duration)

    def submit(self):
        """Clicks the submit button."""
        self.get_by_test_id(self.SUBMIT_BTN).click()

    def verify_success(self, timeout=10000):
        """Verifies the success toast and redirection."""
        toast = self.get_by_test_id(self.TOAST_SUCCESS)
        expect(toast).to_be_visible(timeout=timeout)
        expect(toast).to_contain_text("Item created")
        expect(self.page).to_have_url("https://testing-box.vercel.app/items")

from playwright.sync_api import Page, Locator, expect

class BasePage:
    """
    Abstracts the Playwright Page object.
    Centralizes common actions (navigation, strict waiting, obtaining locators).
    """

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str):
        """Navigate to a relative path from the base URL."""
        # Using built-in basic join logic or relying on base_url fixture implicitly if simpler
        # But since we are wrapping page, we might just call goto directly.
        # Assuming base_url is set in pytest.ini or passed to browser context.
        # If path starts with /, just go there.
        self.page.goto(path)

    def get_by_test_id(self, test_id: str) -> Locator:
        """
        Convenience wrapper for getting elements by data-testid.
        Ensures strict mode is compliant by default.
        """
        return self.page.get_by_test_id(test_id)

    def wait_for_url(self, url_part: str):
        """Wait for the URL to contain a specific string (smart wait)."""
        self.page.wait_for_url(f"**/{url_part}**")

from playwright.sync_api import Page

class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        # Locators
        self.EMAIL_INPUT = '[data-testid="login-email"]'
        self.PASSWORD_INPUT = '[data-testid="login-password"]'
        self.SUBMIT_BUTTON = '[data-testid="login-submit"]'
        self.DASHBOARD_INDICATOR = "**/dashboard"

    def navigate(self, base_url: str):
        self.page.goto(f"{base_url}/login")

    def login(self, email: str, password: str):
        self.page.fill(self.EMAIL_INPUT, email)
        self.page.fill(self.PASSWORD_INPUT, password)
        self.page.click(self.SUBMIT_BUTTON)

    def wait_for_success(self):
        self.page.wait_for_url(self.DASHBOARD_INDICATOR, timeout=15000)

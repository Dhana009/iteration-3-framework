import pytest

class PageFactory:
    """
    Lazy-loading factory for Page Objects.
    Usage: pages.login.login()
    """
    def __init__(self, page):
        self.page = page
        self._login = None
        self._create_item = None
        self._search = None

    @property
    def login(self):
        from lib.pages.login_page import LoginPage
        if not self._login:
            self._login = LoginPage(self.page)
        return self._login

    @property
    def create_item(self):
        from lib.pages.create_item_page import CreateItemPage
        if not self._create_item:
            self._create_item = CreateItemPage(self.page)
        return self._create_item

    @property
    def search(self):
        from lib.pages.search_page import SearchPage
        if not self._search:
            self._search = SearchPage(self.page)
        return self._search

@pytest.fixture
def pages(page):
    """
    Fixture that returns a PageFactory.
    Requires the standard playwright 'page' fixture.
    """
    return PageFactory(page)

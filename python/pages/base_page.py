from playwright.sync_api import Page


class BasePage:
    """Base class for all page objects"""

    def __init__(self, page: Page):
        self.page = page

    def wait_for_element(self, selector: str, timeout: int = 5000):
        """Wait for element to be visible"""
        self.page.wait_for_selector(selector, timeout=timeout)

    def fill_field(self, selector: str, text: str):
        """Fill a text field"""
        self.page.fill(selector, text)

    def click_button(self, selector: str):
        """Click a button"""
        self.page.click(selector)

    def get_text(self, selector: str) -> str:
        """Get element text"""
        return self.page.text_content(selector)

    def is_visible(self, selector: str) -> bool:
        """Check if element is visible"""
        return self.page.is_visible(selector)

    def wait_for_load_state(self, state: str = "networkidle"):
        """Wait for page to load"""
        self.page.wait_for_load_state(state)

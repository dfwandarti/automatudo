from playwright.sync_api import Page, Locator
from .display_name_to_test_id import DisplayNameToTestId
from .display_name_to_xpath import DisplayNameToXpath


class PageField:
    display_name: str = None
    page: Page = None
    data_test_id: str = None
    xpath: str = None
    locator: Locator

    def __init__(self, page: Page, display_name: str):
        super().__init__()
        self.page = page
        self.display_name = display_name
        self.locator: Locator = self.get_locator(display_name)

    def get_locator(self, display_name: str):
        self.data_test_id: str | None = DisplayNameToTestId.get_data_test_id(display_name)
        if self.data_test_id is not None:
            return self.page.get_by_test_id(self.data_test_id)

        self.xpath: str | None = DisplayNameToXpath.get_xpath(display_name)
        if self.xpath is not None:
            return self.page.locator(self.xpath)

        raise ValueError(f"Display name '{display_name}' not found in mapping. Review display_name_to_test_id.py and display_name_to_xpath.py.")

    @classmethod
    def from_display_name(cls, display_name: str) -> PageField | None:
        return None

    def press_sequentially(self, text: str) -> None:
        self.locator.press_sequentially(text, delay=300)

    def click(self) -> None:
        self.locator.click(delay=300)

    def get_text(self) -> str | None:
        self.confirm_is_visible()
        return self.locator.text_content()

    def get_input_text(self):
        self.confirm_is_visible()
        self.confirm_is_enabled()
        return self.locator.input_value()

    def confirm_is_visible(self):
        if not self.locator.is_visible():
            raise ValueError(f"Display name '{self.display_name}' not visible in page.")

    def confirm_is_enabled(self):
        if not self.locator.is_enabled():
            raise ValueError(f"Display name '{self.display_name}' not enabled in page.")


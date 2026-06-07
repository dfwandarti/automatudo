from playwright.sync_api import Page, Locator
from .display_name_to_test_id import DisplayNameToTestId


class PageField:
    display_name: str = None
    page: Page = None
    data_test_id: str = None
    locator: Locator

    def __init__(self, page: Page, display_name: str):
        super().__init__()
        self.page = page
        self.display_name = display_name
        self.data_test_id: str | None = DisplayNameToTestId.get_data_test_id(display_name)
        if self.data_test_id is None:
            raise ValueError(f"Display name '{display_name}' not found in mapping. Review display_name_to_test_id.py.")

        self.locator: Locator = self.page.get_by_test_id(self.data_test_id)

    @classmethod
    def from_display_name(cls, display_name: str) -> PageField | None:
        return None

    def press_sequentially(self, text: str) -> None:
        self.locator.press_sequentially(text, delay=300)

    def click(self) -> None:
        self.locator.click(delay=300)

    def get_text(self) -> str | None:
        return self.locator.text_content()

    def get_input_text(self):
        return self.locator.input_value()

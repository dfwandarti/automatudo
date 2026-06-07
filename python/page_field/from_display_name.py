from playwright.sync_api import Page

from config.browser_config import BrowserConfig
from page_field.page_field import PageField
from page_field.page_field_entrar import PageFieldEntrar

class PageFieldFactory:
    @staticmethod
    def from_display_name(page: Page, display_name: str) -> PageField:
        if display_name == "login gas online - botão entrar" and BrowserConfig.is_responsive():
            return PageFieldEntrar(page, display_name)

        return PageField(page, display_name)

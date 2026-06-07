from playwright.sync_api import Page

from .page_field import PageField


class PageFieldEntrar(PageField):
    def __init__(self, page: Page, display_name: str) -> None:
        super().__init__(page, "login gas online - botão entrar")

    def click(self):
        self.page.locator("//*[@class='menu-icon']").click(delay=300)
        super().click()
from playwright.sync_api import Page

from python.page_field.from_display_name import PageFieldFactory
from python.locators.login_locators import LoginLocators
from python.pages.base_page import BasePage


class LoginPageGasOnline(BasePage):
    """Login Page Object"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = LoginLocators()

    def navigate_to(self):
        self.page.goto("https://gasonline.galp.com/")
        PageFieldFactory.from_display_name(self.page, "login gas online - botão aceitar cookies").click()

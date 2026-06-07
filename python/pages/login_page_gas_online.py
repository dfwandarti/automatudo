from playwright.sync_api import Page

from page_field.page_field import PageField
from python.pages.base_page import BasePage
from python.locators.login_locators import LoginLocators


class LoginPageGasOnline(BasePage):
    """Login Page Object"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = LoginLocators()

    def navigate_to(self):
        self.page.goto("https://gasonline.galp.com/")
        PageField(self.page, "login gas online - botão aceitar cookies").click()


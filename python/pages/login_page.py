from playwright.sync_api import Page

from python.pages.base_page import BasePage
from python.locators.login_locators import LoginLocators


class LoginPage(BasePage):
    """Login Page Object"""

    def __init__(self, page: Page):
        super().__init__(page)

    def navigate_to(self):
        self.page.goto("https://dfwandarti.github.io/automatudo/static/login.html")


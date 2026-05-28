from playwright.sync_api import Page

from python.pages.base_page import BasePage
from python.locators.login_locators import LoginLocators


class LoginPage(BasePage):
    """Login Page Object"""

    def __init__(self, page: Page):
        super().__init__(page)
        self.locators = LoginLocators()

    def login(self, username: str, password: str):
        """Login with credentials"""
        self.fill_field(self.locators.USERNAME_INPUT, username)
        self.fill_field(self.locators.PASSWORD_INPUT, password)
        self.click_button(self.locators.LOGIN_BUTTON)

    def is_success_message_visible(self) -> bool:
        """Check if success message is displayed"""
        try:
            self.wait_for_element(self.locators.SUCCESS_MESSAGE, timeout=5000)
            return True
        except Exception:
            return False

    def is_invalid_message_visible(self) -> bool:
        """Check if invalid credentials message is displayed"""
        try:
            self.wait_for_element(self.locators.INVALID_MESSAGE, timeout=5000)
            return True
        except Exception:
            return False

    def get_success_message(self) -> str:
        """Get success message text"""
        return self.get_text(self.locators.SUCCESS_MESSAGE)

    def get_invalid_message(self) -> str:
        """Get invalid message text"""
        return self.get_text(self.locators.INVALID_MESSAGE)

    def verify_login_success(self):
        """Verify login was successful by checking success message"""
        assert self.is_success_message_visible(), "Success message not found!"

    def verify_invalid_credentials(self):
        """Verify invalid credentials message is shown"""
        assert self.is_invalid_message_visible(), "Invalid credentials message not found!"

    def navigate_to(self):
        self.page.goto("https://dfwandarti.github.io/automatudo/static/login.html")


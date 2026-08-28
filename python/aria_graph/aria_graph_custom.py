from playwright.sync_api import Page

from python.flowchart.parser import Node
from python.pages.login_page import LoginPage


def navigate_to_initial_page(page) -> None:
    login_page = LoginPage(page)
    login_page.navigate_to()

def hook_fillform_before(current_node: Node, page: Page, form_filling: dict) -> None:
    """
    Hook function called before filling a form.
    Can be used to modify the form_filling dictionary or perform other actions.
    """
    pass


def hook_fillform_after(current_node: Node, page: Page, form_filling: dict) -> None:
    """
    Hook function called after filling a form.
    Can be used to perform actions based on the filled form or modify the form_filling dictionary.
    """
    pass


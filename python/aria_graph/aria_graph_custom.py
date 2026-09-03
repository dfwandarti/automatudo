from playwright.sync_api import Page

from python.flowchart.parser import Node
from python.pages.login_page import LoginPage
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Callable, TypeAlias

@dataclass
class HookArguments:
    page: Page
    node: Node
    form_filling: dict[str, str]
    
HookFunction: TypeAlias = Callable[[HookArguments], bool]
    
class AriaGraphCustomBase:
    @abstractmethod
    def navigate_to_initial_page(self, page) -> None:
        pass
    
    @abstractmethod
    def get_hook_before_navigation(self) -> dict[str, HookFunction]:
        pass

    @abstractmethod
    def get_hook_after_navigation(self) -> dict[str, HookFunction]:
        pass
    
    @abstractmethod
    def get_handle_transition(self) -> dict[str, HookFunction]:
        pass


class AriaGraphCustomImpl(AriaGraphCustomBase):
    def navigate_to_initial_page(self, page: Page) -> None:
        login_page = LoginPage(page)
        login_page.navigate_to()

    def get_hook_before_navigation(self) -> dict[str, HookFunction]:
        return {}

    def get_hook_after_navigation(self) -> dict[str, HookFunction]:
        return {}
    
    def get_handle_transition(self) -> dict[str, HookFunction]:
        return {}


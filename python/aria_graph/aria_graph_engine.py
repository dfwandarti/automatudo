import logging
import re

from playwright.sync_api import Locator, Page

from python.aria_graph import aria_graph_custom
from python.flowchart.parser import FlowchartTree, Node, Transition
from python.aria_graph.aria_graph_custom import AriaGraphCustomBase, HookFunction, HookArguments

class AriaGraphEngine:
    FLOWCHART_PATH: str = "LOGIN_FLOW.md"
    MAX_BUTTON_ATTEMPTS: int = 3
    MAX_SCREEN_ATTEMPTS: int = 3
    WAIT_BETWEEN_ATTEMPTS_MS: int = 1000
    FILLABLE_ARIA_ROLES: list[str] = [
        "textbox", "searchbox", "spinbutton",
        "checkbox", "radio",
        "combobox", "listbox", "option",
    ]
    CLICKABLE_ARIA_ROLES: list[str] = [
        "button", "link", "menuitem", "tab", "treeitem"
    ]

    _page: Page
    _form_filling: dict[str, str]
    _aria_graph_custom: AriaGraphCustomBase

    def __init__(self, page: Page, form_filling: dict[str, str], aria_graph_custom: AriaGraphCustomBase) -> None:
        self._page = page
        self._form_filling = form_filling
        self._aria_graph_custom = aria_graph_custom

    def loop_until_reaches_end_of_flow(self, route_node_label: str) -> None:
        path = self._find_path(route_node_label)

        for transition in path:
            self.handle_one_screen(transition)
            
        self._handle_last_screen(path[-1].node)

    def _find_path(self, route_node_label):
        tree: FlowchartTree = FlowchartTree.from_file(self.FLOWCHART_PATH)
        self._aria_graph_custom.navigate_to_initial_page(self._page)

        destination: Node | None = tree.find_by_label(route_node_label)
        if destination is None:
            raise AssertionError(f"Node with title '{route_node_label}' not found in {self.FLOWCHART_PATH}")

        path: list[Transition] = tree.path(tree.root(), destination)
        return path

    def _handle_last_screen(self, last_node: Node) -> None:
        self._fillform()
        self._call_hook_if_exists(self._aria_graph_custom.get_hook_before_navigation(), last_node)

    def handle_one_screen(self, transition: Transition):
        current_node: Node = transition.node
        button_label: str = transition.label
        
        if button_label == "HOOK":
            called_hook: bool = self._call_hook_if_exists(self._aria_graph_custom.get_handle_transition(), current_node)
            if not called_hook: raise AssertionError(f"Didn't find a hook for transition with label 'HOOK' and node label '{current_node.label}'. Check you implementation of AriaGraphCustomBase.")
            return
        
        self._fillform()

        self._call_hook_if_exists(self._aria_graph_custom.get_hook_before_navigation(), current_node)
        
        self._clickable_with_retry(button_label)
        self._wait_for_screen_with_retry(transition.node.label)
            
        self._call_hook_if_exists(self._aria_graph_custom.get_hook_after_navigation(), current_node)

    def _call_hook_if_exists(self, dict_of_hooks: dict[str, HookFunction], current_node: Node) -> bool:
        if current_node.label not in dict_of_hooks:
            return False
        
        hook_before: HookFunction = dict_of_hooks[current_node.label]
        args: HookArguments = HookArguments(self._page, current_node, self._form_filling)
        hook_before(args)
        return True

    def _fillform(self) -> None:
        key: str
        value: str
        for key, value in self._form_filling.items():
            element, role = self._find_field_by_key(key)
            if element is None or role is None:
                continue
            try:
                self._fill_element(element, role, value)
            except Exception as e:
                logging.warning(
                    "Failed to fill field (role '%s') found by key '%s': %s",
                    role, key, e,
                )

    def _find_field_by_key(self, key: str) -> tuple[Locator, str] | tuple[None, None]:
        pattern: re.Pattern[str] = re.compile(re.escape(key), re.IGNORECASE)
        role: str
        for role in self.FILLABLE_ARIA_ROLES:
            locator: Locator = self._page.get_by_role(role, name=pattern)
            if locator.count() > 0:
                return locator.first, role
        return None, None

    def _fill_element(self, element: Locator, role: str, value: str) -> None:
        if role in ("textbox", "searchbox", "spinbutton"):
            element.fill(value)
        elif role == "checkbox":
            element.set_checked(self._is_truthy_value(value))
        elif role == "radio":
            element.check()
        elif role in ("combobox", "listbox"):
            element.select_option(value)
        elif role == "option":
            element.click()
        else:
            logging.warning("ARIA role '%s' not supported for automatic filling", role)

    def _is_truthy_value(self, value: str) -> bool:
        return value.strip().lower() in ("true", "1", "sim", "yes", "verdadeiro")

    def _clickable_with_retry(self, label: str) -> None:
        last_error: Exception | None = None
        attempt: int
        for attempt in range(1, self.MAX_BUTTON_ATTEMPTS + 1):
            try:
                clickable: Locator | None = self._get_clickable(label)
                if clickable is not None:
                    clickable.click(timeout=3000)
                return
            except Exception as e:
                last_error = e
                logging.warning(
                    "Attempt %d/%d to click button '%s' failed: %s",
                    attempt, self.MAX_BUTTON_ATTEMPTS, label, e,
                )
                self._page.wait_for_timeout(self.WAIT_BETWEEN_ATTEMPTS_MS)
        raise AssertionError(f"Button '{label}' not found after {self.MAX_BUTTON_ATTEMPTS} attempts: {last_error}")

    def _get_clickable(self, label: str) -> Locator | None:
        pattern: re.Pattern[str] = re.compile(re.escape(label), re.IGNORECASE)
        role: str
        for role in self.CLICKABLE_ARIA_ROLES:
            clickable: Locator = self._page.get_by_role(role, name=pattern)
            if clickable.count() > 0:
                return clickable.first
        return None

    def _wait_for_screen_with_retry(self, expected_title: str) -> None:
        current_screen: str | None = None
        attempt: int
        for attempt in range(1, self.MAX_SCREEN_ATTEMPTS + 1):
            current_screen = self._read_screen_title()
            if current_screen.__contains__(expected_title):
                return
            logging.info(
                "Current screen is '%s', waiting for '%s' (attempt %d/%d)",
                current_screen, expected_title, attempt, self.MAX_SCREEN_ATTEMPTS,
            )
            self._page.wait_for_timeout(self.WAIT_BETWEEN_ATTEMPTS_MS)
        raise AssertionError(f"Expected to reach screen '{expected_title}' but currently at '{current_screen}'")

    def _read_screen_title(self) -> str:
        title: str = self._page.title()
        heading_text: str = self._page.get_by_role("heading", level=1).inner_text().strip()
        return f"{title} / {heading_text}"

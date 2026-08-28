import logging
import re

from playwright.sync_api import Locator, Page

from python.aria_graph import aria_graph_custom
from python.flowchart.parser import FlowchartTree, Node, Transition


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

    _page: Page
    _form_filling: dict[str, str]

    def __init__(self, page: Page, form_filling: dict[str, str]) -> None:
        self._page = page
        self._form_filling = form_filling

    def loop_until_reaches_end_of_flow(self, route_node_label: str) -> None:
        tree: FlowchartTree = FlowchartTree.from_file(self.FLOWCHART_PATH)
        aria_graph_custom.navigate_to_initial_page(self._page)

        destination: Node | None = tree.find_by_label(route_node_label)
        if destination is None:
            raise AssertionError(f"Node with title '{route_node_label}' not found in {self.FLOWCHART_PATH}")

        path: list[Transition] = tree.path(tree.root(), destination)

        for transition in path:
            current_node: Node = transition.node

            aria_graph_custom.hook_fillform_before(current_node, self._page, self._form_filling)
            self._fillform()

            button_label: str = transition.label
            self._clickable_with_retry(button_label)
            self._wait_for_screen_with_retry(transition.node.label)
            aria_graph_custom.hook_fillform_after(current_node, self._page, self._form_filling)

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
        for role in ("button", "link", "menuitem", "tab", "treeitem"):
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

import logging
import re
from enum import Enum

from playwright.sync_api import Locator, Page

from python.aria_graph import aria_graph_custom
from python.flowchart.parser import FlowchartTree, Node, Transition
from python.aria_graph.aria_graph_custom import AriaGraphCustomBase, HookFunction, HookArguments


class FindFieldMode(str, Enum):
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"

class ValidatePageName(str, Enum):
    NO = "no"
    YES = "yes"


class FormFiller:
    FILLABLE_ARIA_ROLES: list[str] = [
        "textbox", "searchbox", "spinbutton",
        "checkbox", "radio",
        "combobox", "listbox", "option",
    ]

    def __init__(self, page: Page, form_filling: dict[str, str]) -> None:
        self._page = page
        self._form_filling = form_filling

    def fill_form(self, find_field_mode: FindFieldMode = FindFieldMode.MODERATE) -> None:
        if find_field_mode == FindFieldMode.MODERATE:
            self._fill_form_moderate()
        else:
            self._fill_form_aggressive()
        self._page.keyboard.press("Tab")  # Move focus to the next field after filling

    def _fill_form_moderate(self) -> None:
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

    def _fill_form_aggressive(self) -> None:
        for role in self.FILLABLE_ARIA_ROLES:
            locator: Locator = self._page.get_by_role(role)
            for element in locator.all():
                possible_name: str = self._build_possible_name(element)
                matched_key: str | None = self._match_key(possible_name)
                if matched_key is None:
                    continue
                value: str = self._form_filling[matched_key]
                try:
                    self._fill_element(element, role, value)
                except Exception as e:
                    logging.warning(
                        "Failed to fill field (role '%s') matched by key '%s': %s",
                        role, matched_key, e,
                    )

    def _match_key(self, possible_name: str) -> str | None:
        for key in self._form_filling:
            if key.lower() in possible_name:
                return key
        return None

    def _build_possible_name(self, element: Locator) -> str:
        parts: list[str | None] = [
            element.get_attribute("aria-label"),
            self._get_label_text(element),
            element.get_attribute("placeholder"),
            self._get_labelledby_text(element),
            element.get_attribute("title"),
        ]
        return " / ".join(part for part in parts if part).lower()

    def _get_label_text(self, element: Locator) -> str | None:
        element_id: str | None = element.get_attribute("id")
        if element_id:
            label_for: Locator = self._page.locator(
                f'label[for="{element_id}"]')
            if label_for.count() > 0:
                text: str | None = label_for.first.text_content()
                if text:
                    return text.strip()

        ancestor_label: Locator = element.locator("xpath=ancestor::label[1]")
        if ancestor_label.count() > 0:
            text = ancestor_label.first.text_content()
            if text:
                return text.strip()
        return None

    def _get_labelledby_text(self, element: Locator) -> str | None:
        labelledby: str | None = element.get_attribute("aria-labelledby")
        if not labelledby:
            return None
        texts: list[str] = []
        for ref_id in labelledby.split():
            ref_element: Locator = self._page.locator(f'[id="{ref_id}"]')
            if ref_element.count() > 0:
                text: str | None = ref_element.first.text_content()
                if text:
                    texts.append(text.strip())
        return " ".join(texts) if texts else None

    def _find_field_by_key(self, key: str) -> tuple[Locator, str] | tuple[None, None]:
        pattern: re.Pattern[str] = self._build_case_insensitive_pattern(key)
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
            element.fill(value)
            element.select_option(value)
        elif role == "option":
            element.click()
        else:
            logging.warning(
                "ARIA role '%s' not supported for automatic filling", role)        

    @staticmethod
    def _is_truthy_value(value: str) -> bool:
        return value.strip().lower() in ("true", "1", "sim", "yes", "verdadeiro")

    @staticmethod
    def _build_case_insensitive_pattern(text: str) -> re.Pattern[str]:
        return re.compile(re.escape(text), re.IGNORECASE)


class HookDispatcher:
    def __init__(self, page: Page, form_filling: dict[str, str]) -> None:
        self._page = page
        self._form_filling = form_filling

    def call_hook_if_exists(self, dict_of_hooks: dict[str, HookFunction], current_node: Node) -> bool:
        if current_node.label not in dict_of_hooks:
            return False

        hook: HookFunction = dict_of_hooks[current_node.label]
        args: HookArguments = HookArguments(
            self._page, current_node, self._form_filling)
        hook(args)
        return True


class AriaGraphEngine:
    HOOK_TRANSITION_LABEL: str = "HOOK"
    MAX_BUTTON_ATTEMPTS: int = 3
    MAX_SCREEN_ATTEMPTS: int = 3
    WAIT_BETWEEN_ATTEMPTS_MS: int = 1000
    CLICKABLE_ARIA_ROLES: list[str] = [
        "button", "link", "menuitem", "tab", "treeitem"
    ]

    _page: Page
    _aria_graph_custom: AriaGraphCustomBase
    _flowchart_path: str
    _form_filler: FormFiller
    _hook_dispatcher: HookDispatcher
    _find_field_mode: FindFieldMode
    _validate_page_name: ValidatePageName

    def __init__(self,
                 page: Page,
                 form_filling: dict[str, str],
                 aria_graph_custom: AriaGraphCustomBase,
                 flowchart_path: str = "LOGIN_FLOW.md",
                 find_field_mode: FindFieldMode = FindFieldMode.MODERATE,
                 validate_page_name: ValidatePageName = ValidatePageName.YES) -> None:
        self._page = page
        self._aria_graph_custom = aria_graph_custom
        self._flowchart_path = flowchart_path
        self._form_filler = FormFiller(page, form_filling)
        self._hook_dispatcher = HookDispatcher(page, form_filling)
        self._find_field_mode = find_field_mode
        self._validate_page_name = validate_page_name

    def loop_until_reaches_end_of_flow(self, route_node_label: str) -> None:
        self._aria_graph_custom.navigate_to_initial_page(self._page)
        path = self._find_path(route_node_label)

        for transition in path:
            self._handle_one_screen(transition)

        self._handle_last_screen(path[-1].node)

    def _find_path(self, route_node_label):
        tree: FlowchartTree = FlowchartTree.from_file(self._flowchart_path)

        destination: Node | None = tree.find_by_label(route_node_label)
        if destination is None:
            raise AssertionError(
                f"Node with title '{route_node_label}' not found in {self._flowchart_path}")

        path: list[Transition] = tree.path(tree.root(), destination)
        return path

    def _handle_last_screen(self, last_node: Node) -> None:
        self._form_filler.fill_form(find_field_mode=self._find_field_mode)
        self._hook_dispatcher.call_hook_if_exists(
            self._aria_graph_custom.get_hook_before_navigation(), last_node)

    def _handle_one_screen(self, transition: Transition):
        current_node: Node = transition.node
        button_label: str = transition.label

        if button_label == self.HOOK_TRANSITION_LABEL:
            called_hook: bool = self._hook_dispatcher.call_hook_if_exists(
                self._aria_graph_custom.get_handle_transition(), current_node)
            if not called_hook:
                raise AssertionError(
                    f"Didn't find a hook for transition with label 'HOOK' and node label '{current_node.label}'. Check you implementation of AriaGraphCustomBase.")
            return

        self._form_filler.fill_form(find_field_mode=self._find_field_mode)

        self._hook_dispatcher.call_hook_if_exists(
            self._aria_graph_custom.get_hook_before_navigation(), current_node)

        self._clickable_with_retry(button_label)
        self._wait_for_screen_with_retry(transition.node.label)

        self._hook_dispatcher.call_hook_if_exists(
            self._aria_graph_custom.get_hook_after_navigation(), current_node)

    def _clickable_with_retry(self, label: str) -> None:
        last_error: Exception | None = None
        attempt: int
        for attempt in range(1, self.MAX_BUTTON_ATTEMPTS + 1):
            try:
                clickable: Locator | None = self._get_clickable(label)
                if clickable is not None:
                    clickable.click(timeout=3000)
                return
            except Exception as e:  # Catch all to enable retries on any failure
                last_error = e
                logging.warning(
                    "Attempt %d/%d to click button '%s' failed: %s",
                    attempt, self.MAX_BUTTON_ATTEMPTS, label, e,
                )
                self._page.wait_for_timeout(self.WAIT_BETWEEN_ATTEMPTS_MS)
        raise AssertionError(
            f"Button '{label}' not found after {self.MAX_BUTTON_ATTEMPTS} attempts: {last_error}")

    def _get_clickable(self, label: str) -> Locator | None:
        pattern: re.Pattern[str] = FormFiller._build_case_insensitive_pattern(
            label)
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
            if expected_title in current_screen:
                return
            logging.info(
                "Current screen is '%s', waiting for '%s' (attempt %d/%d)",
                current_screen, expected_title, attempt, self.MAX_SCREEN_ATTEMPTS,
            )
            self._page.wait_for_timeout(self.WAIT_BETWEEN_ATTEMPTS_MS)
        
        if (self._validate_page_name == ValidatePageName.YES):
            raise AssertionError(
                f"Expected to reach screen '{expected_title}' but currently at '{current_screen}'")

    def _read_screen_title(self) -> str:
        title: str = self._page.title()
        if self._page.get_by_role("heading", level=1).count() > 1:
            heading_text: str = self._page.get_by_role(
                "heading", level=1).first.inner_text()
            return f"{title} / {heading_text}".strip()
        return f"{title}".strip()

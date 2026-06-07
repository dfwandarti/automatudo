import behave
from behave import when, Given, then

from python.page_field.page_field import PageField


@Given("Usuário digitou {text} no campo {display_name}")
@when("Usuário digita {text} no campo {display_name}")
def step_impl(context: behave.runner.Context, text: str, display_name: str):
    field: PageField = PageField(context.page, display_name)
    field.press_sequentially(text)

@Given("Usuário clicou no botão {display_name}")
@when("Usuário clica no botão {display_name}")
def step_impl(context: behave.runner.Context, display_name: str):
    field: PageField = PageField(context.page, display_name)
    field.click()

@then("Campo {display_name} terá texto {expected_text}")
def step_impl(context: behave.runner.Context, display_name: str, expected_text: str):
    field: PageField = PageField(context.page, display_name)
    actual_text: str | None = field.get_text()
    assert expected_text == actual_text, f"Expected text '{expected_text}' does not match actual text '{actual_text}' in field '{display_name}'"

@then("Input {display_name} terá texto {expected_text}")
def step_impl(context: behave.runner.Context, display_name: str, expected_text: str):
    field: PageField = PageField(context.page, display_name)
    actual_text: str | None = field.get_input_text()
    assert expected_text == actual_text, f"Expected text '{expected_text}' does not match actual text '{actual_text}' in field '{display_name}'"

import behave
from behave import when, Given, then

from python.page_field.page_field import PageField


@Given("Usuário digitou {text} no campo {display_name}")
@when("Usuário digita {text} no campo {display_name}")
def step_impl(context: behave.runner.Context, text: str, display_name: str):
    PageField(context.page, display_name).press_sequentially(text)


@when("Usuário clica no botão {display_name}")
def step_impl(context: behave.runner.Context, display_name: str):
    PageField(context.page, display_name).click()


@then("Campo {display_name} terá texto {expected_text}")
def step_impl(context: behave.runner.Context, display_name: str, expected_text: str):
    actual_text: str | None = PageField(context.page, display_name).get_text()
    assert expected_text == actual_text, f"Expected text '{expected_text}' does not match actual text '{actual_text}' in field '{display_name}'"

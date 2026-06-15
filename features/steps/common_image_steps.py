import behave
from behave import Then

from python.page_field.from_display_name import PageFieldFactory


@Then("Imagem login - logo wesayso é como esperada")
def assert_same_image(context: behave.runner.Context):
    field = PageFieldFactory.from_display_name(context.page, "login - logo wesayso")
    field.confirm_is_visible()

    src = field.locator.get_attribute("src")
    assert src is not None, "Logo image src attribute is missing"
    assert "wesayso.webp" in src, f"Unexpected logo image source: {src}"
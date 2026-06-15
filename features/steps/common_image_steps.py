import behave
from playwright.sync_api import Page  # type: ignore[import-untyped]

from python.page_field.from_display_name import PageFieldFactory



@then("Imagem {display_name} é como esperada")
def assert_same_image(context: behave.runner.Context, display_name: str):
    page: Page = context.page # type: ignore
    field = PageFieldFactory.from_display_name(page, display_name)
        
    before: bytes = page.screenshot(clip=field.locator.bounding_box())
    after: bytes = page.screenshot(clip=field.locator.bounding_box())
    
    assert before == after, "The images do not match"

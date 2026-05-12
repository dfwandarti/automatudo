from behave import given, when, then
from playwright.sync_api import sync_playwright

@given('que o usuário abre o navegador')
def step_abrir_navegador(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=False)
    context.page = context.browser.new_page()

@when('o usuário acessa "{url}"')
def step_acessa_url(context, url):
    context.page.goto(url)

@then('a página do Google é exibida')
def step_verifica_google(context):
    assert "Google" in context.page.title()
    context.browser.close()
    context.playwright.stop()
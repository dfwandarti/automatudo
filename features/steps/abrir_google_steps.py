import behave
from behave import given, when, then
from playwright.sync_api import sync_playwright
from hamcrest import assert_that, contains_string

@given('que o usuário abriu o navegador')
def step_abrir_navegador(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=False)
    context.page = context.browser.new_page()

@when('o usuário acessa "{url}"')
def step_acessa_url(context, url):
    context.page.goto(url)

@then('a página do Login será exibida')
def step_verifica_google(context):
    assert_that(context.page.title(), contains_string("Login - Automatudo"))
    context.browser.close()
    context.playwright.stop()


@when("o usuário loga como admin")
def step_impl(context: behave.runner.Context):
    context.page.goto("https://dfwandarti.github.io/automatudo/static/login.html")
    context.page.fill("#usuario", "admin")
    context.page.fill("#senha", "admin")
    context.page.click("//button")

@when("o usuário loga como zequinha")
def step_impl(context: behave.runner.Context):
    context.page.goto("https://dfwandarti.github.io/automatudo/static/login.html")
    context.page.fill("#usuario", "zequinha")
    context.page.fill("#senha", "zequinha")
    context.page.click("//button")

@then("o usuário estará logado")
def step_impl(context: behave.runner.Context):
    success_message = context.page.get_by_text("✓ Você logou com sucesso")
    success_message.wait_for(timeout=5000)
    assert success_message.is_visible()

@then("o usuário verá mensagem de usuário inválido")
def step_impl(context: behave.runner.Context):
    success_message = context.page.get_by_text("Usuário ou senha inválidos")
    success_message.wait_for(timeout=5000)
    assert success_message.is_visible()

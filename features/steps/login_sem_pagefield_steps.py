import behave
from behave import given, when, then
from playwright.sync_api import sync_playwright
from hamcrest import assert_that, contains_string
from python.pages.login_page import LoginPage


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
def step_login_admin(context: behave.runner.Context):
    context.page.goto("https://dfwandarti.github.io/automatudo/static/login.html")
    login_page = LoginPage(context.page)
    login_page.login("admin", "admin")


@when("o usuário loga como zequinha")
def step_login_zequinha(context: behave.runner.Context):
    context.page.goto("https://dfwandarti.github.io/automatudo/static/login.html")
    login_page = LoginPage(context.page)
    login_page.login("zequinha", "zequinha")


@then("o usuário estará logado")
def step_verify_login(context: behave.runner.Context):
    login_page = LoginPage(context.page)
    login_page.verify_login_success()
    context.browser.close()
    context.playwright.stop()


@then("o usuário verá mensagem de usuário inválido")
def step_verify_invalid_login(context: behave.runner.Context):
    login_page = LoginPage(context.page)
    login_page.verify_invalid_credentials()
    context.browser.close()
    context.playwright.stop()

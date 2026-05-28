from behave import given

from python.pages.login_page import LoginPage


@given('Usuário navegou para tela de login')
def step_abrir_navegador(context):
    context.login_page = LoginPage(context.page)
    context.login_page.navigate_to()

import behave.runner
from behave import given

from python.pages.login_acme_page import LoginPageAcme

@given("Usuário navegou para tela de login da acme")
def step_impl(context: behave.runner.Context):
    context.login_page = LoginPageAcme(context.page)
    context.login_page.navigate_to()

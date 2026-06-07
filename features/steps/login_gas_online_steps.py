import behave.runner
from behave import *

from python.pages.login_gas_online_page import LoginPageGasOnline


@given("Usuário navegou para tela de login gás online")
def step_impl(context: behave.runner.Context):
    context.login_page = LoginPageGasOnline(context.page)
    context.login_page.navigate_to()

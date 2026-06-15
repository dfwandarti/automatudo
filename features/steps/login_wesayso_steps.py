import behave.runner
from behave import *

from python.pages.login_wesayso_page import LoginPageWesayso

@given("Usuário navegou para tela de login da wesayso")
def step_impl(context: behave.runner.Context):
    context.login_page = LoginPageWesayso(context.page)
    context.login_page.navigate_to()

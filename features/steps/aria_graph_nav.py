import logging
import re

from behave import given, then, when

from python.flowchart.parser import FlowchartTree
from python.aria_graph.aria_graph_engine import AriaGraphEngine

FLOWCHART_PATH = "LOGIN_FLOW.md"
MAX_TENTATIVAS_BOTAO = 3
MAX_TENTATIVAS_TELA = 3
ESPERA_ENTRE_TENTATIVAS_MS = 1000
PAPEIS_ARIA_PREENCHIVEIS = (
    "textbox", "searchbox", "spinbutton",
    "checkbox", "radio",
    "combobox", "listbox", "option",
)


@given("Usuário tem estes dados:")
def save_data_to_form_filling(context):
    form_filling: dict = {row["chave"]: row["valor"] for row in context.table}
    context.aria_graph = AriaGraphEngine(context.page, form_filling)    


@when('Usuário navega até página com título "{titulo}"')
def step_navega(context, titulo):
    context.aria_graph.loop_until_reaches_end_of_flow(titulo)

@then('Usuário verá o título "{titulo}" na página')
def step_verifica_titulo(context, titulo):
    tela_atual = context.aria_graph._read_screen_title()
    assert tela_atual.__contains__(titulo), f"Esperava título '{titulo}' na página, mas encontrado '{tela_atual}'"



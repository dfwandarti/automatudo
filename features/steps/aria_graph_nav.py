from behave import given, then, when

from python.aria_graph.aria_graph_engine import AriaGraphEngine
from python.aria_graph.aria_graph_custom import AriaGraphCustomImpl

@given("Usuário tem estes dados:")
def save_data_to_form_filling(context):
    form_filling: dict = {row["chave"]: row["valor"] for row in context.table}
    aria_graph_custom: AriaGraphCustomImpl = AriaGraphCustomImpl()
    context.aria_graph = AriaGraphEngine(context.page, form_filling, aria_graph_custom)


@when('Usuário navega até página com título "{titulo}"')
def step_navega(context, titulo):
    ariaGraphEngine: AriaGraphEngine = context.aria_graph
    ariaGraphEngine.loop_until_reaches_end_of_flow(titulo)

@then('Usuário verá o título "{titulo}" na página')
def step_verifica_titulo(context, titulo):
    tela_atual = context.aria_graph._read_screen_title()
    assert tela_atual.__contains__(titulo), f"Esperava título '{titulo}' na página, mas encontrado '{tela_atual}'"



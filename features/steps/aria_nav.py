from behave import given


@given("Usuário tem estes dados:")
def step_impl(context):
    context.dados = {row["chave"]: row["valor"] for row in context.table}

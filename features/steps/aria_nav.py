import logging
import re

from behave import given, when

from python.flowchart.parser import FlowchartTree

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
    context.form_filling = {row["chave"]: row["valor"] for row in context.table}


@when('Usuário navega até página com título "{titulo}"')
def step_navega(context, titulo):
    tree = FlowchartTree.from_file(FLOWCHART_PATH)

    destino = tree.find_by_label(titulo)
    if destino is None:
        raise AssertionError(f"Nó com título '{titulo}' não encontrado em {FLOWCHART_PATH}")

    caminho = tree.path(tree.root(), destino)

    for transicao in caminho:
        no_atual = tree.find_by_label(_ler_titulo_tela(context.page))
        if no_atual is None:
            raise AssertionError(f"Tela atual não corresponde a nenhum nó de {FLOWCHART_PATH}")

        _preencher_campos_tela(context.page, getattr(context, "form_filling", {}))

        rotulo_botao = _rotulo_transicao(no_atual, transicao.node)
        _clicar_botao_com_retry(context.page, rotulo_botao)
        _aguardar_tela_com_retry(context.page, transicao.node.label)


def _preencher_campos_tela(page, form_filling: dict) -> None:
    for chave, valor in form_filling.items():
        elemento, papel = _achar_campo_por_chave(page, chave)
        if elemento is None:
            continue
        try:
            _preencher_elemento(elemento, papel, valor)
        except Exception as e:
            logging.warning(
                "Falha ao preencher campo (papel '%s') encontrado pela chave '%s': %s",
                papel, chave, e,
            )


def _achar_campo_por_chave(page, chave: str):
    padrao = re.compile(re.escape(chave), re.IGNORECASE)
    for papel in PAPEIS_ARIA_PREENCHIVEIS:
        locator = page.get_by_role(papel, name=padrao)
        if locator.count() > 0:
            return locator.first, papel
    return None, None


def _preencher_elemento(elemento, papel: str, valor: str) -> None:
    if papel in ("textbox", "searchbox", "spinbutton"):
        elemento.fill(valor)
    elif papel == "checkbox":
        elemento.set_checked(_valor_verdadeiro(valor))
    elif papel == "radio":
        elemento.check()
    elif papel in ("combobox", "listbox"):
        elemento.select_option(valor)
    elif papel == "option":
        elemento.click()
    else:
        logging.warning("Papel ARIA '%s' não suportado para preenchimento automático", papel)


def _valor_verdadeiro(valor: str) -> bool:
    return valor.strip().lower() in ("true", "1", "sim", "yes", "verdadeiro")


def _rotulo_transicao(origem, destino):
    for transicao in origem.successors:
        if transicao.node is destino:
            return transicao.label
    raise AssertionError(f"Não há transição de '{origem.label}' até '{destino.label}' no flowchart")


def _ler_titulo_tela(page) -> str:
    return page.get_by_role("heading", level=1).inner_text().strip()


def _clicar_botao_com_retry(page, rotulo: str) -> None:
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS_BOTAO + 1):
        try:
            page.get_by_role("button", name=rotulo, exact=True).click(timeout=3000)
            return
        except Exception as e:
            ultimo_erro = e
            logging.warning(
                "Tentativa %d/%d de clicar no botão '%s' falhou: %s",
                tentativa, MAX_TENTATIVAS_BOTAO, rotulo, e,
            )
            page.wait_for_timeout(ESPERA_ENTRE_TENTATIVAS_MS)
    raise AssertionError(f"Botão '{rotulo}' não encontrado após {MAX_TENTATIVAS_BOTAO} tentativas: {ultimo_erro}")


def _aguardar_tela_com_retry(page, titulo_esperado: str) -> None:
    tela_atual = None
    for tentativa in range(1, MAX_TENTATIVAS_TELA + 1):
        tela_atual = _ler_titulo_tela(page)
        if tela_atual == titulo_esperado:
            return
        logging.info(
            "Tela atual é '%s', esperando '%s' (tentativa %d/%d)",
            tela_atual, titulo_esperado, tentativa, MAX_TENTATIVAS_TELA,
        )
        page.wait_for_timeout(ESPERA_ENTRE_TENTATIVAS_MS)
    raise AssertionError(f"Esperava chegar na tela '{titulo_esperado}' mas está em '{tela_atual}'")

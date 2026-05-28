# features/environment.py
from behave.cucumber_expression import (
    ParameterType,
    define_parameter_type,
    define_parameter_type_with
)
from playwright.sync_api import sync_playwright

from python.page_field.page_field import PageField

define_parameter_type(ParameterType(
    name="pageField",
    regexp="[a-zA-Z-]+",
    type=PageField,
    transformer=PageField.from_display_name
))


def before_scenario(context, scenario):
    """Inicializa o navegador e page objects antes de cada cenário"""
    init_playwright(context)


def init_playwright(context):
    context.playwright = sync_playwright().start()
    context.browser = context.playwright.chromium.launch(headless=False)
    context.page = context.browser.new_page()


def after_scenario(context, scenario):
    """Limpa recursos após cada cenário"""
    if hasattr(context, 'browser'):
        context.browser.close()
    if hasattr(context, 'playwright'):
        context.playwright.stop()


def after_all(context):
    # 1. Varre todos os formatadores ativos na execução do Behave
    for formatter in getattr(context, "_runner", {}).formatters:

        # 2. Identifica especificamente o behave-html-pretty-formatter
        if formatter.__class__.__name__ == "PrettyHTMLFormatter":
            print("\n[Behave Hook] Forçando gravação e fechamento do relatório HTML...")

            try:
                # 3. Força a geração final dos dados estruturados em HTML
                if hasattr(formatter, "close"):
                    formatter.close()
                elif hasattr(formatter, "close_stream"):
                    formatter.close_stream()

                # 4. Garante a gravação física imediata do buffer no HD
                if hasattr(formatter, "stream") and formatter.stream:
                    formatter.stream.flush()
                    formatter.stream.close()

                print("[Behave Hook] Sucesso! O arquivo report.html foi persistido.")
            except Exception as e:
                print(f"[Behave Hook] Erro ao descarregar arquivo: {e}")

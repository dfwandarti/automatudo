# features/environment.py

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

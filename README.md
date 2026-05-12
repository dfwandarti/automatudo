# Automatizando tudo de testes E2E.

<img width="512" height="512" alt="automatudo" src="https://github.com/user-attachments/assets/1e185f5a-5ffb-45ff-bf39-3fe5a35bd74f" />


# Sobre 

Projeto de exemplo: Teste automatizado com Python, Behave (Cucumber) e Playwright.

## Pré-requisitos
- Python 3.7+
- Dependências Playwright (ver abaixo)

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

Para gerar relatório HTML instale o allure: https://allurereport.org/docs/behave/

   Ou se quiser: https://github.com/allure-framework/allure2/releases

## Executando o teste
```bash
behave
```

## Estrutura
- features/abrir_google.feature: Cenário de abrir o Google
- features/steps/abrir_google_steps.py: Implementação dos passos

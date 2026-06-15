# Automatudo

Projeto do canal onde falamos tudo sobre automatização de testes E2E.

## Código

O código exemplo aqui é com Python, Behave (Cucumber) e Playwright.

### Pré-requisitos
- Python 3.7+
- Dependências Playwright (ver abaixo)

### Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install behave playwright
python -m playwright install
```

Se necessário, instale dependências do sistema:
```bash
sudo playwright install-deps
```

## Executando o teste
```bash
behave
```

## Estrutura
- features/abrir_google.feature: Cenário de abrir o Google
- features/steps/abrir_google_steps.py: Implementação dos passos

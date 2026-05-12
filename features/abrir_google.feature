# language: en

Feature: Abrir o Google
  Scenario: Usuário acessa o Google
    Given que o usuário abre o navegador
    When o usuário acessa "https://www.google.com"
    Then a página do Google é exibida
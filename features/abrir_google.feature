# language: en

Feature: Abrir tela de login
  Background:
    Given que o usuário abre o navegador

  Scenario: Usuário acessa o Google
    When o usuário acessa "https://dfwandarti.github.io/automatudo/static/login.html"
    Then a página do Google é exibida
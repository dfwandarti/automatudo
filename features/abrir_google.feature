# language: en

Feature: Abrir tela de login
  Background:
    Given que o usuário abriu o navegador

  Scenario: Usuário acessa o Login
    When o usuário acessa "https://dfwandarti.github.io/automatudo/static/login.html"
    Then a página do Login será exibida

  Scenario: Usuário loga como admin
    When o usuário loga como admin
    Then o usuário estará logado

    Scenario: Usuário loga como zequinha
    When o usuário loga como zequinha
    Then o usuário verá mensagem de usuário inválido

# Given -> usar passado
# When -> usar presente
# Then -> usar futuro


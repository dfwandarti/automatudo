# language: en

Feature: Abrir tela de login

  Background:
    Given Usuário navegou para tela de login

  Scenario: Usuário loga como admin
    Given Usuário digitou admin no campo login - input user
    And Usuário digitou admin no campo login - input senha
    When Usuário clica no botão login - botão logar
    Then Campo home - mensagem sucesso terá texto ✓ Você logou com sucesso


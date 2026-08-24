Feature: Abrir tela de login

  Background:
    Given Usuário navegou para tela de login

  Scenario: Usuário loga como admin
    Given Usuário digitou admin no campo login - input user
    And Usuário digitou admin no campo login - input senha
    When Usuário clica no botão login - botão logar
    Then Campo home - mensagem sucesso terá texto ✓ Você logou com sucesso

  Scenario: Usuário loga como zequinha
    Given Usuário digitou zequinha no campo login - input user
    And Usuário digitou zequnha no campo login - input senha
    When Usuário clica no botão login - botão logar
    Then Campo login - mensagem erro terá texto Usuário ou senha inválidos

  Scenario: Valida tamanho do login
    Given Usuário digitou abcdefghikz no campo login - input user
    Then Input login - input user terá texto abcdefghik

  Scenario: Usuário navega pelo aria snapsht
    Given Usuário tem estes dados:
      | chave   | valor      |
      | Usuário | admin      |
      | senha   | admin      |
      | dia     | 1974-11-23 |
    When Usuário navega até página com título "Compras de um dia"
    Then Usuário verá o título "Compras de um dia" na página

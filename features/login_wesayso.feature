# language: en

Feature: Abrir tela de login do wesayso

  Background:
    Given Usuário navegou para tela de login da wesayso

  Scenario: Verifica se logo está correto
    Then Imagem login - logo wesayso é como esperada
    And Apenas uma imagem de logo é encontrada
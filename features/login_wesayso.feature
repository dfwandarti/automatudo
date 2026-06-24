# language: en

Feature: Abrir tela de login do wesayso

  Background:
    Given Usuário navegou para tela de login da wesayso

  Scenario: Verifica se logo está correto
    Then Imagem login - logo wesayso é como esperada
    And A imagem logo wesayso é encontrada 1 vez
    And A imagem logo acme é encontrada 0 vezes
# language: en

Feature: Abrir tela de login do acme

  Background:
    Given Usuário navegou para tela de login da acme

  Scenario: Verifica se logo está correto
    Then Imagem login - logo acme é como esperada
 
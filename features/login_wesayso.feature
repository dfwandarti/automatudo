# language: en

Feature: Abrir tela de login do wesayso

  Background:
    Given Usuário navegou para tela de login da wesayso

  Scenario: Verifica se logo está correto
    Then Logo da wesayso é exibido corretamente

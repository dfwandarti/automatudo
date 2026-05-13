# Automatizando tudo de testes E2E.
<img width="543" height="460" alt="automatudo2" src="https://github.com/user-attachments/assets/a4b58a3c-f3d2-4648-a11d-ff668c42e451" />

# Sumário
  - [Primeiro episódio](#primeiro_episodio) 
  - [Sobre o código](#sobre_codigo)

# Primeiro episódio
<a id="primeiro_episodio"></a>
*O Automatudo* é sobre dois desenvolvedores que estão trabalhando na automação de testes de um aplicativo. O aplicativo não é complexo, 
mas tem seus desafios. Ao longo da série, nós vamos falar como enfrentamos diversos obstáculos e como conseguimos chegar um site que faturou 
10 milhões em 3 meses e passou meses sem um incidente em produção.

Os vídeos estão no youtube, no canal: <tbd> 

O foco não é falar sobre Python, Playwright nem Behave. Este *stack* foi escolhido pelas
seguintes razões:
- *BDD*: permite alinhar testes com o comportamento esperado do sistema.
- *Gherkin*: associa cenários às histórias, garantindo rastreabilidade.
- *Cenários ligados a bugs*: facilita reproduzir e validar correções.
- *Granularidade dos testes*: aumenta a agilidade na automação.

No vídeo você vai entender:
- A importância de organizar os testes para rodar sem supervisão.
- Onde se encaixa um teste E2E em um CI/CD.
- Como fazer testes E2E com mock, e qual tipo de mock deve ser evitado.
- Como transformamos o código inicial em POM (*Page Object Model*)
   - Como você deve organizar as dependências entre os steps e as páginas.
- A importância de ter um teste que faz retentativas e é resiliente.
- Estratégia para cobertura de testes E2E.

## Sobre a resiliência
Imagine o seguinte cenário:
```
*Given* Usuário acessou a tela de login
*When* Informa usuário e senha
*And* Entra com código do token
*Then* Usuário estará logado
```
Objetivo deste cenário é testar o login, e qualquer erro neste cenário deve abortar o teste e reportar o problema no login.

Agora imagine o cenário abaixo:
```
*Given* Usuário logou no sistema
*And* Pesquisou e colocou no carrinho um "Secador de cabelo"
*When* Usuário clica para pagar e informa cartão de crédito
*Then* Verá tela de pagamento concluído
```

Objetivo neste cenário é testar o pagamento, e não o login. Se houver qualquer problema no começo deste cenário é interessante
fazer o teste ser resiliente e fazer nova retentativa.

## Estratégia para cobertura
Segundo a pirâmide de testes abaixo, a maior cobertura de testes deveria ser com testes unitários. A menor cobertura deveria ser com testes E2E.

<img width="777" height="389" alt="piramide" src="https://github.com/user-attachments/assets/aad75694-3f5b-46fd-956f-51b9003c3d57" />

Assim, você deveria pensar em automatizar alguns fluxos principais e nada mais.

Este não foi o nosso caso naquela aplicação, mas atenção, ó peregrino desconhecedor dos perigos presentes nesse caminho! Nossa recomendação seria:
| Condição | Recomendação |
|----------|--------------|
| O time de automação *consegue* manter ritmo similar ao time de desenvolvimento | Procure automatizar 100% da aplicação |
| O time de automação *não* consegue manter ritmo similar ao time de desenvolvimento | Procure automatizar os fluxos mais importantes |
| Você está começando a automatizar um projeto legado, por onde você começa? | Foque nas **novas** features e nas mais importantes das legadas, em tese a aplicação legada já é "testada" pelo tempo |

Se o time de automação está participando desde o começo, ótimo. 

Se o produto já tem várias funcionalidades prontas, busque reforços para alguém fazer a automação enquanto alguém faz o trabalho manual.

# Sobre o código
<a id="sobre_codigo"/>

Projeto de exemplo: Teste automatizado com Python, Behave (Cucumber) e Playwright.

## Pré-requisitos
- Python 3.7+
- Dependências Playwright (ver abaixo)

## Instalação
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install
```

Para gerar relatório HTML instale o allure: https://allurereport.org/docs/behave/

   Ou se quiser: https://github.com/allure-framework/allure2/releases

## Executando o teste
```bash
behave
```

## Estrutura
- features/abrir_google.feature: Cenário de abrir o Google
- features/steps/abrir_google_steps.py: Implementação dos passos

<img width="512" height="512" alt="automatudo" src="https://github.com/user-attachments/assets/1e185f5a-5ffb-45ff-bf39-3fe5a35bd74f" />

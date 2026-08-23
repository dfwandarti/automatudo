display_name_to_test_id = {
  "login - input user": "usuario",
  "login - input senha": "senha",
  "login - botão logar": "botao-entrar",
  "login - mensagem erro": "mensagem-erro",
  "home - mensagem sucesso": "mensagem-sucesso",
  "home - botão minha conta": "botao-minha-conta",
  "home - botão minhas compras": "botao-minhas-compras",
  "minhas compras - input data pesquisa": "input-data-pesquisa",
  "minhas compras - botão pesquisar": "botao-pesquisar",
  "minhas compras - tabela compras": "tabela-compras",
  "login - logo wesayso": "wesayso-icon",
  "login - logo acme": "acme-icon",
}

class DisplayNameToTestId:
    @classmethod
    def get_data_test_id(cls, display_name: str) -> str | None:
        return display_name_to_test_id.get(display_name)
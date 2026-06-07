from playwright.sync_api import Page

from page_field.page_field import PageField


class PageFieldLogin(PageField):
    def __init__(self, page: Page, display_name: str) -> None:
        super().__init__(page, "login gas online - botão entrar")

    def click(self):
        current_user: str = PageField(self.page, "login - input user").get_input_text()
        print('***************************')
        print('antes de clicar no botão, salve os dados da tela')
        print(f'  registre em arquivo que logou com usuário {current_user}')
        print('***************************')
        super().click()
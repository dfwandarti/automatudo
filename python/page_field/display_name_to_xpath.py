display_name_to_xpath = {
    "login gas online - botão entrar": "//*[text()='Entrar']",
    "login gas online - menu sanduíche": "//*[@class='menu-icon']",
    "login gas online - botão aceitar cookies": "//*[@id='onetrust-accept-btn-handler']"
}

class DisplayNameToXpath:
    @classmethod
    def get_xpath(cls, display_name: str) -> str | None:
        return display_name_to_xpath.get(display_name)
from entities.pages.page_tools.page_tools import PageTools


class LoginPageTools(PageTools):
    def __init__(self, driver):
        super().__init__(driver)

    def setUsername(self, username: str):
        # Username
        web_element = self.write_id('mat-input-0', username)

    def setPassword(self, password: str):
        # Password
        web_element = self.write_id('mat-input-1', password)

    def pressLoginButton(self):
        self.click_element("//button[contains(.//text(), 'Entrar')]")

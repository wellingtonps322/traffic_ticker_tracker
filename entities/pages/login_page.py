from entities.pages.page import Page
from entities.pages.page_tools.login_page.login_page_tools import LoginPageTools


class LoginPage(Page):
    def __init__(self, username: str, password: str, driver: dict = None) -> None:
        super().__init__()
        if driver:
            self.driver = driver
        self.driver.get(
            'https://autenticacao.localiza.com/login?source_system=https:%2F%2Ffrota360.localiza.com%2Fhome&system_code=PORTAL_CLIENTE')

        self.login_page_tools = LoginPageTools(driver=self.driver)

        self.username = username
        self.password = password

        self.insert_login_data()

    def insert_login_data(self):
        self.login_page_tools.setUsername(username=self.username)
        self.login_page_tools.setPassword(password=self.password)
        self.login_page_tools.pressLoginButton()

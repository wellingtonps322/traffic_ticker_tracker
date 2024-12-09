from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import SessionNotCreatedException


class DriverFactory():

    def __init__(self) -> None:
        pass

    @staticmethod
    def createDriver():
        driver = None
        attempts = 0

        while not driver and attempts <= 3:
            try:
                chrome_options = Options()
                # chrome_options.add_argument('--headless')
                chrome_options.add_argument(
                    '--log-level=3')  # Disable console log
                chrome_options.add_experimental_option("detach", True)
                service = Service(ChromeDriverManager().install())
                # WebDriverWait(driver, timeout=10)  # .until(document_initialised)
                # browser.maximize_window()
                driver = webdriver.Chrome(
                    service=service, options=chrome_options)
                # self.driver.implicitly_wait(20)

                return driver
            except SessionNotCreatedException as e:
                driver = None

    @staticmethod
    def getDriver():
        driver = DriverFactory.createDriver()
        if driver:
            return driver

    def getUrl(self, url: str):
        self.driver.get(url=url)

    def killDriver(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

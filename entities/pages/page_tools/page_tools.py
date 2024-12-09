import re
import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup


class PageTools():

    def __init__(self, driver):
        self.driver = driver

    ################### * Tools #####################

    def getDateConverter(self, date, type):
        self.date_str = date.replace('h', '')
        self.date_format = r'%d/%m/%Y %H:%M'
        self.date_object = datetime.datetime.strptime(
            self.date_str, self.date_format)

        if type == 'all':
            return self.date_object
        if type == 'date':
            return self.date_object.date()
        if type == 'hour':
            return self.date_object.time()
        return None

    ############### * Get Page Source ###############

    def getHTML(self):
        html_page = WebDriverWait(self.driver, 30, 1).until(
            EC.visibility_of_element_located(locator=(By.XPATH, "//ul//li")))
        return self.driver.page_source

    def getHTML_bs(self):
        #!Having troubles with delay to load page
        html = self.getHTML()
        return BeautifulSoup(html, 'html.parser')

    ############### * Click on element ##############
    def click_element(self, xpath):
        web_element = self.driver.find_element(By.XPATH, xpath)
        web_element.click()
        return web_element

    def checkingTextInElement(self, text: str, xpath: str):
        web_element_text = self.driver.find_element(By.XPATH, xpath).text
        web_element_text = re.split(r'\n', web_element_text)
        if len(web_element_text) > 1:
            web_element_text = web_element_text[1].strip()
            if text == web_element_text:
                return True
        return False

    # *Write in textfield
    def write(self, By, element, text):
        html_page = WebDriverWait(self.driver, 30, 1).until(
            EC.visibility_of_element_located(locator=(By, element)))
        web_element = self.driver.find_element(By, element)
        web_element.send_keys(text)
        return web_element

    def write_xpath(self, xpath, text):
        web_element = self.write(By.XPATH, xpath, text)
        return web_element

    def write_id(self, id, text):
        web_element = self.write(By.ID, id, text)
        return web_element

    def closeWindow(self):
        if len(self.driver.window_handles) > 1:
            self.driver.close()

    def changeWindowFocus(self, window):
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[window])

    ############### * Find element ##############

    def find_element_by_text(self, tag_element, search_text):
        xpath_str = f"//{tag_element}[contains(text(), '{search_text}')]"
        element = self.driver.find_element(By.XPATH, xpath_str)

        if element:
            return element

    def get_parent_element(self, element, parent_class, tag):
        xpath_str = f"./ancestor::{tag}[contains(@class, '{parent_class}')]"
        parent_element = element.find_element(By.XPATH, xpath_str)

        parent_element_html = parent_element.get_attribute("outerHTML")
        parent_element_bs4 = BeautifulSoup(parent_element_html, "html.parser")

        return parent_element_bs4


if __name__ == '__main__':
    test = '02/08/2023 10:03h'

    instance = PageTools(None)
    date_test = instance.getDateConverter(date=test, type='all')
    print(date_test)

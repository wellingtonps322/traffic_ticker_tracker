import os
import time
import datetime

import pandas as pd

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from entities.pages.page_tools.page_tools import PageTools
from database.database import Database
from database.reader import Reader
from database.recorder import Recorder


class InfractionManagerPageTools(PageTools):

    seven_days_before = datetime.datetime.strftime(
        datetime.datetime.now() - datetime.timedelta(days=7), "%d/%m/%Y")
    yesterday = datetime.datetime.strftime(
        datetime.datetime.now() - datetime.timedelta(days=1), "%d/%m/%Y")

    def __init__(self, driver):
        super().__init__(driver)
        database = Database()
        self.reader = Reader(database)
        self.recorder = Recorder(database)

    def setting_filter_to_realease_date(self, initial_date, end_date):
        self.insert_value_at_unidade_cnpj()
        self.insert_date_at_realease_date(initial_date, end_date)
        # ? Search button
        self.click_on_search_button_at_infraction_manager()

    # * Click functions

    def click_on_search_button_at_infraction_manager(self):
        self.click_element(
            "//button[@class='btn-primary mat-raised-button mat-primary']")

    def click_on_export_button_at_infraction_manager(self):
        self.click_element(
            "//button[@class='btn-export ml-2 ng-star-inserted']")

    # * Insert functions

    def insert_value_at_unidade_cnpj(self):
        self.click_element("//div[@class='col-sm-6 col-xs-6 col-md-3']")

        self.write_id("mat-input-6", "Move Servicos")

        self.click_element("//span[contains(.//text(), 'Move Servicos')]")

        # ? Click on overlay to close the modal
        self.click_element(
            "//div[@class='cdk-overlay-container']")

    def insert_date_at_realease_date(self, initial_date: str = yesterday, end_date: str = yesterday):
        """
        INSERIR AS DATAS NO MODELO DD/MM/AAAA
        """

        # ? Click at date select element
        self.click_element(
            "//div[@class='mat-form-field-suffix ng-tns-c22-7 ng-star-inserted']")

        # ? Initial date
        self.write_id("mat-input-3", initial_date)
        # ? End date
        self.write_id("mat-input-4", end_date)

        # ? Click on submit button at modal date
        self.click_element(
            "//button[@class='btn-primary mat-raised-button']")

    # * Get functions

    def get_infraction_rows(self):
        infraction_rows = self.driver.find_elements(
            By.XPATH, "//mat-row[@class='mat-row element-row grey-row ng-star-inserted']")

        return infraction_rows

    def get_filepath_to_file_download(self, timeout=60, delete: bool = False) -> str:
        """
            Essa função procurará pelo download especificado até que o tempo limite seja excedido, caso encrontrado, irá retornar o path do arquivo, caso não encontrado retornará None
        """
        START_TIME = time.time()
        DOWNLOAD_DIR = "<PATH DA PASTA DOWNLOAD>"

        # ! Descobrir uma forma de direcionar a pasta downloads não importa qual seja o computador

        while True:

            for filename in os.listdir(DOWNLOAD_DIR):

                if filename == 'Relatório de Multas ( - ).xlsx':
                    file_path = os.path.join(DOWNLOAD_DIR, filename)
                    return file_path

            # ? Se o método for chamado apenas para procurar um arquivo para excluir, o timer não será utilizado
            if not (time.time() - START_TIME < timeout and not delete):
                break

        # raise TimeoutError("File not found after limit time.")
        return None

    def get_export_infraction_report_file(self) -> pd.DataFrame:
        is_page_loading_result = self.is_page_loading()

        # * Checando se existe algum arquivo de notificação de multas para excluir
        self.delete_old_file()

        # Clicando no botão para extrair as multas
        if not is_page_loading_result:

            self.click_on_export_button_at_infraction_manager()
            file_path = self.get_filepath_to_file_download()

            file = pd.read_excel(file_path)

            return file

    def get_infraction_report_row_data(self, row: pd.Series):
        infraction_report_data = {}
        infraction_report_data["AIT_number"] = f'"{
            row["Número AIT"]}"'
        infraction_report_data["original_AIT"] = f'"{
            row["AIT Originária"]}"' if row["AIT Originária"] != "-" else "NULL"
        infraction_report_data["license_plate"] = f'"{
            row["Placa"]}"'
        infraction_report_data["description"] = f'"{
            row["Infração"]}"'
        infraction_report_data["value"] = round(
            float(row["Valor Cobrado"]), 2)
        infraction_report_data["email_date"] = f'"{
            row["Data do Email (Envio Multa)"]}"' if row["Data do Email (Envio Multa)"] != "-" else "NULL"
        infraction_report_data["shipping_date_to_customer"] = f'"{
            row["Data do Envio para o Cliente"]}"'
        infraction_report_data["deadline_for_nomination"] = f'"{
            row["Data Limite para Indicação"]}"'
        infraction_report_data["name_of_nominee"] = f'"{
            row["Nome do Indicado"]}"' if row["Nome do Indicado"] != "-" else "NULL"
        infraction_report_data["customer"] = f'"{row["Cliente"]}"'
        infraction_report_data["infraction_date"] = f'"{
            row["Data/Hora da Infração"]}"'
        infraction_report_data["release_date_of"] = f'"{
            row["Data de Lançamento"]}"'
        infraction_report_data["referral_status"] = f'"{
            row["Status da Indicação"]}"' if row["Status da Indicação"] != "Sem Indicação" else "NULL"
        infraction_report_data["resource_status"] = f'"{
            row["Status de Recurso"]}"' if row["Status de Recurso"] != "-" else "NULL"
        infraction_report_data["reason"] = f'"{
            row["Motivo"]}"' if row["Motivo"] != "-" else "NULL"
        infraction_report_data["infraction_location"] = f'"{
            row["Local Infração"]}"'
        infraction_report_data["total_value"] = round(infraction_report_data["value"] + (
            infraction_report_data["value"] * 20 / 100), 2)

        return infraction_report_data

    def update_infraction_report_data(self):
        file = self.get_export_infraction_report_file()

        infraction_report_data_list = []
        infraction_report_data_to_update_list = []

        for index, row in file.iterrows():
            infraction_report_data = {}

            infraction_report_data = self.get_infraction_report_row_data(
                row=row)

            if not self.infraction_data_already_exists(row["Número AIT"]):

                infraction_report_data_list.append(infraction_report_data)
            else:
                # Update infraction data ! Está com erro!

                if not self.infraction_at_database_is_updated(infraction_report_data):
                    print(f"Infraction {row['Número AIT']
                                        } is out of date, please update!")

        if len(infraction_report_data_list) >= 1:
            self.recorder.insert_infraction_report_data(
                infraction_report_data_list)

            return {"status": "success"}

    # * Validate functions

    def infraction_data_already_exists(self, AIT_number: str) -> bool:

        #! Coletar todas as AITs de uma só vez, armazenar em uma variável da instância
        #! Para verificar se a infração está na lista de infrações existentes
        #! Para diminuir a quantidade de requisições no banco de dados
        #* Pensar uma forma que seja escalavel para não se tornar inviável quando
        #* Houver uma quantidade alta de multas no histórico 
        response = self.reader.get_infraction_data_by_AIT_number(AIT_number)

        if response:
            return True
        return False

    def is_page_loading(self):
        while True:
            try:
                html_page = WebDriverWait(self.driver, 3, 1).until(EC.presence_of_element_located(
                    locator=(By.XPATH, "//div[@class='loading-screen-icon']")))
            except:
                return False

    def infraction_at_database_is_updated(self, new_data):
        old_data = self.reader.get_infraction_data_by_AIT_number(
            new_data["AIT_number"].replace('"', ""))[:17]

        # Check if the data is the same
        for (new, old) in zip(new_data.values(), old_data):

            new = None if new == "NULL" else new

            if str(old) in str(new):
                continue

            return False

        return True

    # * System functions

    def delete_old_file(self):
        # * Checando se existe algum arquivo de notificação de multas para excluir
        old_file_path = self.get_filepath_to_file_download(delete=True)
        if old_file_path:
            os.remove(old_file_path)
            return True

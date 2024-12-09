import sched
import datetime
import time

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from entities.pages.login_page import LoginPage
from entities.pages.infraction_manager_page import InfractionManagerPage
from core.driver_factory import DriverFactory
from database.database import Database
from database.reader import Reader
from database.updater import Updater


class Program():
    def __init__(self) -> None:
        ...

    def infractionDataCollector(self):
        # Login Page
        self.driver = DriverFactory.getDriver()

        # Se a criação do driver não for bem sucedida, a aplicação deverá parar
        if not self.driver:
            return

        LoginPage(username='USERNAME',
                  password='PASSWORD', driver=self.driver)

        is_page_login_result = self.is_page_loading()

        current_url = self.driver.current_url

        # Checando se a plataforma está na home
        if current_url == "https://frota360.localiza.com/home" and not is_page_login_result:
            infraction_manager_page = InfractionManagerPage(self.driver)
            infraction_manager_page.get_in_page()

            # Checando se a plataforma está no
            is_page_loading_result = self.is_page_loading()
            current_url = self.driver.current_url
            if current_url == "https://frota360.localiza.com/gerenciador-infracoes/indicacoes-eletronicas" and not is_page_loading_result:

                infraction_data_file = infraction_manager_page.get_traffic_tickets_data()

        self.driver.close()
        self.driver.quit()
        del self.driver
        print("Dados coletados com sucesso!")

    def is_page_loading(self):
        while True:
            try:
                html_page = WebDriverWait(self.driver, 3, 1).until(EC.presence_of_element_located(
                    locator=(By.XPATH, "//div[@class='loading-screen-icon']")))
            except:
                return False

    def infraction_identifier(self):

        database = Database()
        reader = Reader(database)
        updater = Updater(database, reader)
        print("Identifying driver")

        def get_all_unidentified_infractions() -> list[tuple] | None:
            infractions_data = reader.get_unidentified_infractions()
            if infractions_data:
                return infractions_data

        def is_it_aggravation(infraction) -> bool:
            if infraction[1]:
                return True
            return False

        def get_route_by_license_plate_and_date(license_plate: str, date: str) -> list[tuple] | None:
            route_data = reader.get_route_by_license_plate_and_date(
                license_plate=license_plate, date=date)

            if route_data:
                return route_data

        def infraction_on_the_day_off(license_plate, infraction_date) -> dict | None:
            # Obter o dia anterior
            infraction_date = datetime.datetime.strptime(
                infraction_date, "%d/%m/%Y")
            last_day = datetime.datetime.strftime(
                (infraction_date - datetime.timedelta(1)), "%d/%m/%Y")
            # Obter o dia seguinte
            next_day = datetime.datetime.strftime(
                (infraction_date + datetime.timedelta(1)), "%d/%m/%Y")

            last_day_rote = get_route_by_license_plate_and_date(
                license_plate=license_plate, date=last_day)
            next_day_rote = get_route_by_license_plate_and_date(
                license_plate=license_plate, date=next_day)

            # * Se o script conseguir encontrar as rotas do dia anterior e do dia seguinte e se as rotas foram feitas pelo mesmo motorista, se enquanda no dia de folga para identificar o motorista.

            # ? Identificando se houve as rotas
            if last_day_rote and next_day_rote:
                # ? Identificando se foram feitas com o mesmo motorista
                if last_day_rote[3].upper() == next_day_rote[3].upper():
                    driver_name = next_day_rote[3].upper()
                    driver_id = reader.get_employee_id_by_name(
                        employee_name=driver_name)
                    service_center = next_day_rote[0]
                    evidence = f"ROTA ANTERIOR E POSTERIOR A DATA DA MULTA: {
                        last_day_rote[1]} e {next_day_rote[1]}"
                    return {
                        'driver_id': driver_id,
                        'driver_name': driver_name,
                        'service_center': service_center,
                        'evidence': evidence,
                    }
            return None

        # ? Obter as infrações que estão com o status do sistema NULL que referem-se ao status "Não identificado"
        infractions_data = get_all_unidentified_infractions()

        if infractions_data:

            infraction_update_data_list = []
            for infraction in infractions_data:
                infraction_update_data = {}
                original_infraction = None

                infraction_update_data["AIT_number"] = infraction[0]

                if not is_it_aggravation(infraction):
                    # ? Se for uma infração deafult, obtém a data dela mesma
                    infraction_update_data["infraction_date"] = infraction[10].split()[
                        0]
                    # * Possibilidade de uso
                    infraction_update_data["infraction_hour"] = infraction[10].split()[
                        1]
                else:
                    # ? Busca a infração originária para obter a data
                    original_infraction = reader.get_infraction_data_by_AIT_number(
                        infraction[1])

                    if not original_infraction:
                        print(f"Infração originária não encontrada, infração originária: {infraction[1]}!")
                        continue

                    infraction_update_data["infraction_date"] = original_infraction[10].split()[
                        0]
                    # * Possibilidade de uso
                    infraction_update_data["infraction_hour"] = original_infraction[10].split()[
                        1]

                infraction_update_data["license_plate"] = infraction[2]

                route_data = get_route_by_license_plate_and_date(
                    license_plate=infraction_update_data["license_plate"],
                    date=infraction_update_data["infraction_date"])

                # Se a rota for encontrada, obter o nome do motorista
                if route_data:
                    # ! ADICIONAR VERIFICAÇÃO DA PLACA

                    infraction_update_data["driver_name"] = route_data[3].upper(
                    )
                    infraction_update_data["service_center"] = route_data[0]
                    infraction_update_data["driver_id"] = reader.get_employee_id_by_name(
                        employee_name=infraction_update_data["driver_name"])

                    infraction_update_data["evidence"] = f"NÚMERO DA ROTA: {
                        route_data[1]}"

                    infraction_update_data_list.append(infraction_update_data)
                else:
                    # ! Verificar se o motorista tomou a multa no dia de folga
                    # ! Validando se ele subiu rota um dia antes e um dia depois da infração
                    result = infraction_on_the_day_off(
                        license_plate=infraction_update_data["license_plate"],
                        infraction_date=infraction_update_data["infraction_date"])

                    if result:
                        # Unindo dois dicionários
                        infraction_update_data = infraction_update_data | result

                        infraction_update_data_list.append(
                            infraction_update_data)
                    else:
                        continue
            # Atualizar a infração com o nome do motorista e atualizar o status para identificado

            if infraction_update_data_list:
                updater.setAllDriverAndIdentificationStatus(
                    infraction_update_data_list=infraction_update_data_list)

        # ? Se não houver, buscar um dia antes e um dia depois, se houver, validar se os dois dias foi o mesmo motorista que subiu rota
        print("Indentification is done!")
        # ? Se sim, atribuir a multa para esse motorista.
        # ? Se não, deixar a multa sem motorista identificado.

    def nomination_date_has_expired(self):
        database = Database()
        reader = Reader(database)

        infractions_awaiting_indication = reader.get_infractions_awaiting_indication()
        status_to_update_list = []

        if infractions_awaiting_indication:
            today = datetime.datetime.now()

            for infraction in infractions_awaiting_indication:

                status_to_update = {}

                try:
                    deadline_for_nomination = datetime.datetime.strptime(
                        infraction[2], "%d/%m/%Y")

                    if today > deadline_for_nomination:
                        status_to_update = {
                            "AIT_number": infraction[0],
                            "nomination_status": 1,
                            "observation": "Prazo para indicação excedido"
                        }
                except ValueError:
                    if infraction[1]:
                        # ! Agravo com data de indicação expirada
                        status_to_update = {
                            "AIT_number": infraction[0],
                            "nomination_status": 1,
                            "observation": "Prazo para indicação excedido"
                        }
                    else:
                        print(f"Erro ao obter a data limite para indicação na multa: {
                              infraction[0]}")

                if status_to_update:
                    status_to_update_list.append(status_to_update.copy())

            updater = Updater(database, reader)

            if status_to_update_list:
                updater.updateNominationStatus(
                    status_to_update_list=status_to_update_list)

    def get_current_period(self):
        TODAY = datetime.datetime.now()

        YEAR = TODAY.year
        MONTH = TODAY.month

        if TODAY.day >= 1 and TODAY.day <= 15:
            FORTNIGHT = "Q1"
        else:
            FORTNIGHT = "Q2"

        MONTH = f"0{MONTH}" if MONTH < 10 else MONTH

        return f"{YEAR}{MONTH}{FORTNIGHT}"

    def get_last_invoice_id_inserted(self, reader: Reader):
        result = reader.get_last_invoice_id_inserted()
        if result:
            return result
        return "NULL"
    
    def get_invoice_period_by_id(self, id: int, reader: Reader):
        result = reader.get_invoice_period_by_id(id)
        if result:
            return result
        return "NULL"

    def send_to_payment_mirror_infraction_identified(self):
        DATABASE = Database()
        READER = Reader(DATABASE)

        infractions_awaiting_to_send_to_payment_mirror = READER.infractions_awaiting_send_payment_mirror_and_identified()
        infractions_to_send_to_payment_mirror = []

        if infractions_awaiting_to_send_to_payment_mirror:
            ID_INVOICE = self.get_last_invoice_id_inserted(READER)
            PERIOD = self.get_invoice_period_by_id(ID_INVOICE, READER)

            for infraction_data in infractions_awaiting_to_send_to_payment_mirror:
                infraction_date = infraction_data[4].split()[0]
                payment_data = {
                    "AIT_number": f"'{infraction_data[0]}'",
                    "id_invoice": ID_INVOICE,
                    "period": f"'{PERIOD}'",
                    "service_center": f"'{infraction_data[7]}'",
                    "employee_id": infraction_data[6],
                    "date": f"'{infraction_date}'",
                    "license_plate": f"'{infraction_data[2]}'",
                    "transaction_type": f"'DESCONTO'",
                    "value": -infraction_data[5],
                    "status": f"'PENDENTE'",
                    "observation": f"'{infraction_data[8]}'",
                }

                if not infraction_data[1]:
                    payment_data["description"] = f"'MULTA ** {
                        infraction_data[3]} AIT {infraction_data[0]}'"
                else:
                    payment_data["description"] = f"'AGRAVO ** {
                        infraction_data[3]} AIT {infraction_data[0]}'"

                infractions_to_send_to_payment_mirror.append(
                    payment_data.copy())

        if infractions_to_send_to_payment_mirror:
            UPDATER = Updater(DATABASE, READER)
            UPDATER.insert_infraction_discount_and_update_infraction_system_status(
                infractions_to_send_to_payment_mirror)


def getNewInfractionNotifications():
    application = Program()
    application.infractionDataCollector()
    application.infraction_identifier() #! VERIFICAÇÃO SOB ERROS
    application.nomination_date_has_expired()
    application.send_to_payment_mirror_infraction_identified() #* INSERÇÃO MANUAL
    del application

# getNewInfractionNotifications()

updateAllRoutesOfTheBeforeDay = datetime.time(14, 25)

schedule = sched.scheduler(time.time, time.sleep)


def check_hours():
    now = datetime.datetime.now().time()
    if now.hour == updateAllRoutesOfTheBeforeDay.hour and now.minute == updateAllRoutesOfTheBeforeDay.minute:

        print("Get new infraction notifications")

        schedule.enter(0, 1, getNewInfractionNotifications,
                       argument=())

    schedule.enter(60, 1, check_hours, ())


schedule.enter(0, 1, check_hours, ())

schedule.run()

getAllRoutesInThisHours = [
    datetime.time(10, 6),
    datetime.time(10, 10),
]

updateAllRoutesOfTheBeforeDay = datetime.time(7, 0)

schedule = sched.scheduler(time.time, time.sleep)


def check_hours():
    now = datetime.datetime.now().time()

    for hour in getAllRoutesInThisHours:
        if now.hour == hour.hour and now.minute == hour.minute:


            print('Start time', datetime.datetime.now())
            schedule.enter(0, 1, getNewInfractionNotifications,
                            argument=())


    schedule.enter(60, 1, check_hours, ())


schedule.enter(0, 1, check_hours, ())

schedule.run()

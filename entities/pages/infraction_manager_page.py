from entities.pages.page import Page
from entities.pages.page_tools.infraction_manager_page.infraction_manager_page_tools import InfractionManagerPageTools


class InfractionManagerPage(Page):
    def __init__(self, driver: object) -> None:
        super().__init__()

        self.driver = driver
        self.tools = InfractionManagerPageTools(driver)

    def get_in_page(self):

        # Entrar no painel gerenciador de multas
        self.driver.get(
            'https://frota360.localiza.com/gerenciador-infracoes/indicacoes-eletronicas')

    def get_traffic_tickets_data(self, initial_date: str = None, end_date: str = None) -> object:

        if not initial_date and not end_date:
            initial_date = self.tools.seven_days_before
            end_date = self.tools.yesterday

        self.tools.setting_filter_to_realease_date(initial_date, end_date)

        is_page_loading_result = self.tools.is_page_loading()

        if not is_page_loading_result:

            # ? Validação se no período solicitado existe alguma linha com dados de infração
            infractionDataRows = self.tools.get_infraction_rows()
            if len(infractionDataRows) >= 1:
                response = self.tools.update_infraction_report_data()

                # * Checando se existe algum arquivo de notificação de multas para excluir
                self.tools.delete_old_file()

                if response:
                    return {"status": "success"}
            return {"status": "error"}

        return None

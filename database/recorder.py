class Recorder():
    def __init__(self, database) -> None:
        self.database = database

    def insert_infraction_report_data(self, infraction_report_data_list: list[dict]):
        self.database.connection.start_transaction()
        for infraction_report_data in infraction_report_data_list:

            command = f"""
                INSERT INTO move_smart.infraction_data (
                    AIT_number, original_AIT, license_plate, description, value, email_date, shipping_date_to_customer, deadline_for_nomination, name_of_nominee, customer, infraction_date, release_date_of, referral_status, resource_status, reason, infraction_location, total_value)
                VALUES (
                    {infraction_report_data["AIT_number"]},
                    {infraction_report_data["original_AIT"]},
                    {infraction_report_data["license_plate"]},
                    {infraction_report_data["description"]},
                    {infraction_report_data["value"]},
                    {infraction_report_data["email_date"]},
                    {infraction_report_data["shipping_date_to_customer"]},
                    {infraction_report_data["deadline_for_nomination"]},
                    {infraction_report_data["name_of_nominee"]},
                    {infraction_report_data["customer"]},
                    {infraction_report_data["infraction_date"]},
                    {infraction_report_data["release_date_of"]},
                    {infraction_report_data["referral_status"]},
                    {infraction_report_data["resource_status"]},
                    {infraction_report_data["reason"]},
                    {infraction_report_data["infraction_location"]},
                    {infraction_report_data["total_value"]}
                )
            """
            self.database.cursor.execute(command)
        self.database.connection.commit()

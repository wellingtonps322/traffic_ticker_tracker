class Updater():
    def __init__(self, database: object, reader: object) -> None:
        self.database = database
        self.reader = reader

    def setAllDriverAndIdentificationStatus(self, infraction_update_data_list: list):

        self.database.connection.start_transaction()
        for infraction_update_data in infraction_update_data_list:
            command = f'''
                        UPDATE move_smart.infraction_data
                        SET driver_id = {infraction_update_data["driver_id"]},
                        driver_name = "{infraction_update_data["driver_name"]}",
                        service_center = "{infraction_update_data["service_center"]}",
                        evidence = "{infraction_update_data["evidence"]}",
                        identification_status = 1
                        WHERE AIT_number = "{infraction_update_data["AIT_number"]}"
                        '''
            self.database.cursor.execute(command)
        self.database.connection.commit()

    def updateNominationStatus(self, status_to_update_list: list[dict]):
        self.database.connection.start_transaction()
        for infraction_update_data in status_to_update_list:
            command = f'''
                        UPDATE move_smart.infraction_data
                        SET nomination_status = {infraction_update_data["nomination_status"]},
                        observation = "{infraction_update_data["observation"]}"
                        WHERE AIT_number = "{infraction_update_data["AIT_number"]}"
                        '''
            self.database.cursor.execute(command)
        self.database.connection.commit()

    def update_system_status(self, update_system_status_list):
        self.database.connection.start_transaction()
        for infraction_update_data in update_system_status_list:
            command = f'''
                        UPDATE move_smart.infraction_data
                        SET system_status = "{infraction_update_data["system_status"]}"
                        WHERE AIT_number = "{infraction_update_data["AIT_number"]}"
                        '''
            self.database.cursor.execute(command)
        self.database.connection.commit()

    def insert_infraction_discount_and_update_infraction_system_status(self, payment_list):
        self.database.connection.start_transaction()
        for payment_data in payment_list:
            insert_command = f'''
            INSERT INTO move_smart.payment_mirrors (
                id_invoice, period, description, service_center, employee_id, 
                date, license_plate, transaction_type, value, total, status, 
                observation, inserted_by
            ) VALUES (
                {payment_data["id_invoice"]}, {payment_data["period"]}, 
                {payment_data["description"]}, {payment_data["service_center"]}, 
                {payment_data["employee_id"]}, 
                {payment_data["date"]}, {payment_data["license_plate"]}, 
                {payment_data["transaction_type"]}, {payment_data["value"]}, 
                {payment_data["value"]}, {payment_data["status"]}, 
                {payment_data["observation"]}, 2
            );
            '''
            update_command = f'''
                UPDATE move_smart.infraction_data
                SET system_status = 1
                WHERE AIT_number = {payment_data["AIT_number"]};
            '''
            self.database.cursor.execute(insert_command)
            self.database.cursor.execute(update_command)
        self.database.connection.commit()
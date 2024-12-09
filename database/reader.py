class Reader():
    def __init__(self, database) -> None:
        self.database = database

    def get_infraction_data_by_AIT_number(self, AIT_number: str) -> tuple | None:
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.infraction_data
                    WHERE AIT_number = "{AIT_number}";
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchone()  # Read the database
        self.database.connection.commit()
        return result

    def get_unidentified_infractions(self) -> list[tuple] | list[None]:
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.infraction_data
                    WHERE identification_status IS NULL;
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        return result

    def get_employee_id_by_name(self, employee_name):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT id FROM move_smart.employee
                    WHERE name = "{employee_name}";
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchone()  # Read the database
        self.database.connection.commit()
        if len(result) > 0:
            return result[0]

    def get_route_by_license_plate_and_date(self, license_plate: str, date: str) -> tuple | None:
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.route
                    WHERE license_plate = "{license_plate}" and route_date = "{date}";
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        if len(result) > 0:
            return result[0]

    def get_infractions_awaiting_indication(self):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT AIT_number, original_AIT, deadline_for_nomination, system_status
                    FROM move_smart.infraction_data
                    WHERE nomination_status IS NULL;
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        if len(result) > 0:
            return result

    def get_routes_in_the_period_by_license_plate_and_date():
        ...

    def get_all_infractions_AIT_number(self):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT AIT_number FROM move_smart.infraction_data;
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        return result

    def get_payment_data_that_contains_on_description(self, data):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.payment_mirrors
                    WHERE description LIKE "%{data}";
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        return result

    def infractions_awaiting_send_payment_mirror_and_identified(self):
        ''' 
            #?Essa função irá buscar do banco de dados as infrações que 
            #?os motoristas foram identificados e que ainda não
            #?foram enviadas para o espelho de pagamento como desconto
        '''
        self.database.connection.start_transaction()
        command = f'''
                    SELECT AIT_number, original_AIT, license_plate, description,
                    infraction_date, total_value, driver_id, service_center, evidence
                    FROM move_smart.infraction_data
                    WHERE system_status IS NULL and identification_status = 1;
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        if len(result) > 0:
            return result

    def get_invoice_id_by_period(self, period):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT * FROM move_smart.invoice_information
                    WHERE period = "{period}";
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        if result:
            return result[0]
        return None
    
    def get_last_invoice_id_inserted(self):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT id FROM move_smart.invoice_information ORDER BY id DESC LIMIT 1;
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        if result:
            return result[0][0]
        return None
    
    def get_invoice_period_by_id(self, id: int):
        self.database.connection.start_transaction()
        command = f'''
                    SELECT period FROM move_smart.invoice_information
                    WHERE id = {id};
                    '''
        self.database.cursor.execute(command)
        result = self.database.cursor.fetchall()  # Read the database
        self.database.connection.commit()
        if result:
            return result[0][0]
        return None
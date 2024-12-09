from database.reader import Reader
from database.updater import Updater
from database.database import Database

import datetime

database = Database()
reader = Reader(database)

infractions_data = reader.get_all_infractions_AIT_number()

infraction_update_list = []
for infraction in infractions_data:

    response = reader.get_payment_data_that_contains_on_description(
        infraction[0])

    if response:

        infraction_update_list.append({
            "AIT_number": infraction[0],
            "system_status": 1
        })

if len(infraction_update_list) > 0:
    updater = Updater(database, reader=reader)
    updater.update_system_status(infraction_update_list)
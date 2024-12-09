import datetime
import time


def clock():
    specific_hours = [
        datetime.time(9, 0),
        datetime.time(11, 0),
        datetime.time(13, 0),
        datetime.time(15, 0),
        datetime.time(17, 0),
        datetime.time(19, 0),
        datetime.time(21, 0),
        datetime.time(23, 0)
    ]

    now = datetime.datetime.now().time()

    if now in specific_hours:
        return True
    else:
        time.sleep(600)

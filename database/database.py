import mysql.connector


class Database():
    def __init__(self) -> None:
        self.connection = mysql.connector.connect(
            user='***',
            password='***',
            host='***',
            port='***',
            database='***',
            connection_timeout=460,
            autocommit=False
        )
        self.cursor = self.connection.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

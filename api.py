"""
Основное приложение для обработки запросов
Проверяет все условия, сохраняет статусы транзакций, проводит транзакции и генерирует ответ
"""

import json
from server import Server
import psycopg2
import time


class API(Server):

    def parse_request(self, message):
        request_data = message.decode().split('\r\n\r\n')
        data = request_data[-1]
        headers = request_data[0]
        method = headers.split(' ')[0]

        request_message = json.loads(data)
        task = request_message['task']
        id = request_message['user_id']

        if task == 'make_transaction':
            transaction = request_message['transaction']

        else:
            transaction = ''

        return method, id, transaction, task

    def generate_headers(self, method):
        if method == 'POST':
            return ('HTTP/1.1 200 OK\r\n\r\n', 200)

    def save_history(self, user_id, transaction, status='in progress', mode='new', transaction_id=''):
        conn = psycopg2.connect(dbname='rest_api', user='postgres', password='45rtFGvb', host='localhost')
        cursor = conn.cursor()
        if mode == 'new':
            transaction_id = int(time.time())
            cursor.execute('INSERT INTO transactions (transaction_id, user_id, transaction_amount, status) '
                           'VALUES (%s,%s,%s,%s)', (transaction_id, user_id, transaction, status))

        elif mode == 'update':
            cursor.execute('UPDATE transactions SET status = %s WHERE transaction_id = %s and user_id = %s',
                           (status, transaction_id, user_id))

        conn.commit()

        cursor.close()
        conn.close()
        return transaction_id

    def make_transaction(self, user_id, transaction):
        conn = psycopg2.connect(dbname='rest_api', user='postgres', password='45rtFGvb', host='localhost')
        cursor = conn.cursor()
        cursor.execute('SELECT amount FROM users WHERE user_id = %s', (user_id, ))
        for item in cursor:
            balance = item[0]

        if float(balance) < float(transaction):
            response_messege = {"user_id": user_id,
                                "transaction_status": False,
                                "error": "insufficient funds"}
            status = 'blocked'

        else:
            balance = float(balance) - float(transaction)
            cursor.execute('UPDATE users SET amount = %s WHERE user_id = %s', (balance, user_id))
            conn.commit()
            response_messege = {"user_id": user_id,
                                "transaction_status": True,
                                "bakance": balance}
            status = 'finish'

        cursor.close()
        conn.close()

        return json.dumps(response_messege), status

    def get_history(self, user_id):
        conn = psycopg2.connect(dbname='rest_api', user='postgres', password='45rtFGvb', host='localhost')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM transactions WHERE user_id = %s', (user_id,))
        response_messege = {}
        for item in cursor:
            response_messege[item[0]] = {"user_id": item[1], "transaction": item[2], "status": item[3]}

        return json.dumps(response_messege)

    def handle(self, data):
        message, client_socket = data
        method, user_id, transaction, task = self.parse_request(message)

        header = self.generate_headers(method)[0]

        if task == 'make_transaction':
            transaction_id = self.save_history(user_id, transaction)

            response_messege, status = self.make_transaction(user_id, transaction)

            print(status)

            self.save_history(user_id, transaction, status=status, mode='update', transaction_id=transaction_id)

        elif task == 'get_history':
            self.get_history(user_id)

            response_messege = self.get_history(user_id)

        result_message = (header + response_messege).encode()

        self.send(client_socket, result_message)


if __name__ == "__main__":
    print("API started.")

    getter = API("localhost", 8887)
    getter.start_server()
    getter.loop()
    getter.stop_server()

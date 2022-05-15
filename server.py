"""
Сервер для обработки входящих запросов
Класс Server - базовый, на основе которого будем создавать приложения для обработки запросов
Метод handle при создании приложения переопределяем нужным нам образом
"""


import time

from server_queue import Queue


class Server:

    def __init__(self, ip, port):
        self.queue = Queue(ip, port)

    def start_server(self):
        self.queue.start_server()

    def stop_server(self):
        self.queue.stop_server()
        print('Stop server')

    def loop(self):
        while True:
            time.sleep(1)
            if self.queue.exists():
                self.handle(self.queue.get())

    def send(self, client_socket, message):
        try:
            print('Send response')
            client_socket.sendall(message)
        finally:
            print('Close connection')
            client_socket.close()

    def handle(self, message):
        pass

"""
Асинхронный сервер для создания очередей
Для каждого клиента создается своя очередь
"""

import threading
import socketserver


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        while True:
            try:
                data = self.request.recv(1024)
                self.server.queue.add(data, self.request)

            except OSError:
                print('Connection is closed')
                break

class Queue:

    def __init__(self, ip, port):
        self.server = ThreadedTCPServer((ip, port), ThreadedTCPRequestHandler)
        self.server.queue = self
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.messages = []

    def start_server(self):
        self.server_thread.start()
        print("Server loop running in thread:", self.server_thread.name)

    def stop_server(self):
        self.server.shutdown()
        self.server.server_close()

    def add(self, message, client_socket):
        self.messages.append((message, client_socket))

    def view(self):
        return self.messages

    def get(self):
        return self.messages.pop()

    def exists(self):
        return len(self.messages)

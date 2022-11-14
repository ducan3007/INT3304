import threading
import socket
from time import sleep
# from render import Render
from random import randint
from bingo import Bingo
from enum import Enum
from struct import *


hostname = socket.gethostname()

HOST = 'localhost'
PORT = 27003
KEY = 'flag{1234567890}'


class PKT(Enum):
    HELLO = 0
    PLAY = 4
    UPDATE = 5
    CREATEMAP = 2
    NOTICE = 3
    RESULT = 6
    START = 1
    END = 7


clients = dict()


class ClientThread(threading.Thread):
    def __init__(self, conn, address: str):
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.bingo = Bingo(5)

        # self.render = Render(self.bingo)

        # num = int(input("Nhập kích thước mảng"))
        try:
            while True:
                self.data = conn.recv(1024)

                # room_id = self.data.decode()

                print('echo', self.data)
                self.conn.send(self.data)

                if (Bingo.isWin()):
                    break

            self.conn.close()
            print(f'Connection to {address} closed')

        except Exception as e:
            print(e)
            self.conn.close()

    def decode_message(package):
        pass


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        print(f'Listening on {HOST}:{PORT}')
        self.server.listen()

    def start_server(self):
        conn, address = self.server.accept()
        threading.Thread(target=ClientThread, args=(conn, address[1])).start()


if __name__ == '__main__':
    server = Server()
    while True:
        server.start_server()

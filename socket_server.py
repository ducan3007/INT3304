import threading
import socket
from render import Render
from random import randint
from bingo import Bingo
from enum import Enum
from struct import *


hostname = socket.gethostname()

HOST = '112.137.129.129'
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


class ClientThread(threading.Thread):
    def __init__(self, conn, address: str, bingo: Bingo):
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.bingo = bingo(5)
        self.render = Render(self.bingo)

        try:
            while True:

                '''
                    Gọi Bingo trong này để update thông tin (board, history, current_move)
                    Sau đó Truyền bingo vào Render để render game ra console
                '''

                if (Bingo.isGameOver):
                    break

            self.conn.close()
            print(f'Connection to {address} closed')

        except Exception as e:
            print(e)
            self.conn.close()

    # hàm định nghĩa giao thức
    def decode_message(package):
        # return (type,data)
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

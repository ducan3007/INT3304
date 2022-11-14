from random import randint
import socket
import threading
from struct import *


hostname = socket.gethostname()
HOST = 'localhost'
PORT = 27003
KEY = 'flag{1234567890}'
T = (
    b'\x00\x00\x00\x00',  # 0
    b'\x01\x00\x00\x00',  # 1
    b'\x02\x00\x00\x00',  # 2
    b'\x03\x00\x00\x00',  # 3
    b'\x04\x00\x00\x00',  # 4
)


class ClientThread(threading.Thread):
    def __init__(self, conn, address):
        print(f'New client connected: {address}')
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.data = None
        self.result = None
        self.test = 20
        self.turns = 0
        self.correct = 0
        self.wrong = 0

        try:
            while self.turns < self.test and self.wrong <= self.test/5:
                self.turns += 1
                self.data = conn.recv(1024)

                print(f'-----------turns {self.turns}-----------')
                print(f'{self.address}: wrong  {self.wrong}')

                if(self.data[0:4] == T[0]):
                    print(f'{self.address}: Server received PKT 0')
                    self.make_pkt_1()

                elif(self.data[0:4] == T[2]):

                    print(f'{address}: Server received PKT 2')
                    result_type = int.from_bytes(self.data[8:12], 'big')

                    if result_type == 1:
                        received_result = int.from_bytes(self.data[12:16], 'big', signed=True)
                        print(f'{self.address}: received_result  {received_result}')
                        print(f'{self.address}: saved_result  {self.result}')
                        if(received_result == self.result):
                            self.win_check()
                        else:
                            self.lose_check()

                    elif result_type == 2:
                        received_result = format(unpack('f', self.data[12:16])[0], '.2f')
                        print(unpack('f', self.data[12:16])[0])
                        print(f'{self.address}: received_result  {received_result}')
                        print(f'{self.address}: saved_result  {self.result}')
                        if(received_result == self.result):
                            self.win_check()
                        else:
                            self.lose_check()

                    elif result_type == 3:
                        print('received_result 3:',  result_type)
                        if(self.result == 'infinity'):
                            self.win_check()
                        else:
                            self.lose_check()
                    else:
                        break
                else:
                    break
            conn.close()
            print(f'Connection to {address} closed')
        except Exception as e:
            conn.close()
            print(f'Error: {e}')

    # call after user's answer is correct
    def win_check(self):
        self.correct += 1
        if(self.correct >= self.test*4/5):
            self.send_pkt_4()
        else:
            self.make_pkt_1()

    # call after user's answer is wrong
    def lose_check(self):
        self.wrong += 1
        if(self.wrong > self.test/5):
            self.send_pkt_3()
        else:
            self.make_pkt_1()

    def make_pkt_1(self):
        a = randint(-1213434, 122213)
        b = randint(-3, 3)
        q = randint(1, 4)

        _type = T[1]
        _a = int.to_bytes(a, 4, 'little', signed=True)
        _b = int.to_bytes(b, 4, 'little', signed=True)
        _q = int.to_bytes(q, 4, 'big')
        _len = int.to_bytes(len(_a + _b + _q), 4, 'little')

        self.result = self.cal(a, b, q)  # saved for checking later
        self.conn.send(_type + _len + _a + _b + _q)

        print(f'{self.address}: a, b, q:', a, b, q)
        print(f'{self.address}: Server sent PKT 1')

    def cal(self, a, b, q):
        if(q == 1):
            return a + b
        elif(q == 2):
            return a - b
        elif(q == 3):
            return a * b
        elif(q == 4):
            if(b == 0):
                return 'infinity'
            # fix float
            return format(unpack('f', pack('f', a/b))[0], '.2f')

    def send_pkt_4(self):
        print(f'{self.address}: Correct!')
        print(f'{self.address}: Server sending pkg__4')

        type = b'\x04\x00\x00\x00'
        length = int.to_bytes(len(KEY.encode()), 4, 'little')
        self.conn.send(type + length + KEY.encode())

    def send_pkt_3(self):
        self.conn.send(b'\x03\x00\x00\x00')


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


# Compare threading.Thread vs 
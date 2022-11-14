from dataclasses import dataclass
from struct import *
import socket
from time import sleep

HOST = '112.137.129.129'
PORT = 27004
ID = '19020202'
TYPES = (
    b'\x00\x00\x00\x00',  # 0
    b'\x01\x00\x00\x00',  # 1
    b'\x02\x00\x00\x00',  # 2
    b'\x03\x00\x00\x00',  # 3
    b'\x04\x00\x00\x00',  # 4
)

class Client:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((self.host, self.port))
        print(f'Connected to {self.host}:{self.port}')

    def send_pkt_hello(self):
        _len = int.to_bytes(len(ID.encode()), 4, 'little')
        print('pkt_hello:', len(TYPES[0] + _len + ID.encode()))
        self.client.sendall(TYPES[0] + _len + ID.encode())

    def send(self, data):
        return self.client.sendall(data)

    def getbytes(self, data, type):
        if(type == 1):
            return int.to_bytes(data, 4, 'big', signed=True)
        if(type == 2):
            return pack('f', data)
        if(type == 3):
            return int.to_bytes(0, 4, 'big')

    def recv(self, size=1024):
        return self.client.recv(size)


if __name__ == '__main__':
    client = Client()
    client.send_pkt_hello()
    turns = 1
    while True:
        sleep(1)
        print(f'-----------turns {turns}-----------')

        data = client.recv(1024)
        # print(f' {data[0:4]}')
        # print(f' {data[4:8]}')
        # print(f' {data[8:16]}')
        # print(f' {data[16:20]}')
        # print(data)

        if(data[0:4] == TYPES[1]):
            print('client received PKT 1')
            lenth = int.from_bytes(data[4:8], 'little')
            a = int.from_bytes(data[8:12], 'little', signed=True)
            b = int.from_bytes(data[12:16], 'little', signed=True)
            q = int.from_bytes(data[16:20], 'big')

            print('recieved a, b, q:', a, b, q)

            result = 0
            result_type = 1  # 1 - int, 2 - float, 3 - invalid

            if(q == 1):
                result = a + b
            elif(q == 2):
                result = a - b
            elif(q == 3):
                result = a * b
            elif(q == 4 and b != 0):
                result_type = 2
                result = a/b
            elif(q == 4 and b == 0):
                result_type = 3

            _type = TYPES[2]
            _result = client.getbytes(result, result_type)
            _result_type = int.to_bytes(result_type, 4, 'big')
            _len = int.to_bytes(len(_result + _result_type), 4, 'little')

            print('sent result: ', result, unpack('f', _result)[0], format(unpack('f', _result)[0], '.2f'))

            client.send(_type + _len + _result_type + _result)
            print('client sent PKT 2')
        if (data[0:4] == TYPES[3]):
            print('client received PKT 3')
            break
        if (data[0:4] == TYPES[4]):
            print('client received PKT 4')
            length = int.from_bytes(data[4:8], 'little')
            key = data[8:8+length].decode()
            print('Successfully receive Key:', key)
            break
        if(data[0:4] == TYPES[0]):
            print('client received PKT 0')
            break
        turns += 1

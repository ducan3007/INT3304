from dataclasses import dataclass
import threading
from struct import *
import socket
from time import sleep

HOST = 'localhost'
PORT = 27003
ID = '19020202'
TYPES = (
    b'\x00\x00\x00\x00',  # 0
    b'\x01\x00\x00\x00',  # 1
    b'\x02\x00\x00\x00',  # 2
    b'\x03\x00\x00\x00',  # 3
    b'\x04\x00\x00\x00',  # 4
)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')


def send_pkt_hello():
    _len = int.to_bytes(len(ID.encode()), 4, 'little')
    print('pkt_hello:', len(TYPES[0] + _len + ID.encode()))
    client.sendall(TYPES[0] + _len + ID.encode())


def receive():
    while True:
        try:
            message = client.recv(1024)
            print('Received from server: ', message.decode())
        except:
            print("An error occured!")
            client.close()
            break


def write():
    while True:
        message = input('->Enter a number: ')
        client.send(message.encode())


# Client game cần 2 thread để vừa nghe và vừa gửi.
if __name__ == '__main__':

    # start receive thread
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    # start write thread
    receive_thread = threading.Thread(target=write)
    receive_thread.start()

    # while True:

    #     data = client.recv(1024)

    #     str = input('Enter a number: ')
    #     print('You entered', str)
    #     print('echo: ', data.decode())

    #     client.send(str.encode())

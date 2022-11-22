from dataclasses import dataclass
import threading
from struct import *
import socket
import protocol
from time import sleep
from bingo import Bingo
import sys
event = threading.Event()

HOST = 'localhost'
PORT = 27003
ID = '19020202'
SECRET_KEY = '12345678'
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

# Mã UUId của người chơi, 8 ký tự
UUID = 0

INPUT = None

ReceivedThread = False
bingo = Bingo(5)


class GameState:
    def __init__(self):
        self.won = False
        self.can_choose = False


state = GameState()


def send_pkt_hello():
    type = int.to_bytes(0, 4, 'little')
    print(SECRET_KEY)
    client.sendall(type + SECRET_KEY.encode())


def receive():
    global state
    global ReceivedThread

    send_pkt_hello()
    while True:

        try:
            message = client.recv(1024)
            TYPE = protocol._get_type(message)

            match TYPE:
                case 200:  # Khởi tạo
                    _len = protocol._get_ints(message[4:8])
                    sys.stdout.write("\r{} {} \n".format('200 :', message[8:8 + _len].decode()))

                case 100:  # Gói tin boardcast
                    len = protocol._get_ints(message[4:8])
                    sys.stdout.write("\r{} {} \n".format('100 :', protocol._get_str(message[8:8+len])))

                case 201:  # Gói tin bắt đầu game
                    bingo.x = protocol.deserialize_matrix(message[4:])[0]
                    bingo.game_board = protocol.deserialize_matrix(message[4:])[1]
                    bingo.printBoard()
                    sys.stdout.write("\r{} {} \n".format("(won, can choose):", state.won, state.can_choose))

                    client.send(protocol.get_next_move())

                case 202:  # Gói tin đến lượt
                    sys.stdout.write("\r{} {} \n".format('202 :', 'Đến lượt bạn: !'))
                    state.can_choose = True
                    ReceivedThread = True

                case 205:  # Gói tin update nước đi
                    n = protocol._get_ints(message[4:8])
                    sys.stdout.write("\r{} {} \n".format('205 :', f'Đối thủ chọn {n}!'))
                    bingo.update_and_print(int(n))

                case 401:
                    sys.stdout.write("\r{} \n".format('401 : Chưa đến lượt !'))
                    state.can_choose = False

                case 999:
                    state.won = True
                    sys.stdout.write("\r{} \n".format('999 : Bạn thắng !.'))
                    ReceivedThread = True
                    sys.exit()

                case 888:
                    state.won = True
                    sys.stdout.write("\r{} \n".format('888 : Hòa.'))
                    ReceivedThread = True
                    sys.exit()

                case 777:
                    state.won = True
                    sys.stdout.write('777 :THUA !.')
                    ReceivedThread = True
                    sys.exit()

                case 400:  # Gói tin từ request
                    sys.stdout.write("\r{} {} \n".format('400 :Connection rejected'))
                    client.close()

                case 401:  # Gói tin từ request
                    sys.stdout.write("\r{} {} \n".format('401 : Chưa đến lượt'))
                    client.close()

                case 500:  # Gói tin đóng kết nối
                    sys.stdout.write("\r{} {} \n".format('500 :Closing CONNECTION: ', message))
                    client.close()

        except Exception as e:
            sys.stdout.write(f'An error occured! {e}')
            sys.exit()
            # client.close()
            break


message = "Nhập số nguyên: \n"


def write():
    global message
    global ReceivedThread
    while True:
        sleep(0.1)
        if ReceivedThread is not True:
            continue

        if (state.won is True):
            break
        else:
            user_input = input(message)

        if (state.can_choose is True):

            if (user_input.strip().isdigit() is not True):
                sys.stdout.write("Nhập lại số nguyên: \n")
                message = ">"
                continue

            if (int(user_input) < 1 or int(user_input) > 25):
                sys.stdout.write("Nhập lại số nguyên từ 1 đến 25: \n")
                message = ">"
                continue

            if (bingo.isSelectedNumber(int(user_input)) is True):
                sys.stdout.write("Số đã được chọn: \n")
                message = ">"
                continue

        else:
            sys.stdout.write("Chưa đến lượt: \n")
            message = ">"

        if state.can_choose is True and user_input.strip().isdigit() and int(user_input) in range(1, bingo.size()+1):
            state.can_choose = False
            bingo.update_and_print(int(user_input))
            print('history', bingo.history)
            message = "Nhập số nguyên: \n"
            ReceivedThread = False
            client.send(protocol._select_number(int(user_input)))


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

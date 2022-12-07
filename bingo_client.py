import numpy as np
import threading
from struct import *
import socket
import protocol
from time import sleep
from bingo import Bingo
import sys
import json


HOST = 'localhost'  # Hoặc IP của máy
PORT = 27004
SECRET_KEY = '12345678'


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print(f'Connected to {HOST}:{PORT}')

# Mã UUId của người chơi, 8 ký tự
UUID = 0

INPUT = None

ReceivedThread = False
bingo = Bingo(5)
random_number = []


def red(str):
    return f'\x1b[7;30;41m {str} \x1b[0m'


def green(str):
    return f'\x1b[7;30;42m{str} \x1b[0m'


class GameState:
    def __init__(self):
        self.won = False
        self.can_choose = False


state = GameState()


def send_pkt_hello():  # khởi tạo kết nối
    type = int.to_bytes(0, 4, 'little')
    print(SECRET_KEY)
    client.sendall(type + SECRET_KEY.encode())


def receive():
    global state
    global ReceivedThread
    global random_number

    send_pkt_hello()
    while True:

        try:
            message = client.recv(1024)
            TYPE = protocol._get_type(message)

            match TYPE:
                case 200:  # Khởi tạo
                    _len = protocol._get_ints(message[4:8])
                    sys.stdout.write("\r{} {} \n".format(f'{green(200)} :', message[8:8 + _len].decode()))

                case 100:  # Gói tin boardcast
                    len = protocol._get_ints(message[4:8])
                    sys.stdout.write("\r{} {} \n".format(f'{green(100)} :', protocol._get_str(message[8:8+len])))

                case 201:  # Server trả về Gói tin bắt đầu game
                    import random
                    bingo.x = protocol.deserialize_matrix(message[4:])[0]
                    bingo.game_board = protocol.deserialize_matrix(message[4:])[1]

                    # random mang co bingo.x so
                    random_number = random.sample(range(1, bingo.x**2 + 1), bingo.x**2)

                    # Them UI vao day
                    bingo.printBoard()
                    sys.stdout.write("\r{} {} \n".format("(Won, Can choose):", state.won, state.can_choose))

                    client.send(protocol.get_next_move())

                case 202:  # Server trả về Gói tin đến lượt
                    sys.stdout.write("\r{} {} \n".format(f'{green(202)} :', 'Đến lượt bạn: !'))
                    state.can_choose = True
                    ReceivedThread = True

                case 205:  # Gói tin update nước đi
                    n = protocol._get_ints(message[4:8])
                    sys.stdout.write("\r{} {} \n".format(f'{green(205)} :', f'Đối thủ chọn {n}!'))
                    random_number.remove(n)
                    bingo.update_and_print(int(n))

                case 222:  # Hiển thị kết quả của người choi còn lại, data là matrix và history
                    sys.stdout.write("\r{} {} \n".format(f'{green(222)} :', f'Kết quả của đối thủ'))

                    n = protocol._get_ints(message[4:8])
                    matrix = protocol.deserialize_matrix(message[8:8+n])

                    m = protocol._get_ints(message[8+n:12+n])
                    history_temp = json.loads(message[12+n:12+n+m].decode())

                    history = dict()

                    for i in history_temp:
                        history[int(i)] = (history_temp[i][0], history_temp[i][1])

                    opponent_bingo = Bingo(matrix[0])
                    opponent_bingo.game_board = matrix[1]
                    opponent_bingo.history = history
                    opponent_bingo.printBoard()

                    state.won = True
                    ReceivedThread = True
                    sys.exit()

                case 401:
                    sys.stdout.write("\r{} \n".format(f'{red(401)} : Chưa đến lượt !'))
                    state.can_choose = False

                case 999:
                    sys.stdout.write("\r{} \n".format(f'{green(999)} : Bạn thắng !.'))

                case 1000:
                    state.won = True
                    ReceivedThread = True
                    sys.stdout.write("\r{} \n".format(f'{green(1000)} : Đối thủ thoát Bạn thắng !.'))
                    client.close()
                    sys.exit()

                case 888:
                    sys.stdout.write("\r{} \n".format(f'{green(999)} : Hòa.'))

                case 777:
                    sys.stdout.write(f'{red(777)} : THUA !')

                case 400:  # Gói tin từ request
                    sys.stdout.write("\r{} {} \n".format('400 :Connection rejected'))
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
    global random_number
    while True:
        sleep(1)
        if ReceivedThread is not True:
            continue

        if (state.won is True):
            break
        # else:
        #     user_input = random_number.pop()
        #     sys.stdout.write("\r{} \n".format(f'{user_input} : PICK !.'))
        if (state.can_choose is True):
            pass
            # if (user_input.strip().isdigit() is not True):
            #     sys.stdout.write("Nhập lại số nguyên: \n")
            #     message = ">"
            #     user_input = None
            #     continue

            # if (int(user_input) < 1 or int(user_input) > 25):
            #     sys.stdout.write("Nhập lại số nguyên từ 1 đến 25: \n")
            #     message = ">"
            #     user_input = None
            #     continue

            # if (bingo.isSelectedNumber(int(user_input)) is True):
            #     sys.stdout.write("Số đã được chọn: \n")
            #     message = ">"
            #     user_input = None
            #     continue

        else:
            sys.stdout.write("Chưa đến lượt: \n")
            message = ">"

        if state.can_choose is True:
            user_input = random_number.pop()
            # sys.stdout.write(''.join(str(x) for x in random_number))
            sys.stdout.write("\r{} \n".format(''.join(str(x) for x in random_number)))
            state.can_choose = False
            bingo.update_and_print(int(user_input))
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

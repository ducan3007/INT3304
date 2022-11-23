import threading
import socket
from time import sleep
# from render import Render
from random import randint
import protocol
from bingo import Bingo
from enum import Enum
from struct import *
import random
import string
import json

hostname = socket.gethostname()

HOST = 'localhost'
PORT = 27003
KEY = 'flag{1234567890}'

LEVEL = 3 # 3x3


class PKT(Enum):
    HELLO = 0
    PLAY = 4
    UPDATE = 5
    CREATEMAP = 2
    NOTICE = 3
    RESULT = 6
    START = 1
    END = 7


# Biến Global Dùng để lưu thông tin game của các room


# Để ý hai cái này
# Biến Globlal Dùng để lưu các cặp (socket_client 1,socket_client 2) theo room
#
# Clients = {id1: socket_client1, id2: socket_client2}}
Clients = dict()

# Biến Global Dùng để lưu các bàn chơi theo room
# Bingos = {room_id: {uuid1: Bingo, uuid2: Bingo}}
Bingos = dict()

# Biến Global Dùng để lưu lượt đi tiếp theo
NextMove = dict()

# Khởi tạo mặc định 5 phòng có room_id từ 1 đến 5
for i in range(5):
    Bingos[f'{i}'] = dict()


# Chưa cần dùng đến
MessageQueue = dict()


class ClientThread(threading.Thread):

    def __init__(self, conn, address: str):
        threading.Thread.__init__(self)

        self.conn = conn
        self.address = address

        self.msg_queue = []
        # self.bingo = Bingo(5)

        # Mình lưu id vào thread này, id này Client ko biết được
        self.data = None
        self.room_id = None
        self.uuid = create_uuid()

        try:
            while True:

                self.data = conn.recv(1024)

                print('================================================================')

                TYPE = protocol._get_type(self.data)

                match TYPE:  # Switch case các TYPE của gói

                    case 0:  # khởi tạo kết nối

                        Clients[self.uuid] = conn
                        print(f'0 : Client {self.uuid} connected')
                        self.accept_connection()

                        # Tìm trận, sẽ gửi hai matrix cho hai người
                        if self.find_match() is True:

                            # Lấy id của người còn lại trong phòng
                            opponent_id = self.get_opponent_id()
                            if (opponent_id is None):
                                continue

                            # Serialize matrix của hai người trước khi gửi
                            opponent_matrix = self.getOpponentBingo().serialize_matrix()
                            my_matrix = self.getBingo().serialize_matrix()

                            # for uuid in Clients:
                            #     if uuid in opponent_id:
                            #         print('0 : Sent matrix to ', uuid)
                            #         Clients[opponent_id].sendall(protocol._server_match_making(opponent_matrix))

                            #     if uuid in self.uuid:
                            #         print('0 : Sent matrix to ', uuid)
                            #         Clients[uuid].sendall(protocol._server_match_making(my_matrix))

                            #         print('0: Sent can move to ', uuid)

                            print('0 : Sent matrix to ', self.uuid)
                            Clients[opponent_id].sendall(protocol._server_match_making(opponent_matrix))

                            print('0 : Sent matrix to ', self.uuid)
                            Clients[self.uuid].sendall(protocol._server_match_making(my_matrix))

                        self.server_state()

                    case 203:  # client chọn một số
                        ooponent_id = self.get_opponent_id()
                        # Kiểm tra đến lượt của mình chưa, bếu đến lượt thì cập nhật game info
                        if NextMove[self.room_id] != self.uuid:
                            Clients[self.uuid].send(protocol.cant_move())
                            continue

                        # Lấy số của mình chọn và  gửi người chơi còn lại
                        n = protocol._get_ints(self.data[4:8])
                        Clients[ooponent_id].send(protocol.update_board(n))

                        print(f'Client {self.uuid} choose {n}')

                        # Kiểm tra xem số đó có hợp lệ không
                        if (n > self.getBingo().size() or n < 0):
                            Clients[self.uuid].send(protocol.invalid_move())
                            continue

                        # Bắt đầu cập nhật dữ liệu hai mt ở Server
                        pos_1 = self.getBingo().pos(int(n))
                        pos_2 = self.getOpponentBingo().pos(int(n))
                        self.getBingo().update(pos_1[0], pos_1[1], int(n))
                        self.getOpponentBingo().update(pos_2[0], pos_2[1], int(n))

                        # 888 : Nếu cả hai thắng thì gửi thông báo hòa, gửi kết qủa cho hai người chơi
                        if self.getBingo().isWin() and self.getOpponentBingo().isWin():
                            print('888 : Hòa')

                            for i in range(3):
                                if i == 0:
                                    Clients[self.uuid].send(protocol.game_draw())
                                if i == 1:
                                    Clients[ooponent_id].send(protocol.game_draw())
                                if i == 2:
                                    self.sent_result_matrix_to_all()

                        # 777 : Mình thắng, bên kia thua
                        if self.getBingo().isWin():
                            print('777 : ', self.uuid, ' win')

                            for i in range(3):
                                if i == 0:
                                    Clients[self.uuid].send(protocol.you_won())
                                if i == 1:
                                    Clients[ooponent_id].send(protocol.you_lost())
                                if i == 2:
                                    self.sent_result_matrix_to_all()

                        if self.getOpponentBingo().isWin():
                            print('777 2 : ', ooponent_id, ' win')

                            for i in range(3):
                                if i == 0:
                                    Clients[self.uuid].send(protocol.you_lost())
                                if i == 1:
                                    Clients[ooponent_id].send(protocol.you_won())
                                if i == 2:
                                    self.sent_result_matrix_to_all()

                        else:
                            print('Continue')
                            NextMove[self.room_id] = ooponent_id
                            Clients[ooponent_id].send(protocol.can_move())

                    case 204:
                        if NextMove[self.room_id] != self.uuid:
                            Clients[self.uuid].send(protocol.cant_move())
                        else:
                            Clients[self.uuid].send(protocol.can_move())

                    case other:

                        self.conn.close()

        except Exception as e:
            print("ERROR: ", e)
            self.clean_up_function()
            # self.conn.close()

    def getBingo(self):
        return Bingos[self.room_id][self.uuid]

    def getOpponentBingo(self):
        return Bingos[self.room_id][self.get_opponent_id()]

    # Gửi kết quả ma trận cho cả hai
    def sent_result_matrix_to_all(self):
        print("SEND TO ALLL")
        opponent_history = json.dumps(self.getOpponentBingo().history)
        my_history = json.dumps(self.getBingo().history)

        Clients[self.uuid].send(protocol.send_result(
            self.getOpponentBingo().serialize_matrix(), opponent_history.encode()))

        Clients[self.get_opponent_id()].send(protocol.send_result(
            self.getBingo().serialize_matrix(), my_history.encode()))

    # Tìm phòng

    def find_match(self):
        # Nếu người chơi đã vào phòng từ trước
        for Room in Bingos:

            if (self.uuid in Room):
                print(f'Player {self.uuid} already in room ')
                return False

        # Check Phòng có 1 người
        for Room in Bingos:

            if len(Bingos[Room]) == 2:
                continue

            if len(Bingos[Room]) == 1:

                # Tạo bàn chơi mới
                self.bingo = Bingo(LEVEL)

                # ánh xạ uuid của client vào Bingo
                Bingos[Room][self.uuid] = self.bingo
                self.room_id = Room
                NextMove[self.room_id] = self.uuid

                # Lưu lại phòng của người chơi
                print(f'Player {self.uuid} matched room {self.room_id}')
                return True

        # Check phòng chưa có ai => thêm vào phòng chống
        for Room in Bingos:

            if len(Bingos[Room]) == 0:

                # Tao bàn chơi mới và luu vào dict Bingos
                self.bingo = Bingo(LEVEL)
                self.room_id = Room
                Bingos[Room][self.uuid] = self.bingo
                print('Joined Room', Bingos[Room])
                return False

        return False

    def boardcast(self):
        for uuid in Clients:
            if uuid != self.uuid:
                Clients[uuid].send(protocol._server_boardcast(f'Client {self.uuid} has joined the server'.encode()))

    # lấy id của đối thủ trong phòng để boardcast
    def get_opponent_id(self):
        if (self.room_id is not None):
            for uuid in Bingos[self.room_id]:
                if uuid != self.uuid:
                    return uuid
        return None

    # chấp nhận kết nối
    def accept_connection(self):
        self.conn.send(protocol.accept_connection(self.uuid))

    # từ chối kết nối
    def reject_connection(self):
        self.conn.send(int.to_bytes(400, 4, 'little'))

    # dọng dẹp sau khi người dùng hủy kết nối
    def clean_up_function(self):
        print("clean up function")

        # đóng kết nối, xóa Bingo
        del Bingos[self.room_id][self.uuid]
        del Clients[self.uuid]

        # gửi thông báo Chiến thắng cho đối thủ
        opponent_id = self.get_opponent_id()

        if (opponent_id is not None):
            print('999: ', opponent_id)
            Clients[opponent_id].send(protocol.you_won())

        # Kiểm tra state
        self.server_state()

    def server_state(self):
        print('----------------- SERVER STATE -----------------')
        for Room in Bingos:
            for uuid in Bingos[Room]:
                print(f'Room {Room}, {uuid} : \n {Bingos[Room][uuid].game_board}')

        for uuid in Clients:
            print(f'Client {uuid} : {Clients[uuid]}')
        print('-----------------------------------------------')


def create_uuid():
    return ''.join(random.choice(string.digits) for _ in range(8))


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        print(f'Listening on {HOST}:{PORT}')
        self.server.listen()

    def start_server(self):
        try:
            conn, address = self.server.accept()
            threading.Thread(target=ClientThread, args=(conn, address[1])).start()
        except Exception as e:
            print("Server error: ", e)


if __name__ == '__main__':
    server = Server()
    while True:
        server.start_server()

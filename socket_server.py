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

LEVEL = 5


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

'''
Flows: CÓ THỂ KHÔNG ĐÚNG, phải làm mới biết dc.

Làm sao để Server chủ động push cho client1 biết là đến lượt chọn của mình, khi mà client2 đã chọn xong nước đi ? => Các client ở Thread khác nhau ?
 => Lưu lại socket của tất cả client ở Global

+ Đầu tiên ta cần mã phòng (zoom_id) cho 2 Client, mã có thể auto tạo ở phía Server, hoặc một trong hai Client yêu cầu tạo mã phòng để lấy mã.

+ Mã phòng sẽ lưu vào dict Clients ở trên: với key chính là Mã phòng, value là 1 mảng [(uuid1, socket_client1), (uuid2, socket_client2)]. Dựa vào uuid để xác định Client nào.

+ Tại sao cần mã phòng và lưu vào Clients trên?

=> Để broadcast đến tất cả Client khi có update mới nhất, ví dụ client2 gửi gói update game, lúc này nếu ko lưu lại socket của client1 thì chỉ có socket_client2 nhận được update từ Server.

Client1 vẫn chưa biết gì vì socket_clinet1 ở một Thread khác. ( CODE tham khảo boardcast ở trong ./sample/chat_broadcast )

+ Server sẽ dựa vào mã phòng để gửi thông tin mới update cho tất cả người chơi dùng trong phòng đó.

Ví dụ:

# khởi tạo
Clients[zoom_id] = [(uuid1, client1), (uuid2, client2)]
# Lưu trạng thái chung của bàn chơi, tránh cheat, có lưu lại 'next_turn', để xác định tiếp theo ai được đi.
Bingos[zoom_id] = (),

# Khi client2 chọn một số, thì :

    # boardcast thông tin mới nhất
    for uuid, socket_client in Clients[zoom_id]:
        socket_client.send(next_turn)

            // next_turn là gói tin CÓ THỂ bao gồm:
            + turn: uuid của người chơi có lượt tiếp theo (hoặc là gì cx được, nói chung là biết ai vừa đi)
            + giá trị nước đi đó: để client còn lại cập nhật (Theo luật thì nếu client2 chọn '5' mà client1 chưa chọn '5' thì client1 sẽ ăn số '5' ấy )


+ Các package còn lại làm như bình thường


'''

# Để ý hai cái này

# Biến Globlal Dùng để lưu các cặp (socket_client 1,socket_client 2) theo room
#
# Clients = {uuid1: socket_client1, uuid2: socket_client2}}
Clients = dict()

# Biến Global Dùng để lưu các bàn chơi theo room
#
# Bingos = {room_id: {uuid1: Bingo, uuid2: Bingo}}
Bingos = dict()

NextMove = dict()

# Khởi tạo mặc định 5 phòng có room_id từ 1 đến 5
for i in range(5):
    Bingos[f'{i}'] = dict()

print(Bingos)

#
MessageQueue = dict()


class ClientThread(threading.Thread):

    def __init__(self, conn, address: str):
        threading.Thread.__init__(self)

        # push socket vào dict Clients

        self.conn = conn
        self.address = address

        # self.bingo = Bingo(5)

        self.data = None
        self.room_id = None
        self.msg_queue = []

        # ID giúp server định danh Socket của Client
        self.uuid = create_uuid()

        # self.render = Render(self.bingo)

        # num = int(input("Nhập kích thước mảng"))
        try:
            while True:

                self.data = conn.recv(1024)

                print('================================================================')

                TYPE = protocol._get_type(self.data)

                match TYPE:

                    case 0:  # khởi tạo kết nối

                        Clients[self.uuid] = conn
                        print(f'0 : Client {self.uuid} connected')
                        self.accept_connection()

                        if self.match_making() is True:
                            opponent_id = self.get_opponent_id()
                            if (opponent_id is None):
                                continue

                            opponent_matrix = self.getOpponentBingo().serialize_matrix()
                            my_matrix = self.getBingo().serialize_matrix()

                            for uuid in Clients:
                                if uuid in opponent_id:
                                    print('Sent matrix to ', uuid)
                                    Clients[uuid].sendall(protocol._server_match_making(opponent_matrix))

                                if uuid in self.uuid:
                                    print('Sent matrix to ', uuid)
                                    Clients[uuid].sendall(protocol._server_match_making(my_matrix))

                                    print('Sent can move to ', uuid)

                        self.server_state()

                    case 203:  # client chọn một số

                        # Kiểm tra đến lượt chơi chưa
                        if NextMove[self.room_id] != self.uuid:
                            Clients[uuid].send(protocol.cant_move())
                            continue

                        # Nếu đến lượt thì cập nhật game info
                        n = protocol._get_ints(self.data[4:8])

                        # Gửi số vừa chọn cho người chơi còn lại
                        Clients[self.get_opponent_id()].send(protocol.update_board(n))

                        print(f'Client {self.uuid} choose {n}')

                        if (n > self.getBingo().size() or n < 0):
                            Clients[uuid].send(protocol.invalid_move())
                            continue

                        pos_1 = self.getBingo().pos(int(n))
                        pos_2 = self.getOpponentBingo().pos(int(n))

                        self.getBingo().update(pos_1[0], pos_1[1], int(n))
                        self.getOpponentBingo().update(pos_2[0], pos_2[1], int(n))

                        print("Bingo board: ", self.uuid,  self.getBingo().game_info)
                        print("Bingo history: ", self.uuid,  self.getBingo().history)
                        print("Bingo board: ", self.get_opponent_id(),  self.getOpponentBingo().game_info)
                        print("Bingo history: ", self.get_opponent_id(),  self.getOpponentBingo().history)

                        # 888 : Nếu cả hai thắng thì gửi thông báo hòa, gửi ma trận cho cả hai
                        if self.getBingo().isWin() and self.getOpponentBingo().isWin():
                            print('888 : Draw')

                            Clients[self.uuid].send(protocol.game_draw())
                            Clients[self.get_opponent_id()].send(protocol.game_draw())

                            # self.sent_result_matrix_to_all()

                        # 777 : Mình thắng, bên kia thua
                        if self.getBingo().isWin():
                            print('777 : ', self.uuid, ' win')

                            Clients[self.uuid].send(protocol.you_won())
                            Clients[self.get_opponent_id()].send(protocol.you_lost())
                            # self.sent_result_matrix_to_all()

                        if self.getOpponentBingo().isWin():
                            print('777 : ', self.get_opponent_id(), ' win')
                            Clients[self.uuid].send(protocol.you_lost())
                            Clients[self.get_opponent_id()].send(protocol.you_won())

                        else:
                            print('Continue')
                            NextMove[self.room_id] = self.get_opponent_id()
                            Clients[self.get_opponent_id()].send(protocol.can_move())

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

    '''
        Hàm này dùng để tìm trận
        Output: True or False nếu tìm được
    '''

    def getBingo(self):
        return Bingos[self.room_id][self.uuid]

    def getOpponentBingo(self):
        return Bingos[self.room_id][self.get_opponent_id()]

    # Gửi kết quả ma trận cho cả hai
    def sent_result_matrix_to_all(self):
        opponent_history = json.dumps(self.getOpponentBingo().history)
        my_history = json.dumps(self.getBingo().history)

        for uuid in Clients:
            if uuid in self.uuid:
                Clients[uuid].send(protocol.send_result(
                    self.getOpponentBingo().serialize_matrix(), opponent_history.encode()))

            if uuid in self.get_opponent_id():
                Clients[uuid].send(protocol.send_result(
                    self.getBingo().serialize_matrix(), my_history.encode()))
    # Tìm phòng

    def match_making(self):
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
        # gửi package disconnect

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
        # self.conn.send(protocol.server_error())

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

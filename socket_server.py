import json
import string
import random
import redis
from struct import *
from enum import Enum
from bingo import Bingo
import protocol
from random import randint
import threading
import socket
import time
# from render import Render


# hostname = socket.gethostname()

# hostname = socket.gethostname()
# HOST = socket.gethostbyname(hostname)

HOST = 'localhost'
PORT = 27003
KEY = 'flag{1234567890}'

LEVEL = 5  # 3x3

redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")

# Clients = {id1: socket_client1, id2: socket_client2}}
Clients = dict()

# Bingos = {room_id: {uuid1: Bingo, uuid2: Bingo}}
Bingos = dict()
MatchID = dict()

# Biến Global Dùng để lưu lượt đi tiếp theo
NextMove = dict()

History = dict()

# For Redis

RoomList = dict()


# Khởi tạo mặc định 5 phòng có room_id từ 1 đến 5
for i in range(10):
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
        self.room_id = ''
        self.match_id = ''
        self.opponent_id = ''
        self.uuid = create_uuid()
        self.winner = ''

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

                        # Bắt đầu cập nhật dữ liệu hai người chơi ở Server
                        pos_1 = self.getBingo().pos(int(n))
                        pos_2 = self.getOpponentBingo().pos(int(n))
                        self.getBingo().update(pos_1[0], pos_1[1], int(n))
                        self.getOpponentBingo().update(pos_2[0], pos_2[1], int(n))

                        # Lưu cả người chơi vào Redis
                        self.redis_save_bingos(self.uuid)
                        self.redis_save_openent_bingo(ooponent_id)

                        # 888 : Nếu cả hai thắng thì gửi thông báo hòa, gửi kết qủa cho hai người chơi
                        if self.getBingo().isWin() and self.getOpponentBingo().isWin():
                            print('888 : Hòa')
                            self.bingo.win = True
                            self.getOpponentBingo().win = True

                            for i in range(3):
                                if i == 0:
                                    Clients[self.uuid].send(protocol.game_draw())
                                if i == 1:
                                    Clients[ooponent_id].send(protocol.game_draw())
                                if i == 2:
                                    self.sent_result_matrix_to_all()

                        # 777 : Mình thắng, bên kia thua
                        if self.getBingo().isWin():
                            self.bingo.win = True
                            print('777 : ', self.uuid, ' win')

                            for i in range(3):
                                if i == 0:
                                    Clients[self.uuid].send(protocol.you_won())
                                if i == 1:
                                    Clients[ooponent_id].send(protocol.you_lost())
                                if i == 2:
                                    self.sent_result_matrix_to_all()

                        if self.getOpponentBingo().isWin():
                            self.getOpponentBingo().win = True
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
                            self.server_state()
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

    # Gửi kết quả ma trận cho cả hai khi vấn đấu kết thúc
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

                # Tạo bàn chơi mới và lưu Game_Board và History vào Redis
                self.bingo = Bingo(LEVEL)
                self.redis_save_bingos(self.uuid)

                # Ánh xạ uuid của client vào Bingo
                Bingos[Room][self.uuid] = self.bingo
                self.room_id = Room
                self.match_id = MatchID[Room]
                NextMove[self.room_id] = self.uuid

                # Lưu lại phòng của người chơi
                print(f'Player {self.uuid} matched room {self.room_id}')
                return True

        # Check phòng chưa có ai => thêm vào phòng chống
        for Room in Bingos:

            if len(Bingos[Room]) == 0:

                # Tao bàn chơi mới và luu vào dict Bingos, Lưu vào Redis
                self.bingo = Bingo(LEVEL)
                self.redis_save_bingos(self.uuid)

                # Tạo match_id
                match_id = create_uuid()
                MatchID[Room] = match_id

                self.room_id = Room
                self.match_id = match_id

                Bingos[Room][self.uuid] = self.bingo
                print('Joined Room', Bingos[Room])
                return False

        return False

    # Lấy id của đối thủ trong phòng để boardcast
    def get_opponent_id(self) -> str:
        if (self.room_id is not None):
            for uuid in Bingos[self.room_id]:
                if uuid != self.uuid:
                    self.opponent_id = uuid
                    return uuid

        return

    def accept_connection(self):
        self.conn.send(protocol.accept_connection(self.uuid))

    def reject_connection(self):
        self.conn.send(int.to_bytes(400, 4, 'little'))

    # Dọn dẹp sau khi người dùng hủy kết nối
    def clean_up_function(self):

        self.redis_save_game_history()
        print("clean up function")

        # đóng kết nối, xóa Bingo
        del Bingos[self.room_id][self.uuid]
        del Clients[self.uuid]
        # del NextMove[self.room_id]

        redisClient.delete(f'game_board:{self.uuid}')
        redisClient.delete(f'history:{self.uuid}')

        if len(Bingos[self.room_id]) == 0:
            if self.room_id in History:
                del History[self.room_id]
                del MatchID[self.room_id]

        # Lưu lịch sử của games

        # gửi thông báo Chiến thắng cho đối thủ
        opponent_id = self.get_opponent_id()

        if (opponent_id is not None):
            print('999: ', opponent_id)
            self.bingo.win = True
            Clients[opponent_id].send(protocol.you_won_enemy_out())

        self.server_state()

    def server_state(self):
        print('----------------- SERVER STATE -----------------')
        # print("NextMove: ", NextMove)
        print("MatchID", MatchID)
        print("History", History)
        # print(Bingos)
        self.redis_save_game_state()
        print('-----------------------------------------------')

    '''
    Lưu vào REDIS
    '''

    def redis_save_game_state(self):
        redis_data = dict()
        for room in Bingos:
            # print('ROOM: ', room)
            redis_data[room] = dict()
            redis_data[room]['players'] = []
            redis_data[room]['next_move'] = ''

            for uuid in Bingos[room]:
                redis_data[room]['players'].append(uuid)
                if (len(Bingos[room]) == 2):
                    redis_data[room]['next_move'] = NextMove[room]

        redisClient.set('game_state', json.dumps(redis_data))

        # print("redis_data:", redis_data)

    def redis_save_bingos(self, ID):
        redisClient.set(f'game_board:{ID}', self.bingo.to_json()['board'])
        redisClient.set(f'history:{ID}', self.bingo.to_json()['history'])

    def redis_save_openent_bingo(self, ID):
        redisClient.set(f'game_board:{ID}', self.getOpponentBingo().to_json()['board'])
        redisClient.set(f'history:{ID}', self.getOpponentBingo().to_json()['history'])

    def redis_save_game_history(self):
        if (len(Bingos[self.room_id]) != 2):
            return
        # Lưu vào Redis [ match_id + room_id + 2 uid + 2 game_board + 2 history ]

        endTime = round(time.time()*1000)
        # Nếu đã có match_id trong hitory tì không lưu nữa
        if self.match_id not in History:

            win = ''

            if self.bingo.win:
                win = str(self.uuid)
            else:
                win = str(self.opponent_id)

            print('win: ', win)

            win = win.encode()
            win_len = protocol._int_to_bytes(len(win))

            math_id = self.match_id.encode()
            math_id_len = protocol._int_to_bytes(len(math_id))

            room_id = self.room_id.encode()
            room_id_len = protocol._int_to_bytes(len(room_id))

            uid_1 = self.uuid.encode()
            uid_1_len = protocol._int_to_bytes(len(uid_1))

            uid_2 = self.get_opponent_id().encode()
            uid_2_len = protocol._int_to_bytes(len(uid_2))

            game_board_1 = self.bingo.serialize_matrix()
            game_board_1_len = protocol._int_to_bytes(len(game_board_1))

            game_board_2 = self.getOpponentBingo().serialize_matrix()
            game_board_2_len = protocol._int_to_bytes(len(game_board_2))

            history_1 = json.dumps(self.bingo.history).encode()
            history_1_len = protocol._int_to_bytes(len(history_1))

            hsitory_2 = json.dumps(self.getOpponentBingo().history).encode()
            history_2_len = protocol._int_to_bytes(len(hsitory_2))

            data = math_id_len + math_id + room_id_len + room_id + uid_1_len + uid_1 + uid_2_len + uid_2 + game_board_1_len + \
                game_board_1 + game_board_2_len + game_board_2 + history_1_len + history_1 + history_2_len + hsitory_2 + win_len + win

            RoomList

            redisClient.zadd('game_history', {data: endTime})
        else:
            History[self.match_id] = endTime


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

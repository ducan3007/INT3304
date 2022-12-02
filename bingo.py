import numpy as np
import random
from colorama import Fore, Back, Style
import protocol
import sys
import json
import json
from json import JSONEncoder


class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


class Bingo:
    def __init__(self, x):

        # Số hàng và cột
        self.x = int(x)
        self.win = False
        # Lưu lịch sử
        self.history = dict()  # {num: (pos_x, pos_y)}

        # Mảng 2 chiều lưu trữ bảng, init = 0
        self.game_board = np.zeros((x, x), dtype=int)  # [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]

        # Lưu các đường nằm ngang, dọc, chéo, khởi tạo bằng 0,
        self.game_info = {
            "row": np.zeros(x),  # [5,0,0,0,0] : có 5 phần tử có vị trị y = 0
            "col": np.zeros(x),
            "cross": np.zeros(2)
        }

        # Số đường thẳng, lines = x thì Win
        self.lines = 0

        # Tạo bảng
        self.board()

        # Random board

    # Khởi tạo bảng

    def board(self):
        nums = [i for i in range(1, self.x**2+1)]
        for i in range(self.x):
            for j in range(self.x):
                ran = random.choice(nums)
                self.game_board[i][j] = ran
                nums.pop(nums.index(ran))

    # Tìm vị trí của số trong bảng

    def pos(self, num):
        for i in range(self.x):
            for j in range(self.x):
                if self.game_board[i][j] == num:
                    return (j, i)

    # Cập nhật game_info sau khi chọn một ô
    def update(self, pos_x, pos_y, num):
        self.history[num] = (pos_x, pos_y)
        self.game_info["row"][pos_x] += 1
        self.game_info["col"][pos_y] += 1
        if (pos_x == pos_y):
            self.game_info["cross"][0] += 1

        if (pos_x + pos_y == self.x - 1):
            self.game_info["cross"][1] += 1

    # Thắng khi có 5 đư24
    # ờng thẳng
    def isWin(self):
        lines = 0
        print(self.x)
        for i in range(self.x):
            if self.game_info["row"][i] == self.x:
                lines += 1
            if self.game_info["col"][i] == self.x:
                lines += 1
            if (i < 2):
                if self.game_info["cross"][i] == self.x:
                    lines += 1

        if lines >= self.x:
            return True

        return False

    def isSelectedNumber(self, number):
        sys.stdout.write(f'{self.history} \n')
        for i in self.history:
            if i == number:
                return True
        return False

    def printBoard(self):
        output = ''
        for i in range(self.x):
            for j in range(self.x):
                if (self.game_board[i][j] in self.history):
                    output += f'\x1b[7;30;41m {self.game_board[i][j]} \x1b[0m'
                else:
                    output += f'\x1b[7;30;42m {self.game_board[i][j]} \x1b[0m'
            output += '\n'
        sys.stdout.write(output)

    def validate(self, num):
        if num.strip().isdigit() is not True:
            return 'INVALID'

        if int(num) in self.history:
            return 'DUPLICATE'

        return int(num)

    '''
        Serialize mảng board thành bytes
        Output:  [ 'int32' + kích thước mảng 5 + len(bytes) + bytes ]
    '''

    def serialize_matrix(self):
        data_type = self.game_board.dtype.name
        shape = self.game_board.shape
        bytes = self.game_board.tobytes()
        print(len(data_type.encode()))
        return data_type.encode() + protocol._int_to_bytes(shape[0]) + protocol._int_to_bytes(len(bytes)) + bytes

    def size(self):
        return self.x**2

    def update_and_print(self, num):
        pos = self.pos(int(num))
        self.update(pos[0], pos[1], int(num))
        self.printBoard()

    def to_json(self):
        return {
            "board": self.serialize_matrix(),
            "history": json.dumps(self.history),
        }


if __name__ == '__main__':

    matrix = input("Nhập kích thước mảng ")

    while matrix.strip().isdigit() is not True:

        matrix = input("Nhập kích thước mảng ")
        print(type(matrix))

    Bingo = Bingo(int(matrix))
    Bingo.board()
    Bingo.printBoard()

    while True:
        _input = input("Nhập số cần đánh dấu ")

        valid = Bingo.validate(_input)

        if (valid == 'INVALID'):
            print('Đầu vào ko hợp lệ')
            continue
        if (valid == 'DUPLICATE'):
            print('Số đã được chọn')
            continue

        a, b = Bingo.pos(valid)

        Bingo.update(a, b, valid)
        # package = Bingo.serialize_matrix()
        # print('Bingo serialize: ', package)

        # data_type = protocol._get_str(package[0:5])
        # shape = protocol._get_ints(package[5:9])
        # len_ = protocol._get_ints(package[9:13])
        # bytes = package[13:13+len_]

        # print(data_type, shape, bytes)

        # print('Bingo deserialize: ', protocol.deserialize_matrix(bytes, data_type, (shape, shape)))
        # print('Bingo game_board: ', Bingo.game_board)

        # in bảng sau mỗi lần nhập
        Bingo.printBoard()
        print('Bingo game_board: ', Bingo.game_info)
        print('lines: ', Bingo.isWin())

        if (Bingo.isWin() is not False):
            break

    print("Win!")

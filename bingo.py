import numpy as np
import random
from colorama import Fore, Back, Style


class Bingo:
    def __init__(self, x):

        # Số hàng và cột
        self.x = int(x)

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

    # Thắng khi có 5 đường thẳng
    def isWin(self):
        lines = 0
        for i in range(self.x):
            if self.game_info["row"][i] == self.x:
                lines += 1
            if self.game_info["col"][i] == self.x:
                lines += 1
            if (i < 2):
                if self.game_info["cross"][i] == self.x:
                    lines += 1

        if lines >= self.x:
            return lines

        return False

    def printBoard(self):
        print("BINGO: ")
        for i in range(self.x):
            for j in range(self.x):
                if (self.game_board[i][j] in self.history):
                    print(Fore.RED + str(self.game_board[i][j]) + Style.RESET_ALL, end=" ")
                else:
                    print(self.game_board[i][j], end=" ")
            print()

    def validate(self, num):
        if num.strip().isdigit() is not True:
            return 'INVALID'

        if int(num) in self.history:
            return 'DUPLICATE'

        return int(num)


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

        # in bảng sau mỗi lần nhập
        Bingo.printBoard()
        print('lines: ', Bingo.isWin())

        if (Bingo.isWin() is not False):
            break

    print("Win!")

```
$ py -m venv .venv

+ An: Logic phần bingo
+ Ánh: Phần giao thúc game (PKT_HELLO, ..)
+ Hoàng: Phần giao thức của Cơ
+ Đăng: Phần giao diện console
```

Render bảng -> Bắt nhập số hàng cột -> Bảng -> Chọn số -> Validate số, lấy vị trí số trong bảng,số bị chọn hiện thị với màu khác -> Render

```Python
class Bingo:
    def __init__(self, x):

        # Số hàng và cột
        self.x = x

        # Lưu lịch sử, dùng để đánh dấu số đã chọn khi Render
        self.history = dict()  # {num: (pos_x, pos_y)}

        # Mảng 2 chiều lưu trữ bảng, init = 0, Dùng để Render
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

    # Khởi tạo bảng [x][x]

    def board(self):
        nums = [i for i in range(1, self.x**2+1)]
        for i in range(self.x):
            for j in range(self.x):
                ran = random.choice(nums)
                self.game_board[i][j] = ran
                nums.pop(nums.index(ran))

    # Tìm vị trí của số trong bảng
    # num: giá trị của số cần lấy vị trí, trả về False nếu ko thấy
     
    def pos(self, num):
        for i in range(self.x):
            for j in range(self.x):
                if self.game_board[i][j] == num:
                    return (j, i)
        return False

    # Cập nhật game_info sau khi chọn một ô
    # Cần gọi hàm `pos(num)` đế lấy tọa độ (pos_x, pos_y) rồi truyền vào
    
    
    def update(self, pos_x, pos_y, num):
        self.history[num] = (pos_x, pos_y)
        self.game_info["row"][pos_x] += 1
        self.game_info["col"][pos_y] += 1
        if (pos_x == pos_y):
            self.game_info["cross"][0] += 1

        if (pos_x + pos_y == self.x - 1):
            self.game_info["cross"][1] += 1

    # Thắng khi ăn được 5 đường thẳng
    def isWin(self):
        for i in range(self.x):
            if self.game_info["row"][i] == self.x:
                self.lines += 1
            if self.game_info["col"][i] == self.x:
                self.lines += 1
            if (i < 2):
                if self.game_info["cross"][i] == self.x:
                    self.lines += 1

        if self.lines >= self.x:
            return True

        return False

    # Hàm để test
    def printBoard(self):
        print(self.game_board)
        num = 14
        a, b = self.pos(num)
        print('x: ', a, 'y: ', b)
        self.update(a, b, num)
        print(self.game_info)
        print(self.history)
        print(self.isWin())


Bingo = Bingo(5)
Bingo.board()
Bingo.printBoard()
```

```
$ py -m venv .venv
$ pip install -r requirements.txt
$ docker compose up -d
```

+ `socket_server.py`: Socket Server, game chính giữa hai người chơi, lưu data và Redis
+ `bingo_client.py`: Client game, BOT kết nối đến socket_server.py.
+ `web/react`: UI của Server game, cho phép theo dõi trận đấu, lịch sử. Kết nối đến websocket.py
+ `websocket.py`: Websocket Server, lấy data từ Redis, gửi đến UI.
+ `server.py`: Socket Server, kết nối đến Game Server 104.194.240.16.
+ `status.py`: Websocket Server, gửi status đến Game Server 104.194.240.16.


Render bảng -> Bắt nhập số hàng cột -> Bảng -> Chọn số -> Validate số, lấy vị trí số trong bảng,số bị chọn hiện thị với màu khác -> Render

### I. Thiết lập 1 match
+ Web server game là `A` (SV cơ)
+ Game server là `S` (Sv của mình)
+ 2 User là `C1`, `C2` (Client của mình, chưa có)

* quá trình có 1 match để 2 client join vào gồm:
### b1. 

`A` phải có thông tin của `S` để `C1`, `C2` yêu cầu tạo 1 match của game nào. 
	`S` sẽ gửi cho `A` (ip, port cung cấp sau) gồm những thông tin  theo thứ tự[

+ action (int 4byte, với cung cấp thông tin của game thì action=1),
+ a (int 4 byte, độ dài của ip game), 
+ ip/domain game(string), 
+ b (int 4byte, thông tin của port), 
+ c (int 4 byte, độ dài tên game), 
+ tên game (string), 
+ d (int, độ dài thông tin game như rule), 
+ rule,
+ e (int 4 byte, độ dài author), 
+ author (string)
]
	`A` nhận thông tin từ `S`: 
+ nếu chấp nhận thì gửi [1(int 4 byte)], 
+ còn không nhận thì [0(int 4 byte), error(thông tin lỗi)]

### b2. 
sau khi `A` có thông tin của 1 game `S`. bước tiếp theo là 2 User cần có 1 match và thông tin của match đó để chơi. 
	`A` sẽ gửi yêu cầu `S` bắt đầu 1 trận đấu với thông tin.[
+ action(int 4byte, tạo match thì action =1),
+ matchId(int 4 byte),
+ uid1(int 4 byte), 
+ uid2(int 4 byte), 
+ x(int 4 byte độ dài của keymatch), 
+ keymatch(string)]

`S` nhận thông tin từ `A`: nếu tạo thành công `S` gửi cho `A`: [
+ 1(int 4 byte)], 
+ nếu không thành công gửi cho `A`[0(int 4 byte), error(string, thông tin lỗi)]

### b3. 
Khi `A` nhận thông tin từ `S` là 1 thì `A` gửi thông tin `ip, port, keymatch cho 2 User`.


### b4. 
User truy cập vào `ip, port` của `S` do `A` cung cấp. 
Sau đó User nhập thông tin `uid` và `keymatch` của mình cho `S` để chơi game.
( Khi nhập uid thì `S` phải phân biệt kết nối nào là của user nào tiện cho việc tính điểm và trả lại kết quả)

// bổ sung: lúc 2 user bắt đầu chơi S gửi cho A [action=3,mathId;status=1]

### b5. 
Sau khi chơi xong `S` gửi lại thông tin cho `A`. [ 
+ action=2(trả thông tin kết quả, kết thúc ván đấu),
+ matchId(int 4byte), 
+ score1(int 4 byte của uid1), 
+ score2(int 4 byte của uid2)] 

### II. Cập nhật thông tin trạng thái 1 match đang chơi.

1. bên `A` gửi gói tin cho `S`  [action(int 4 byte , =3 với việc cập nhật thông tin), matchId(int 4 byte)].

2. `S` phản hồi cho `A`: [
+ action(int 4 byte, =3 ), 
+ status(0,1,2 tương ứng vs chưa bắt đầu, đang diễn ra, kết thúc), 
+ [score1(int4 byte, điểm uid1), 
+ score(int 4 byte, điểm uid2) chỉ cần gửi với status =1 hoặc 2]]




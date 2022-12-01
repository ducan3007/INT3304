```
$ py -m venv .venv

+ An: Logic phần bingo
+ Ánh: Phần giao thúc game (PKT_HELLO, ..)
+ Hoàng: Phần giao thức của Cơ
+ Đăng: Phần giao diện console
```

Render bảng -> Bắt nhập số hàng cột -> Bảng -> Chọn số -> Validate số, lấy vị trí số trong bảng,số bị chọn hiện thị với màu khác -> Render
 [ 
+ Web server game là A (SV cơ),
+ Game server là S (Sv của mình), 
+ 2 User là C1, C2]

### I. Phía Frontend
* quá trình tạo 1 match để 2 client join vào gồm:
### b1. Gửi thông tin GAME cho bên web

`S` sẽ gửi thông tin game cho `A` bao gồm 4 trường theo thứ tự sao[
![image](https://user-images.githubusercontent.com/91183884/205115739-c00ea714-9069-4aa5-8797-66276fb26203.png)
+ Tên game: (không được trùng với tên game người khác đã đăng ký),
+ IP: ip để bên web xác minh và gửi nhận thông tin với game server(nếu làm server bằng websocket thì gửi ip theo dạng ws://ip để phân biệt được là socket thuần hay
websocket), 
+ Port: port của game server để bên web kết nối, 
+ Rule: có thể là file ảnh hay text để người chơi có thể hiểu rõ cách chơi game
![image](https://user-images.githubusercontent.com/91183884/205116009-198840c4-e13d-4d38-b099-db376230156d.png)

### b2. Tạo 1 Match

Sau khi có thông tin của 1 game, bước tiếp theo sẽ tạo 1 Match với các thông tin sau(chỉ những game status = On mới tạo được ván đấu).
![image](https://user-images.githubusercontent.com/91183884/205118668-e66985db-a1cd-490f-a7b5-a65ab5690e52.png)
 Chọn Create Game
 
 ![image](https://user-images.githubusercontent.com/91183884/205118948-d4d4e2a0-a942-4ea8-a209-447097d6e9d4.png)
+ ID1,ID2: là 2 ID của 2 người chơi, bắt buộc phải nhập đúng và ID1 không trùng ID2
+ Pasword:là mật khẩu thống nhất để người chơi nhập vào Server Game

### II. Phía socket

1. Sau khi tạo 1 trận đấu thành công, bên `A` sẽ gửi tới địa chỉ IP, Port của game đã đăng kí cho `S` theo format
![image](https://user-images.githubusercontent.com/91183884/205120943-d6c275d9-c4c5-44b1-a219-9493f8847a2e.png)

2. Nếu thành công, `S` phản hồi cho `A`:[
{"result": 1, "ip": "localhost", "port": 27003, "path": "path"}
+ result = 1 là thành công, 
+ ip,port: ip này là thông tin match đã tạo,
+ path: đối với game web thì cần thêm thông tin path để tạo thành url, ]

3. Nếu thất bại thì `S` sẽ gửi cho `A` result = 0.

### III. Cập nhập thông tin trận đấu
1. sau khi 2 người chơi đã vào ván và đấu bắt đầu chơi game thì `S` sẽ gửi cho `A`: [
+ result = 1,
+ match: giá trị mà `A` gửi cho `S`]

2. sau khi 2 người chơi đã chơi xong và kết thúc ván đấu, `S` sẽ gửi cho `A`: [
+ result = 3, 
+ match]

3.`A` sẽ gửi cho `S` yêu cầu thông tin ván đấu:[
+ result = 2,
+ match]

4. Thông tin mà `S` sẽ gửi cho `A` bao gồm:[
+ result = 2,
+ match,
+ status: trạng thái ván đấu, với 0 là chưa bắt đầu, 1 đang diễn ra, 3 là đã kết thúc,
+ id1: điểm của id1,
+ id2: điểm của id2,
(VD: {"result": 2, "match": 10, "status": 1, "id1": 5, "id2": 7})]

5. Nếu như gặp phải bất kì lỗi gì thì `S` sẽ gửi cho `A`:[
+ result = 0,
+ match]

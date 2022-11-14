import threading
import socket
from time import sleep
# from render import Render
from random import randint
from bingo import Bingo
from enum import Enum
from struct import *


hostname = socket.gethostname()

HOST = 'localhost'
PORT = 27003
KEY = 'flag{1234567890}'


class PKT(Enum):
    HELLO = 0
    PLAY = 4
    UPDATE = 5
    CREATEMAP = 2
    NOTICE = 3
    RESULT = 6
    START = 1
    END = 7


# Để ý hai cái này
Clients = dict()

Bingos = dict()

'''
Flows: CÓ THỂ KHÔNG ĐÚNG, phải làm mới biết dc. 

Làm sao để client1 biết là đến lượt chọn của mình, khi mà client2 đã chọn xong nước đi ? => Lưu lại socket của tất cả client.

+ Đầu tiên ta cần mã phòng (zoom_id) cho 2 Client, mã có thể auto tạo ở phía Server, hoặc một trong hai Client yêu cầu tạo mã phòng để lấy mã.

+ Mã phòng sẽ lưu vào dict Clients ở trên: với key là mã phòng, value là mảng [(uuid1, socket_client1), (uuid2, socket_client2)]. Dựa vào uuid để xác định Client nào.

+ Tại sao cần mã phòng và lưu vào Clients trên?
 
=> Để broadcast, ví dụ client2 gửi gói update game, lúc này nếu ko lưu lại socket của client1 thì chỉ có socket_client2 nhận được update. 
Vì socket_clinet1 ở một Thread khác. ( CODE tham khảo boardcast ở trong ./sample/chat_broadcast )

+ Server sẽ dựa vào mã phòng để gửi thông tin mới update cho tất cả người chơi dùng trong phòng đó.

Ví dụ:

# khởi tạo
Clients[zoom_id] = [(uuid1, client1), (uuid2, client2)]
Bingos[zoom_id] = (),  # Lưu trạng thái chung của bàn chơi, tránh cheat, có lưu lại 'next_turn', để xác định tiếp theo ai được đi. 
    
# Khi client2 chọn một số, thì :
    
    #boardcast thông tin mới nhất
    for uuid, socket_client in Clients[zoom_id]:
        socket_client.send(next_turn)
            
            // next_turn là gói tin CÓ THỂ bao gồm: 
            + turn: uuid của người chơi có lượt tiếp theo (hoặc là gì cx được, nói chung là biết ai vừa đi)
            + giá trị nước đi đó: để client còn lại cập nhật (Theo luật thì nếu client2 chọn '5' mà client1 chưa chọn '5' thì client1 sẽ ăn số '5' ấy )


+ Các package còn lại làm như bình thường


'''


class ClientThread(threading.Thread):
    def __init__(self, conn, address: str):
        threading.Thread.__init__(self)
        self.conn = conn
        self.address = address
        self.bingo = Bingo(5)

        # uuid của Clien tại thread này
        self.uuid = ''

        # self.render = Render(self.bingo)

        # num = int(input("Nhập kích thước mảng"))
        try:
            while True:
                self.data = conn.recv(1024)

                # 1. nhận gói tạo tham gia game với zoom_id

                # kiểm tra xem có ai trong zoom chưa để start game

                # Néu zoom đủ người thì bắt đầu game, gửi gói boardcast start_game đến tất cả client trong zoom

                # 2.  nhận ma trận từ client, lưu lại vào dict Bingos. dict Bingos sẽ lưu lại đối tượng Bingo của từng Client

                # 3. Đầu tiên boardcast, mặc định cho Client1 đi trước.

                ''' 4.
                Nhận gói tin chọn số từ Client1, Validate nó, 
                
                Cập nhật Bingo của Client1, cập nhật next_turns,
                
                Boardcast thông tin đến tất cả Client trong zoom
                '''
                pass

            self.conn.close()
            print(f'Connection to {address} closed')

        except Exception as e:
            print(e)
            self.conn.close()

    def decode_message(package):
        pass


class Server:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        print(f'Listening on {HOST}:{PORT}')
        self.server.listen()

    def start_server(self):
        conn, address = self.server.accept()
        threading.Thread(target=ClientThread, args=(conn, address[1])).start()


if __name__ == '__main__':
    server = Server()
    while True:
        server.start_server()

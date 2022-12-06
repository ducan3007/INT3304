import asyncio
import websockets
import struct
import json

# cập nhập trạng thái
data1 = {
    "result": 2,
    "match": 63, # id của match
    "status": 2, # trạng thái match
    "id1": 100,
    "id2": 100
}

# thông báo bắt đầu
data2 = {
    "result": 1,
    "match": 63, # id của match
}

# thông báo kết thúc
data3 = {
    "result": 3,
    "match": 63, # id của match
}

# thông báo lỗi
data4 = {
    "result": 0,
    "match": 63, # id của match
}

async def hello():
    async with websockets.connect("ws://104.194.240.16/ws/channels/") as websocket:
        await websocket.send(json.dumps(data1))
        msg = await websocket.recv()
        print(msg)
asyncio.run(hello())


import asyncio
import websockets
import struct
import json

# cập nhập trạng thái
update = {
    "result": 2,
    "match": 65,  # id của match
    "status": 2,  # trạng thái match
    "id1": 0,
    "id2": 100
}

# thông báo bắt đầu
start = {
    "result": 1,
    "match": 65,  # id của match
}

# thông báo kết thúc
end = {
    "result": 3,
    "match": 65,  # id của match
}

# thông báo lỗi
error = {
    "result": 0,
    "match": 64,  # id của match
}


async def hello():
    async with websockets.connect("ws://104.194.240.16/ws/channels/") as websocket:
        await websocket.send(json.dumps(end))
        msg = await websocket.recv()
        print(msg)
asyncio.run(hello())

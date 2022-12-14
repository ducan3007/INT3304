import asyncio
import websockets
import struct
import json
import redis
from time import sleep

redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")

# cập nhập trạng thái
update = {
    "result": 2,
    "match": 387,  # id của match
    "status": 2,  # trạng thái match
    "id1": 1,
    "id2": 100
}

# thông báo bắt đầu
start = {
    "result": 1,
    "match": 381,  # id của match
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


def update(id1, id2, matchid, status, result=2):
    return {
        "result": result,
        "match": matchid,
        "status": status,
        "id1": id1,
        "id2": id2
    }


async def hello():
    async with websockets.connect("ws://104.194.240.16/ws/channels/") as websocket:
        while True:
            sleep(1)

            keys = redisClient.keys('game_server:*')

            for key in keys:
                a = redisClient.get(key.decode()).decode().split(':')
                print(a)
                await websocket.send(json.dumps(update(a[0], a[1], a[2], a[3])))
                msg = await websocket.recv()

                print(msg)


asyncio.run(hello())

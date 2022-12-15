import asyncio
import websockets
import struct
import json
import redis
import random
from time import sleep

redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")

# cập nhập trạng thái
update_package = {
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


def update_package(id1, id2, matchid, status, result=2):
    return {
        "result": result,
        "match": matchid,
        "status": status,
        "id1": id1,
        "id2": id2
    }


async def hello():
    point_1 = 10
    point_2 = 10

    async with websockets.connect("ws://104.194.240.16/ws/channels/") as websocket:
        while True:
            sleep(1)

            keys = redisClient.keys('game_server:*')
            point_2 += random.randint(1, 7)
            point_1 += random.randint(1, 7)

            print(point_1, point_2)

            for key in keys:
                a = redisClient.get(key.decode()).decode().split(':')
                print(a)

                if (a[3] == '2'):
                    redisClient.delete(f'game_server:{a[2]}')

                await websocket.send(json.dumps(update_package(point_1, point_2, a[2], a[3])))
                msg = await websocket.recv()
                print(msg)


asyncio.run(hello())

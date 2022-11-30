
import socket_server as socketServer
import os
import sys
import json
import websockets
import asyncio
import time
import protocol
from datetime import datetime
import redis


redisClient = redis.Redis(host='localhost', port=6379, db=0, password="admin")

t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)


def log(*args, **kwargs):
    print(f'{datetime.now().strftime("%H:%M:%S")} :', *args, **kwargs)


async def main(ws, path):
    # ping pong

    while True:
        recv = await ws.recv()
        print('recv: ', recv)
        message = json.loads(recv)

        if message['msg'] == 'ping':
            log('ping')
            game_state = json.loads(redisClient.get('game_state').decode())
            game_history = protocol.redis_get_history(redisClient.zrange(
                "game_history", 0, -1, desc=True, withscores=True))
            data = json.dumps({'msg': 'get', 'game_state': game_state, 'game_history': game_history})
            await ws.send(data)

        if message['msg'] == 'detail':
            pass
            # room_id = message['room_id']
            # game_state = json.loads(redisClient.get('game_state').decode())
            # print(game_state)
            # for i in game_state:
            #     if i['room_id'] == room_id:
            #         data = json.dumps({'msg': 'detail', 'game_state': i})
            #         await ws.send(data)
            #         break


if __name__ == '__main__':
    start_server = websockets.serve(main, "localhost", 8081)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

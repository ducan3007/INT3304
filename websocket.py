
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
            room_id = message.get('room_id')
            data = redisClient.get('game_state')

            if room_id is None:
                await ws.send(json.dumps({'msg': 'error', 'error': 'room_id is None'}))
                continue

            if data is not None:
                game_state = json.loads(data.decode())
                print('game_state: ', game_state)

                res = []
                players = []

                for i in game_state:
                    if i == room_id:
                        players = game_state[room_id]['players']
                        break

                print(players)

                id_player_1 = players[0] if len(players) > 0 else ''
                id_player_2 = players[1] if len(players) > 1 else ''

                player_1 = redisClient.get('game_board:' + id_player_1)
                player_2 = redisClient.get('game_board:' + id_player_2)

                player_1_history = redisClient.get('history:' + id_player_1)
                player_2_history = redisClient.get('history:' + id_player_2)

                if player_1_history is not None:
                    player_1_history = json.loads(player_1_history.decode())

                if player_2_history is not None:
                    player_2_history = json.loads(player_2_history.decode())

                if player_1 is not None:
                    res.append({'uid': id_player_1, 'board': protocol.deserialize_matrix(
                        player_1)[1].tolist(), 'history': player_1_history or {}})
                else:
                    res.append({'uid': id_player_1, 'board': [], 'history': player_1_history or {}})

                if player_2 is not None:
                    res.append({'uid': id_player_2, 'board': protocol.deserialize_matrix(
                        player_2)[1].tolist(), 'history': player_2_history or {}})
                else:
                    res.append({'uid': id_player_2, 'board': [], 'history': player_2_history or {}})

                data = json.dumps(
                    {'msg': 'get', 'res': res, 'next_move': game_state[room_id]['next_move'],
                     'winner': game_state[room_id].get('winner')})
                await ws.send(data)


if __name__ == '__main__':
    start_server = websockets.serve(main, "localhost", 8081)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

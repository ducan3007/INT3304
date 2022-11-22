import numpy as np


def _select_number(number):
    return int.to_bytes(203, 4, 'little') + _int_to_bytes(number)


def _get_ints(data):
    return int.from_bytes(data, 'little')


def _get_str(data):
    return data.decode()


def game_draw():
    return int.to_bytes(888, 4, 'little')


def _int_to_bytes(num):
    return int.to_bytes(num, 4, 'little')


def _get_type(data):
    if (len(data) >= 4):
        type = int.from_bytes(data[:4], 'little')
        print(type, 'type')
        return type


def _server_boardcast(data):
    type = int.to_bytes(100, 4, 'little')
    _len = int.to_bytes(len(data), 4, 'little')
    return type + _len + data

# Package get board Data


# tạo match và gửi cho người chơi
def _server_match_making(data):
    return int.to_bytes(201, 4, 'little') + data


def server_error():
    return int.to_bytes(500, 4, 'little')


def accept_connection(uuid):
    type = int.to_bytes(200, 4, 'little')
    message = f'Connection accepted, your UUID is {uuid}'.encode()
    _len = int.to_bytes(len(message), 4, 'little')
    return type + _len + message


def deserialize_matrix(package):
    data_type = _get_str(package[0:5])
    shape = _get_ints(package[5:9])
    len_ = _get_ints(package[9:13])
    bytes = package[13:13+len_]

    return (shape, np.frombuffer(bytes, dtype=data_type).reshape((shape, shape)))


def you_won():
    return int.to_bytes(999, 4, 'little')


def you_lost():
    return int.to_bytes(777, 4, 'little')


def send_result(matrix, history):
    return int.to_bytes(222, 4, 'little') + matrix + _int_to_bytes(len(history)) + history


def you_lose():
    return int.to_bytes(777, 4, 'little')


def can_move():
    return int.to_bytes(202, 4, 'little')


def cant_move():
    return int.to_bytes(401, 4, 'little')


def get_next_move():
    return int.to_bytes(204, 4, 'little')


def invalid_move():
    return int.to_bytes(402, 4, 'little')


def update_board(number):
    return int.to_bytes(205, 4, 'little') + _int_to_bytes(number)

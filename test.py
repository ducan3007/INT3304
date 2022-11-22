import numpy as np
from bingo import Bingo


if __name__ == '__main__':
    a = dict()

    a['room1'] = dict()
    a['room1']['player1'] = 'Bingo 1'
    a['room1']['player2'] = 'Bingo 2'

    del a['room1']['player1']
    print(a)

import numpy as np
from socket_server import Server


def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30, 38):
            s1 = ''
            for bg in range(40, 48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print(f'! {s1}', s1)
        print('\n')


# print_format_table()

if __name__ == '__main__':
    server = Server()
    while True:
        server.start_server()


# Compare threading.Thread vs

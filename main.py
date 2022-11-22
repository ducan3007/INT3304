import numpy as np
import sys

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


if __name__ == '__main__':

    print_format_table()
    sys.stdout.write(f'\x1b[6;37;42m 1 \x1b[0m')
    sys.stdout.write('\x1b[4;37;41m 1 \x1b[0m')

# Compare threading.Thread vs

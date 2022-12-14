import json
import socket
msg = {"result": 1, "ip": "0.tcp.ap.ngrok.io", "port": 18920, "path": "path"}


def server_program():
    host = 'localhost'
    port = 27018

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))
    while True:
        try:
            data = conn.recv(1024).decode()

            print("form connected user: " + str(data))
            conn.send(json.dumps(msg).encode())

        except Exception as e:
            print(e)
            # break

    # conn.close()  # close the connection


if __name__ == '__main__':
    server_program()

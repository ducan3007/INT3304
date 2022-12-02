import json
import socket
msg = {"result": 1, "ip": "localhost", "port": 10010, "path": "path"}

def server_program():
    # get the hostname
    host = 'localhost'
    # initiate port no above 1024
    port = 8881

    server_socket = socket.socket() # get instance
    # look closely, the bind() function takes tuple as argument
    server_socket.bind((host, port)) # bind host address and port together

    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    conn, address = server_socket.accept() # accept new connection
    print("Connection from: " + str(address))
    while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        data = conn.recv(1024).decode()
        if not data:
            # if data is not received break
            break
        print("form connected user: " + str(data))
        # data = input(' -> ')
        conn.send(json.dumps(msg).encode()) # send data to the client

    conn.close() # close the connection

if __name__ == '__main__':
    server_program()

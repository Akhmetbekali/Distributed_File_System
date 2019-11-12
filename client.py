import pickle
import socket
import os, os.path
import sys


def client_program():
    host = socket.gethostname()
    port = 8080
    client_socket = socket.socket()
    # client_socket.connect(('18.224.137.125', port)) IP - aws Instance IP; Open TCP in Security Groups
    client_socket.connect((host, port))
    message = input(" -> ")

    while message.lower().strip() != 'exit':
        client_socket.send(pickle.dumps(message))
        data = pickle.loads(client_socket.recv(1024))
        if type(data) == list:
            print('Received from server: ' + ', '.join(data))
        elif type(data) == os.stat_result:
            print('Received from server: ')
            print(data)
        else:
            print('Received from server: ' + data)

        message = input(" -> ")

    client_socket.close()


def download(client_socket, filename):
    pickle.loads(client_socket.recv(1024))
    client_socket.send(filename.encode())

    f = open(str(sys.argv[1]), 'rb')

    size = os.path.getsize(sys.argv[1])
    bytes_transported = 1024
    byte = f.read(1024)
    print(client_socket.recv(1024).decode())

    while byte:
        percent = bytes_transported * 100 // size
        if percent%10 == 0:
            print(f'{percent}%')
        bytes_transported += 1024
        client_socket.send(byte)
        byte = f.read(1024)

    f.close()

if __name__ == '__main__':
    client_program()

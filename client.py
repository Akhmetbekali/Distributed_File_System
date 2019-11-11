import pickle
import socket
import os


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
        print (type(data))
        if type(data) == list:
            print('Received from server: ' + ', '.join(data))
        elif type(data) == os.stat_result:
            print('Received from server: ')
            print(data)
        else:
            print('Received from server: ' + data)

        message = input(" -> ")

    client_socket.close()


if __name__ == '__main__':
    client_program()

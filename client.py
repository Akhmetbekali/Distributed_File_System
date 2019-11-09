
import socket


def client_program():
    host = socket.gethostname()
    port = 8000

    client_socket = socket.socket()
    # client_socket.connect(('18.224.137.125', port)) IP - aws Instance IP; Open TCP in Security Groups
    client_socket.connect((host, port))
    message = input(" -> ")

    while message.lower().strip() != 'bye':
        client_socket.send(message.encode())
        data = client_socket.recv(1024).decode()

        print('Received from server: ' + data)

        message = input(" -> ")

    client_socket.close()


if __name__ == '__main__':
    client_program()

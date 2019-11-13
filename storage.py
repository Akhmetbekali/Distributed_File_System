import logging
import sys

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
import socket
import pickle
import os


def client_storage():
    authorizer = DummyAuthorizer()

    homedir = "/home/ali/PycharmProjects/DS_project/"
    authorizer.add_user("user", "12345", homedir, perm="elradfmw")  # ROOT
    authorizer.add_anonymous(homedir, perm="elradfmw")
    handler = FTPHandler  # line 1925
    handler.authorizer = authorizer
    server = FTPServer

    logging.basicConfig(filename='/home/ali/PycharmProjects/DS_project/test.txt', level=logging.INFO)

    server.max_cons_per_ip = 1
    server = FTPServer(('', 8000), handler)
    server.serve_forever()


def storage_is_server():
    host = socket.gethostname()
    port = 8080

    server_socket = socket.socket()
    server_socket.bind(('', port))

    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    data = pickle.loads(conn.recv(1024))
    if not data:
        conn.close()
    if data == 'Initialize':
        msg = "Clear"
        conn.send(pickle.dumps(msg))
    if data == 'Upload' or 'Download':
        msg = "Ready to" + data
        conn.send(pickle.dumps(msg))
        client_storage()
    else:
        msg = "error"
        conn.send(pickle.dumps(msg))
    conn.close()


if __name__ == '__main__':
    # storage_is_server()
    client_storage()

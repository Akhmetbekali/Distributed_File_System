import logging
import sys
from threading import Thread

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.servers import ThreadedFTPServer
from ftplib import FTP
import socket
import pickle
import os

ip1 = ""
ip2 = ""


class MyFTPHandler(FTPHandler):
    def on_file_received(self, file):
        if os.path.basename(file) == 'last_file':
            self.server.close_when_done()
            rep1 = Thread(target=start_replication, args=(file, ip1))
            rep2 = Thread(target=start_replication, args=(file, ip2))
            rep1.start()
            rep2.start()
            rep1.join()
            rep2.join()


def client_storage(path):
    authorizer = DummyAuthorizer()

    homedir = "/home/ali/PycharmProjects/DS_project/"
    authorizer.add_user("user", "12345", homedir, perm="elradfmw")  # ROOT
    authorizer.add_anonymous(homedir, perm="elradfmw")
    handler = MyFTPHandler  # line 1925
    handler.authorizer = authorizer
    server = ThreadedFTPServer

    logging.basicConfig(filename='/home/ali/PycharmProjects/DS_project/test.txt', level=logging.INFO)

    server.max_cons_per_ip = 1
    server = ThreadedFTPServer(('', 8000), handler)

    server.serve_forever()
    server = FTPServer(('', 8000), handler)
    current_path = FTP().pwd()
    if current_path == path:
        server.serve_forever()
    else:
        print("current: ", current_path)
        print("path: ", path)


def start_replication(file, ip):
    ftp = FTP()
    host = ip
    # host = socket.gethostname()
    port = 8000
    ftp.connect(host, port)
    ftp.login()
    uploadfile(ftp, file)
    return


def uploadfile(ftp, file):  # Откуда запускаешь, оттуда и скачивает

    filename = file
    ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
    ftp.close()


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
    elif data == "Download" or "Upload":
        msg = "Ready to " + data
        conn.send(pickle.dumps(msg))
        cl_s = Thread(target=client_storage)
        repl = Thread(target=start_replication)

        cl_s.start()
        repl.start()

        cl_s.join()
        repl.join()
        path = pickle.loads(conn.recv(1024))
        client_storage(path)
    # elif data == "Upload":
    #     msg = "Ready to " + data
    #     conn.send(pickle.dumps(msg))
    #     path = pickle.loads(conn.recv(1024))
    #     client_storage(path)
    else:
        msg = "error"
        conn.send(pickle.dumps(msg))
    conn.close()


if __name__ == '__main__':
    storage_is_server()
    # client_storage()

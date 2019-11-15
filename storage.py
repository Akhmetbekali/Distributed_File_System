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
import time

# ds1_ip = "192.168.1.57"
ns_ip = "18.221.170.198"
client_ip = "192.168.1.52"
ds1_ip = "3.15.172.241"
ftp_port = 20
ns_client_port = 8081
ns_ds_port = 8080
ds_ds_tcp_port = 8082


class MyFTPHandler(FTPHandler):
    def on_file_received(self, file):
        print("File received")
        
        print(file)
        
        self.server.close_when_done()
        # rep1 = Thread(target=start_replication, args=(file, ds2_ip))
        # # rep2 = Thread(target=start_replication, args=(file, ds3_ip))
        # rep1.start()
        # # rep2.start()
        # rep1.join()
        # rep2.join()
        
    
class NoRepFTPHandler(FTPHandler):
    def on_file_received(self, file):
        self.server.close_when_done()
        
    
def start_ftp_server(handler):
    authorizer = DummyAuthorizer()

    homedir = os.path.abspath("./Storage")
    if not os.path.isdir(homedir):
        os.mkdir(homedir)
    if not os.path.isfile("{}/test.txt".format(homedir)):
        f = open('{}/test.txt'.format(homedir), 'tw', encoding='utf-8')
        f.close()
    authorizer.add_user("user", "12345", homedir, perm="elradfmw")  # ROOT
    authorizer.add_anonymous(homedir, perm="elradfmw")
    handler.authorizer = authorizer

    logging.basicConfig(filename='{}/test.txt'.format(homedir), level=logging.INFO)
    
    server = ThreadedFTPServer(('', ftp_port), handler)

    server.max_cons_per_ip = 5
    server.serve_forever()

#
# def client_storage(path):
#     handler = MyFTPHandler(FTPHandler)
#     start_ftp_server(handler)


def start_replication(file, ip):
    print("Start replication " + ip)
    conn = socket.socket()
    conn.connect((ip, ds_ds_tcp_port))
    msg = "Replication"
    conn.send(pickle.dumps(msg))
    time.sleep(3)
    ftp = FTP()
    host = ip
    port = ftp_port
    ftp.connect(host, port)
    ftp.login()
    uploadfile(ftp, file)
    return


def uploadfile(ftp, file):  # Откуда запускаешь, оттуда и скачивает
    print("Upload file" + file)
    filename = file
    ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
    ftp.close()


def storage_is_server():
    host = ds1_ip
    port = ns_ds_port

    server_socket = socket.socket()
    server_socket.bind(('', port))
    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    data = pickle.loads(conn.recv(1024))

    if not data:
        conn.close()
    if data == 'Initialize':
        handler = MyFTPHandler
        start = Thread(target=start_ftp_server, args=(handler,))
        start.start()
        # start.join()
        msg = "Server started"
        conn.send(pickle.dumps(msg))
    # if data == 'Connect':



    elif data == "Replication":
        handler = NoRepFTPHandler
        start_ftp_server(handler)
        msg = "Ready to replication"
        conn.send(pickle.dumps(msg))
    elif data == "Download" or "Upload":
        msg = "Ready to " + data
        conn.send(pickle.dumps(msg))
        path = pickle.loads(conn.recv(1024))

        handler = MyFTPHandler
        start_ftp_server(handler)
    else:
        msg = "error"
        conn.send(pickle.dumps(msg))
    conn.close()


if __name__ == '__main__':
    storage_is_server()

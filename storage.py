import hashlib
import logging
from threading import Thread

from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from ftplib import FTP
import socket
import pickle
import os
import constants        # if highlighted - still don't care, it works

ds1_ip = constants.ds1_ip
ds2_ip = constants.ds2_ip
ds3_ip = constants.ds3_ip
ns_ip = constants.ns_ip
client_ip = constants.client_ip
ftp_port = constants.ftp_port
ns_client_port = constants.ns_client_port
ns_ds_port = constants.ns_ds_port
ds_ds_tcp_port = constants.ds_ds_tcp_port


class MyFTPHandler(FTPHandler):
    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_file_sent(self, file):
        # do something when a file has been sent
        print("File sent {}".format(file))

    def on_disconnect(self):
        print("%s:%s disconnected" % (self.remote_ip, self.remote_port))

    def on_login(self, username):
        print("Login {}".format(username))

    def on_file_received(self, file):
        print("File received {}".format(file))
        print(os.stat(file))
        self.server.close_when_done()
        # file = hashlib.sha256(file.encode()).hexdigest()
        rep1 = Thread(target=start_replication, args=(file, ds2_ip))
        rep2 = Thread(target=start_replication, args=(file, ds3_ip))
        rep1.start()
        rep2.start()
        rep1.join()
        rep2.join()
        print(os.stat(file))
        return os.stat(file)
        
    
class NoRepFTPHandler(FTPHandler):
    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_file_sent(self, file):
        # do something when a file has been sent
        print("File sent {}".format(file))

    def on_disconnect(self):
        print("%s:%s disconnected" % (self.remote_ip, self.remote_port))

    def on_login(self, username):
        print("Login {}".format(username))

    def on_file_received(self, file):
        print("File replicated {}".format(file))
        self.server.close_when_done()

    
def start_ftp_server(handler):
    homedir = os.path.abspath("./Storage")
    if not os.path.isdir(homedir):
        os.mkdir(homedir)
    if not os.path.isfile("{}/test.txt".format(homedir)):
        f = open('{}/test.txt'.format(homedir), 'tw', encoding='utf-8')
        f.close()

    authorizer = DummyAuthorizer()
    authorizer.add_user('user', '12345', homedir=homedir, perm='elradfmwMT')
    handler.authorizer = authorizer
    logging.basicConfig(filename='{}/test.txt'.format(homedir), level=logging.INFO)
    
    server = ThreadedFTPServer(('', ftp_port), handler)

    server.max_cons_per_ip = 5
    server.serve_forever()


def start_replication(file, ip):
    ftp = FTP()
    host = ip
    port = ftp_port
    ftp.connect(host, port)
    ftp.login(user='user', passwd='12345')
    uploadfile(ftp, file)
    return


def uploadfile(ftp, file):  # Откуда запускаешь, оттуда и скачивает
    print("Upload file " + file)
    filename = file.split('/')[-1]

    ftp.storbinary('STOR ' + filename, open("Storage/{}".format(filename), 'rb'))
    ftp.close()


def start_storage(msg, ip, port):
    client_socket = socket.socket()
    client_socket.connect((ip, port))
    client_socket.send(pickle.dumps(msg))
    data = pickle.loads(client_socket.recv(1024))
    if data == "Server started":
        return data
    else:
        return "Error"


def storage_is_server(port):
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
        start_ds2 = Thread(target=start_storage, args=("Replication", ds2_ip, ds_ds_tcp_port))
        start_ds2.start()
        start_ds3 = Thread(target=start_storage, args=("Replication", ds3_ip, ds_ds_tcp_port))
        start_ds3.start()
        start = Thread(target=start_ftp_server, args=(handler,))
        start.start()
        print("Server started")
        msg = "Server started"
        print("Line142", handler)
        conn.send(pickle.dumps(msg))
    elif data == "Replication":
        handler = NoRepFTPHandler
        start = Thread(target=start_ftp_server, args=(handler,))
        start.start()
        msg = "Server started"
        conn.send(pickle.dumps(msg))
    elif data == "Upload":
        print("Line 150")
        msg = "Ready to " + data
        conn.send(pickle.dumps(msg))
        handler = MyFTPHandler
        start_ftp_server(handler)
        pickle.loads(conn.recv(1024))
        conn.send(pickle.dumps(handler))

    else:
        msg = "error"
        conn.send(pickle.dumps(msg))
    conn.close()


if __name__ == '__main__':
    ns_ds = Thread(target=storage_is_server, args=(ns_ds_port,))
    ds_ds = Thread(target=storage_is_server, args=(ds_ds_tcp_port,))
    ns_ds.start()
    ds_ds.start()
    ns_ds.join()
    ds_ds.join()

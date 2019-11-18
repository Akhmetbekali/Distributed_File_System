import hashlib
import logging
import shutil
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
ds_ns_port = constants.ds_ns_port


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

        self.server.close_when_done()
        # file_info(file)
        # file = hashlib.sha256(file.encode()).hexdigest()
        rep1 = Thread(target=start_replication, args=(file, ds2_ip))
        rep2 = Thread(target=start_replication, args=(file, ds3_ip))
        rep3 = Thread(target=file_info_met, args=(file, ns_ip))
        print("Trying by thread")
        rep3.start()
        rep1.start()
        rep2.start()
        rep3.join()
        rep1.join()
        rep2.join()
        
    
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


def file_info_met(file, ip):
    print("Creating connection DS -> NS")
    ds_ns = socket.socket()
    ds_ns.connect((ip, ds_ns_port))
    message = os.stat(file)
    ds_ns.send(pickle.dumps(message))
    ds_ns.close()


def start_ftp_server(handler):
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


def uploadfile(ftp, file):
    print("Upload file " + file)
    filename = file.split('/')[-1]

    ftp.storbinary('STOR ' + filename, open("Storage/{}".format(filename), 'rb'))
    ftp.close()


def create_file(file):
    # TODO: create file and return hash + file info
    path = homedir + "/" + file
    try:
        open(path, 'x')
        print("Succesfully created")
        file_info = os.stat(path)
        return file_info
    except FileExistsError:
        msg = "Already exists"
        return msg


def copy_file(source, destination):
    # TODO: make a copy of file and return hash + file info
    source_path = homedir + "/" + source
    destination_path = homedir + "/" + destination
    try:
        shutil.copy(source_path, destination_path)
        print("File copied successfully.")
        file_info = os.stat(destination)
        return file_info
    except shutil.SameFileError:
        print("Source and destination represents the same file.")

    except IsADirectoryError:
        print("Destination is a directory.")

    except PermissionError:
        print("Permission denied.")

    except:
        print("Error occurred while copying file.")


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
    while True:
        server_socket.listen(2)
        conn, address = server_socket.accept()
        print("Connection from: " + str(address))

        data = pickle.loads(conn.recv(1024))

        if not data:
            conn.close()
        if data == 'Initialize':
            handler = MyFTPHandler
            clear_ds2 = Thread(target=start_storage, args=("Replication", ds2_ip, ds_ds_tcp_port))
            clear_ds2.start()
            clear_ds3 = Thread(target=start_storage, args=("Replication", ds3_ip, ds_ds_tcp_port))
            clear_ds3.start()
            start = Thread(target=start_ftp_server, args=(handler,))
            start.start()
            print("Server started")
            msg = "Server started"
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
        elif data == "Create file":
            conn.send(pickle.dumps("Ready"))
            path = pickle.loads(conn.recv(1024))
            file_info = create_file(path)
            conn.send(pickle.dumps(file_info))
        elif data == "Copy file":
            conn.send(pickle.dumps("Ready"))
            path = pickle.loads(conn.recv(1024))
            source = path.split(" ")[0]
            destination = path.split(" ")[1]
            file_info = copy_file(source, destination)
            conn.send(pickle.dumps(file_info))
        elif data == "Clear":
            os.system("sudo rm -r Storage/* -f")
            clear_ds2 = Thread(target=start_storage, args=("Clear2", ds2_ip, ds_ds_tcp_port))
            clear_ds2.start()
            clear_ds3 = Thread(target=start_storage, args=("Clear2", ds3_ip, ds_ds_tcp_port))
            clear_ds3.start()
        elif data == "Clear2":
            os.system("sudo rm -r Storage/* -f")
        else:
            msg = "error"
            conn.send(pickle.dumps(msg))
        conn.close()


if __name__ == '__main__':
    homedir = os.path.abspath("./Storage")
    ns_ds = Thread(target=storage_is_server, args=(ns_ds_port,))
    ds_ds = Thread(target=storage_is_server, args=(ds_ds_tcp_port,))
    ns_ds.start()
    ds_ds.start()
    ns_ds.join()
    ds_ds.join()

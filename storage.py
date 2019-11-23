import hashlib
import logging
import shutil
import time
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
ds = [ds1_ip, ds2_ip, ds3_ip]
ns_ip = constants.ns_ip
client_ip = constants.client_ip
ftp_port = constants.ftp_port
ns_client_port = constants.ns_client_port
ns_ds_port = constants.ns_ds_port
ds_ds_tcp_port = constants.ds_ds_tcp_port
ds_ns_port = constants.ds_ns_port

homedir = os.path.abspath("./Storage")


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
        if self.remote_ip not in ds:
            for ip in ds:
                if ip != get_my_ip():
                    print("Replica to " + ip)
                    new_rep = Thread(target=start_replication(file, ip))
                    if new_rep.isAlive() is False:
                        new_rep.start()
                    new_rep.join()
                    time.sleep(2)
        # file_info_met(file, ns_ip)
        send_file_info = Thread(target=file_info, args=(file, ns_ip))
        if send_file_info.isAlive() is False:
            send_file_info.start()
        send_file_info.join()


# HELPERS


def get_my_ip():
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        return host_ip
    except:
        print("Unable to get Hostname and IP")
        return 0


def file_info(file, ip):
    print("Creating connection DS -> NS")
    while True:
        try:  # moved this line here
            ds_ns = socket.socket()
            ds_ns.connect((ip, ds_ns_port))  # no longer throws error
            break
        except socket.error:
            print("Connection Failed, Retrying..")
            time.sleep(1)
    print("Connected to " + ip)
    message = os.stat(file)
    ds_ns.send(pickle.dumps(message))
    ds_ns.close()
    print("Disconnected from " + ip)


# INSTRUCTION EXECUTORS


def start_ftp_server():
    if not os.path.isdir(homedir):
        os.mkdir(homedir)
    if not os.path.isfile("{}/test.txt".format(homedir)):
        f = open('{}/test.txt'.format(homedir), 'tw', encoding='utf-8')
        f.close()
    handler = MyFTPHandler
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
    try:
        ftp.connect(host, port)
    except:
        return
    ftp.login(user='user', passwd='12345')
    upload_file(ftp, file)
    return


def upload_file(ftp, file):
    print("Upload file " + file)
    filename = file.split('/')[-1]

    ftp.storbinary('STOR ' + filename, open("Storage/{}".format(filename), 'rb'))
    ftp.close()


def create_file(file):
    path = homedir + "/" + file
    if os.path.isfile(path):
        msg = "Already exists"
        return msg
    else:
        open(path, 'w')
        print("Succesfully created")
        file_info = os.stat(path)
        return file_info


def delete_file(file):
    path = homedir + "/" + file
    if os.path.isfile(path):
        os.remove(path)
        msg = "Deleted"
        print(msg)
        return msg
    else:
        msg = "No such file"
        return msg


def copy_file(source, destination):
    source_path = homedir + "/" + source
    destination_path = homedir + "/" + destination
    try:
        shutil.copy(source_path, destination_path)
        print("File copied successfully.")
        file_info = os.stat(destination_path)

    except shutil.SameFileError:
        file_info = "Source and destination represents the same file."

    except IsADirectoryError:
        file_info = "Destination is a directory."
    except PermissionError:
        file_info = "Permission denied."
    return file_info


def move_file(source, destination):
    source_path = homedir + "/" + source
    destination_path = homedir + "/" + destination
    os.rename(source_path, destination_path)
    file_info = os.stat(destination_path)
    return file_info


# INTERSERVER COMMUNICATION


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
        if data == "Check":
            conn.send(pickle.dumps("Check"))

        if data == 'Initialize':
            for ip in ds:
                if ip != get_my_ip():
                    init_ds = Thread(target=start_storage, args=("Replication", ip, ds_ds_tcp_port))
                    if init_ds.isAlive() is False:
                        init_ds.start()
                    init_ds.join()
            start = Thread(target=start_ftp_server, args=())
            start.start()
            print("Server started")
            msg = "Server started"
            conn.send(pickle.dumps(msg))
        elif data == "Replication":
            global replication
            replication = True
            start = Thread(target=start_ftp_server, args=())
            start.start()
            msg = "Server started"
            conn.send(pickle.dumps(msg))
        elif data == "Upload":
            msg = "Ready to " + data
            conn.send(pickle.dumps(msg))
            start_ftp_server()
            pickle.loads(conn.recv(1024))
            conn.send(pickle.dumps("OK"))
        elif data == "Create file":
            conn.send(pickle.dumps("Ready"))
            path = pickle.loads(conn.recv(1024))
            file_info = create_file(path)
            conn.send(pickle.dumps(file_info))
        elif data == "Delete file":
            print("Delete")
            conn.send(pickle.dumps("Ready"))
            path = pickle.loads(conn.recv(1024))
            file_info = delete_file(path)
            conn.send(pickle.dumps(file_info))
        elif data == "Copy file":
            conn.send(pickle.dumps("Ready"))
            path = pickle.loads(conn.recv(1024))
            source = path.split(" ")[0]
            destination = path.split(" ")[1]
            file_info = copy_file(source, destination)
            conn.send(pickle.dumps(file_info))
        elif data == "Move file":
            conn.send(pickle.dumps("Ready"))
            path = pickle.loads(conn.recv(1024))
            source = path.split(" ")[0]
            destination = path.split(" ")[1]
            file_info = move_file(source, destination)
            conn.send(pickle.dumps(file_info))
        elif data == "Clear":
            os.system("sudo rm -r Storage/* -f")
            for ip in ds:
                if ip != get_my_ip():
                    clear_ds = Thread(target=start_storage, args=("Clear2", ip, ds_ds_tcp_port))
                    if clear_ds.isAlive() is False:
                        clear_ds.start()
                    clear_ds.join()
            msg = "Clear"
            conn.send(pickle.dumps(msg))
        elif data == "Clear2":
            os.system("sudo rm -r Storage/* -f")
            msg = "Clear"
            conn.send(pickle.dumps(msg))
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

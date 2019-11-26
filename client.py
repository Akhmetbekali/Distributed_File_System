import pickle
import socket
import os, os.path
from ftplib import FTP
import constants  # if highlighted - still don't care, it works

ns_ip = constants.ns_ip
client_ip = constants.client_ip
ftp_port = constants.ftp_port
ns_client_port = constants.ns_client_port
ns_ds_port = constants.ns_ds_port
ds_ds_tcp_port = constants.ds_ds_tcp_port


# HELPERS


def get_data(conn):
    data = conn.recv(2014)
    if data:
        return pickle.loads(data)
    else:
        return False


def print_data(data):
    if type(data) == list:
        print('Received from server: ' + ', '.join(data))
        return False
    elif type(data) == os.stat_result:
        print('Received from server: ')
        print(data)
        return False
    else:
        print('Received from server: ' + data)
        return True


def upload_script(conn):
    conn.send(pickle.dumps("Upload"))
    pickle.loads(conn.recv(1024))
    print("Enter uploading path ( '/' is current): ")
    folder = input("->")
    if os.path.isdir(folder):
        print("Enter destination path on Storage: ")
        destination = input("->")
        print("Enter filename: ")
        filename = input("->")
        if folder != "/":
            path = folder + '/' + filename
        else:
            path = filename
        if os.path.isfile(path):
            conn.send(pickle.dumps(destination))
            pickle.loads(conn.recv(1024))
            conn.send(pickle.dumps(filename))
            address = pickle.loads(conn.recv(1024))
            if ':' in address:
                ip = address.split(":")[0]
                port = int(address.split(":")[1])
                conn.send(pickle.dumps("Name"))
                hashcode = pickle.loads(conn.recv(1024))

                upload_file(ip, port, hashcode, path)
            else:
                print(address)
        else:
            print("No such file")
            conn.send(pickle.dumps("No such file"))
    else:
        print("No such directory")
        conn.send(pickle.dumps("Error"))
    return


def download_script(conn):
    conn.send(pickle.dumps("Download"))
    pickle.loads(conn.recv(1024))
    print("Enter destination path on host ( '/' is current): ")
    folder = input("->")
    print("Enter path on Storage: ")
    source = input("->")
    if os.path.isdir(folder):
        conn.send(pickle.dumps(source))
        pickle.loads(conn.recv(1024))
        print("Enter filename: ")
        filename = input("->")
        conn.send(pickle.dumps(filename))
        address = pickle.loads(conn.recv(1024))
        if ':' in address:
            ip = address.split(":")[0]
            port = int(address.split(":")[1])
            conn.send(pickle.dumps("Name"))
            hashcode = pickle.loads(conn.recv(1024))
            if folder != "/":
                folder = folder + '/'
            else:
                folder = "/"
            print(hashcode, source, filename, folder)
            download_file(ip, port, hashcode, source, filename, folder)
        else:
            print(address)
    else:
        conn.send(pickle.dumps("Error"))
    return


# FTP EXECUTORS


def upload_file(host, port, hashed_path, filename):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login("user", "12345")
    print(os.getcwd())

    ftp.storbinary('STOR ' + hashed_path, open(filename, 'rb'))
    # ftp.rename(filename, hashed_path)
    ftp.close()


def download_file(host, port, hashed_path, folder, filename, save):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login("user", "12345")
    # ftp.cwd(folder)
    save_path = save + '/' + filename
    localfile = open(save_path, 'wb')
    ftp.retrbinary('RETR ' + hashed_path, localfile.write, 1024)
    ftp.close()
    localfile.close()


# INTERSERVER COMMUNICATION


def client_nameserver():
    host = ns_ip
    port = ns_client_port
    client_socket = socket.socket()
    client_socket.connect((host, port))
    message = input(" -> ")

    while message.lower().strip() != 'exit':
        if message == "Upload":
            upload_script(client_socket)
        elif message == "Download":
            download_script(client_socket)
        else:
            client_socket.send(pickle.dumps(message))
            data = get_data(client_socket)
            print_data(data)
        message = input(" -> ")

    client_socket.close()


if __name__ == '__main__':
    print("Connecting to nameserver...")
    client_nameserver()

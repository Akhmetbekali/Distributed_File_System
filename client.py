import pickle
import socket
import os, os.path
from ftplib import FTP
import time
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


def client_nameserver():
    host = ns_ip
    port = ns_client_port
    client_socket = socket.socket()
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
            if data == "IP:":
                client_socket.send(pickle.dumps("Waiting for IP"))
                address = pickle.loads(client_socket.recv(1024))
                ip = address.split(":")[0]
                port = int(address.split(":")[1])
                # print(ip, port)
                print("Do you want to upload or download file?")
                ans = input()
                client_socket.send(pickle.dumps(ans))
                confirmation = pickle.loads(client_socket.recv(1024))
                if confirmation == "Upload":
                    print("Enter uploading path ( '/' is current): ")
                    folder = input()
                    if os.path.isdir(folder):
                        print("Where to save in Storage?")
                        destination = input()
                        client_socket.send(pickle.dumps(destination))
                        ans = pickle.loads(client_socket.recv(1024))
                        print(ans)
                        if ans == "Enter the filename: ":
                            filename = input()
                            if folder != "/":
                                path = folder + '/' + filename
                            else:
                                path = filename
                            print(path)
                            if os.path.isfile(path):
                                print("File confirmed")
                                client_socket.send(pickle.dumps(filename))
                                hashed_path = pickle.loads(client_socket.recv(1024))
                                uploadfile(ip, port, hashed_path, path)
                                client_socket.send(pickle.dumps("Client uploaded"))
                        else:
                            print(ans)
                            print(folder)
                    else:
                        print("No such directory")
                        print(folder)
                if confirmation == "Download":
                    print("Enter from where to download path ( '/' is current): ")
                    folder = input()
                    if os.path.isdir(folder):
                        client_socket.send(pickle.dumps(folder))
                        ans = pickle.loads(client_socket.recv(1024))
                        print(ans)
                        file = input()
                        client_socket.send(pickle.dumps(file))
                        hashed_path = pickle.loads(client_socket.recv(1024))
                        print("Where to save path:")
                        save = input()
                        downloadfile(ip, port, hashed_path, folder, file, save)
                        client_socket.send(pickle.dumps("Client downloading"))
                    else:
                        print("No such directory")
        message = input(" -> ")

    client_socket.close()


def uploadfile(host, port, hashed_path, filename):  # Откуда запускаешь, оттуда и скачивает
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login("user", "12345")
    print(os.getcwd())

    ftp.storbinary('STOR ' + hashed_path, open(filename, 'rb'))
    # ftp.rename(filename, hashed_path)
    ftp.close()


def downloadfile(host, port, hashed_path, folder, filename, save):  # Откуда запускаешь, туда и сохраняет
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login("user", "12345")
    ftp.cwd(folder)
    save_path = save + '/' + filename
    localfile = open(save_path, 'wb')
    ftp.retrbinary('RETR ' + hashed_path, localfile.write, 1024)
    print(ftp.pwd())
    ftp.close()
    localfile.close()


if __name__ == '__main__':
    print("Connecting to nameserver...")
    # ans = input()
    # os.chdir("Storage")
    client_nameserver()

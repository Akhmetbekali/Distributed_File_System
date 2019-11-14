import pickle
import socket
import os, os.path
from ftplib import FTP

ds1_ip = "192.168.0.136"
ds2_ip = "3.15.172.241"
ds3_ip = "18.221.170.198"
client_ip = "192.168.0.137"
ns_ip = "192.168.0.133"
ftp_port = 8000
ns_client_port = 8081
ns_ds_port = 8080
ds_ds_tcp_port = 8082


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
                client_storage(ip, port)

        message = input(" -> ")

    client_socket.close()


def client_storage(host, port):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login()
    print("Do you want to upload or download file?")
    ans = input()
    if ans == "Upload":
        uploadfile(ftp)
    elif ans == "Download":
        downloadfile(ftp)
    else:
        print("Error: No such command")


def uploadfile(ftp):  # Откуда запускаешь, оттуда и скачивает
    print("Enter uploading path ( '/' is current): ")
    path = input()
    ftp.cwd(path)
    print("Current directory: " + ftp.pwd())
    print("Enter the filename: ")
    filename = input()
    ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
    ftp.close()


def downloadfile(ftp):  # Откуда запускаешь, туда и сохраняет
    print("Enter downloading path ( '/' is current): ")
    path = input()
    ftp.cwd(path)
    print("Current directory: " + ftp.pwd())
    print("Enter the filename: ")
    filename = input()
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.pwd()

    ftp.close()
    localfile.close()


if __name__ == '__main__':
    print("Where you want to connect?")
    ans = input()
    if ans == "NS":
        client_nameserver()
    elif ans == "DS":
        client_storage(ds1_ip, ftp_port)
    else:
        print("Error: No such connection")


import pickle
import socket
import os, os.path
from ftplib import FTP


def client_nameserver():
    # host = socket.gethostname()
    host = "192.168.0.133"
    port = 8080
    client_socket = socket.socket()
    # client_socket.connect(('18.224.137.125', port)) IP - aws Instance IP; Open TCP in Security Groups
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
            data = data.split(" \n")
            if len(data) == 2:
                ip = str(data[0].split(": ")[1])
                port = int(data[1].split(": ")[1])
                client_storage(ip, port)

        message = input(" -> ")

    client_socket.close()


def client_storage(host, port):
    ftp = FTP()
    host = "192.168.0.136"
    # host = socket.gethostname()
    port = 8000
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
        client_storage()
    else:
        print("Error: No such connection")


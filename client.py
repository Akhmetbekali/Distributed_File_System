import pickle
import socket
import os, os.path
from ftplib import FTP


def client_nameserver():
    host = "192.168.1.57"
    port = 8000
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

        message = input(" -> ")

    client_socket.close()


def client_storage():
    ftp = FTP()
    ftp.connect('192.168.1.57', 8000)
    ftp.login()
    ftp.cwd('Test')  # replace with your directory
    print("Do you want to upload or download file?")
    ans = input()
    if ans == "Upload":
        uploadfile(ftp)
    elif ans == "Download":
        downloadfile(ftp)
    else:
        print("Error: No such command")


def uploadfile(ftp):
    print("Enter the filename: ")
    filename = input()
    ftp.storbinary('STOR ' + filename, open(filename, 'rb'))
    ftp.quit()


def downloadfile(ftp):
    print("Enter the filename: ")
    filename = input()
    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)
    ftp.quit()
    localfile.close()


if __name__ == '__main__':
    print(socket.gethostname())
    print("Where you want to connect? NS/DS")
    ans = input()
    if ans == "NS":
        client_nameserver()
    elif ans == "DS":
        client_storage()
    else:
        print("Error: No such connection")

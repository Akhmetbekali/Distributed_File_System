import os
import pickle
import socket
import shutil


def client_server():

    host = "192.168.0.133"
    port = 8080

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))

    while True:
        data = pickle.loads(conn.recv(1024))
        if not data:
            break

        if any(x == data for x in messages) is True:
            if data == "Make directory":
                mkdir(conn)
            elif data == "Delete directory":
                rmdir(conn)
            elif data == "Read directory":
                readdir(conn)
            elif data == "Open directory":
                opendir(conn)
            elif data == "Create file":
                mkfile(conn)
            elif data == "Delete file":
                rmfile(conn)
            elif data == "File info":
                fileinfo(conn)
            elif data == "Copy file":
                copyfile(conn)
            elif data == "Move file":
                movefile(conn)
            elif data == "Initialize":
                storage_address = ""  # IP of Data storage
                conn.send(pickle.dumps(storage_address))
                storage_server(data, "")
            # elif data == "Upload" or "Download":
            elif data == "Download":
                msg = "Enter path: "
                conn.send(pickle.dumps(msg))
                path = pickle.loads(conn.recv(1024))
                ip = "Enter IP: "
                port = "Enter port: "
                storage_address = "IP: " + ip + "\n Port: " + port
                conn.send(pickle.dumps(storage_address))
                storage_server(data, path)
            elif data == "Upload":
                msg = "Enter path: "
                conn.send(pickle.dumps(msg))
                path = pickle.loads(conn.recv(1024))
                ip = "Enter IP: "
                port = "Enter port: "
                storage_address = "IP: " + ip + "\n Port: " + port
                conn.send(pickle.dumps(storage_address))
                # storage_address = "IP: 192.168.0.136 \n Port: 8000"  # IP of Data storage
                storage_server(data, path)

        elif data.split()[0] == "Read" and data.split()[1] == "file":
            filename = data.split()[-1]
            fileread(conn, filename)
        else:
            data = "No such command"
            conn.send(pickle.dumps(data))

    conn.close()


def mkdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if os.path.exists(name):
        msg = "Already exists"
        conn.send(pickle.dumps(msg))
    else:
        os.mkdir(name)
        msg = "Succesfully created"
        conn.send(pickle.dumps(msg))


def rmdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if os.path.isdir(name):
        os.rmdir(name)
        msg = "Directory deleted"
        conn.send(pickle.dumps(msg))
    elif os.path.isfile(name):
        msg = name + " is file"
        conn.send(pickle.dumps(msg))
    else:
        msg = "No such directory"
        conn.send(pickle.dumps(msg))


def readdir(conn):
    name = os.getcwd()
    if os.path.exists(name):
        list = os.listdir(name)
        if (len(list) == 0):
            conn.send(pickle.dumps("Empty directory"))
        else:
            data = pickle.dumps(list)
            conn.send(data)
    else:
        err = "No such file or directory: " + name
        conn.send(pickle.dumps(err))


def opendir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if os.path.exists(name):
        os.chdir(name)
        conn.send(pickle.dumps(os.getcwd()))
    else:
        err = "No such file or directory: " + name
        conn.send(pickle.dumps(err))


def mkfile(conn):
    conn.send(pickle.dumps("\nEnter the name of file"))
    filename = pickle.loads(conn.recv(1024))
    path = os.getcwd() + "/" + filename
    try:
        open(path, 'x')
        msg = "Succesfully created"
        conn.send(pickle.dumps(msg))
    except FileExistsError:
        msg = "Already exists"
        conn.send(pickle.dumps(msg))
        pass


def rmfile(conn):
    conn.send(pickle.dumps("\nEnter the name of file"))
    name = pickle.loads(conn.recv(1024))
    if os.path.isfile(name):
        os.remove(name)
        msg = "File deleted"
        conn.send(pickle.dumps(msg))
    elif os.path.isdir(name):
        msg = name + " is directory"
        conn.send(pickle.dumps(msg))
    else:
        msg = "No such file"
        conn.send(pickle.dumps(msg))


def fileinfo(conn):
    conn.send(pickle.dumps("\nEnter the name of file"))
    filename = pickle.loads(conn.recv(1024))
    path = os.getcwd() + "/" + filename
    if os.path.exists(path):
        info = os.stat(path)
        data = pickle.dumps(info)
        conn.send(data)
    else:
        msg = "No such file"
        conn.send(pickle.dumps(msg))


def copyfile(conn):
    conn.send(pickle.dumps("\nEnter the path of file"))
    source = pickle.loads(conn.recv(1024))
    conn.send(pickle.dumps("\nEnter the destination of file"))
    destination = pickle.loads(conn.recv(1024))
    try:
        shutil.copyfile(source, destination)
        msg = "File copied successfully."
        conn.send(pickle.dumps(msg))

    except shutil.SameFileError:
        msg = "Source and destination represents the same file."
        conn.send(pickle.dumps(msg))

    except IsADirectoryError:
        msg = "Destination is a directory."
        conn.send(pickle.dumps(msg))

    except PermissionError:
        msg = "Permission denied."
        conn.send(pickle.dumps(msg))

    except:
        msg = "Error occurred while copying file."
        conn.send(pickle.dumps(msg))


def movefile(conn):
    conn.send(pickle.dumps("\nEnter the path of file"))
    source = pickle.loads(conn.recv(1024))
    data = source.split("/")
    filename = data[-1]

    conn.send(pickle.dumps("\nEnter the destination of file"))
    destination = pickle.loads(conn.recv(1024))
    if os.path.isdir(destination) is False:
        destination = os.getcwd() + destination

    if os.path.exists(destination) is False:
        msg = "Error in destination path"
        conn.send(pickle.dumps(msg))
    elif os.path.exists(source) is False:
        msg = "Error in source path"
        conn.send(pickle.dumps(msg))
    elif destination == source:
        msg = "Source and destination represents the same file."
        conn.send(pickle.dumps(msg))
    elif os.path.isdir(destination):
        checker = destination + "/" + filename
        if os.path.isfile(checker):
            msg = "File already exists"
            conn.send(pickle.dumps(msg))
        else:
            shutil.move(source, destination)
            msg = "File moved successfully."
            conn.send(pickle.dumps(msg))
    elif os.path.isfile(destination):
        msg = "File already exists"
        conn.send(pickle.dumps(msg))
    else:
        shutil.move(source, destination)
        msg = "File moved successfully."
        conn.send(pickle.dumps(msg))


def fileread(conn, filename):
    if os.path.isfile(filename):
        i = 1
        while True:
            index = filename.rindex('.')
            copy = filename[:index] + '_copy' + str(i) + filename[index:]
            if os.path.isfile(copy):
                i += 1
            else:
                filename = copy
                break
    conn.send(pickle.dumps("File created"))
    f = open(filename, 'wb')
    while True:
        data = conn.recv(1024)
        if data:
            f.write(data)
        else:
            conn.send(pickle.dumps("\nDone"))
            return


def storage_server(message, path):
    host = socket.gethostname()
    port = 8080
    client_socket = socket.socket()
    client_socket.connect((host, port))

    client_socket.send(pickle.dumps(message))

    data = pickle.loads(client_socket.recv(1024))
    if data == "Clear":
        print("OK")
        return "OK"
    elif data == "Ready to Upload" or "Ready to Download":
        client_socket.send(pickle.dumps(path))
    else:
        print("Error")
        return data
    # elif data == "Ready to" + message:
        # with open('test.txt', 'rb') as fh:
        #     fh.seek(0, 0)
        #     last_two = fh.readlines()[-2:]
        #     last = last_two[1].decode().split('] ')[1]
        #     path = last_two[0].decode().split('] ')[1].split(' ')[1]
        # if last == "FTP session closed (disconnect).":
        #     kill = ''  # Kill process of client_storage in storage.py
        # print("Ready to " + message)
    client_socket.close()


def ping(connection):
    hostname = connection # example
    response = os.system("ping -c 1 " + hostname)

    # and then check the response...
    if response == 0:
        print(hostname, 'is up!')
    else:
        print(hostname, 'is down!')


if __name__ == '__main__':
    messages = ["Initialize", "Create file", "Delete file",
                "File info", "Copy file", "Move file", "Open directory", "Read directory",
                "Make directory", "Delete directory", "Upload", "Download"]
    client_server()

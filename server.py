import os
import pickle
import socket
import shutil
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


def client_server():

    host = ns_ip
    port = ns_client_port

    server_socket = socket.socket()
    server_socket.bind(('', port))

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
                # storage_address = "192.168.0.136:8000"  # IP of Data storage
                # msg = \
                msg = start_storage(data, ds1_ip, ns_ds_port)
                # conn.send(pickle.dumps(msg))
                # start_storage(data, ds2_ip, ns_ds_port)
                # conn.send(pickle.dumps(msg))
                # msg = start_storage(data, ds3_ip, ns_ds_port)
                conn.send(pickle.dumps(msg))

            elif data == "Connect":
                # current_dir = os.getcwd()
                # print("Connected " + current_dir)
                # msg = "Enter destination path: "
                # conn.send(pickle.dumps(msg))
                # destination_path = pickle.loads(conn.recv(1024))
                # msg = "Enter source path: "
                # conn.send(pickle.dumps(msg))
                msg = "IP:"
                conn.send(pickle.dumps(msg))
                print(pickle.loads(conn.recv(1024)))
                msg = "{}:{}".format(ds1_ip, ftp_port)
                conn.send(pickle.dumps(msg))

                directory = pickle.loads(conn.recv(1024))
                print(directory)
                print(os.path.isdir(directory))
                if os.path.isdir(directory) is True:
                    msg = "Enter the filename: "
                    conn.send(pickle.dumps(msg))
                    filename = pickle.loads(conn.recv(1024))
                    print(filename)
                else:
                    conn.send(pickle.dumps("No such directory"))
                    print(directory)

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


def start_storage(msg, ip, port):
    # host = ds1_ip
    # port = ns_ds_port
    client_socket = socket.socket()
    client_socket.connect((ip, port))
    client_socket.send(pickle.dumps(msg))
    data = pickle.loads(client_socket.recv(1024))
    if data == "Server started":
        return data
    else:
        return "Error"


def storage_server(message, path):
    host = ds1_ip
    port = ns_ds_port
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
                "Make directory", "Delete directory", "Connect"]
    client_server()

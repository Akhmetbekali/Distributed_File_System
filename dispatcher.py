import hashlib
import os
import pickle
import socket
import shutil
from threading import Thread

import constants  # if highlighted - still don't care, it works

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

file_structure = dict()  # format - path : list of directories and files inside
current_folder = ""  # string with the path of current folder
servers = []  # list of Data Servers, format of server: [ip: str, free space: float]
path_map = dict()  # format - path/filename : [hashcode, file info, availability]


def get_server_connection():
    conn = socket.socket
    return conn


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
                file_info(conn)
            elif data == "Copy file":
                copy_file(conn)
            elif data == "Move file":
                move_file(conn)
            elif data == "Initialize":
                msg = start_storage(data, ds1_ip, ns_ds_port)
                conn.send(pickle.dumps(msg))
            elif data == "Help":
                conn.send(pickle.dumps(messages))
            elif data == "Connect":
                msg = "IP:"
                conn.send(pickle.dumps(msg))
                pickle.loads(conn.recv(1024))
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
                    path = directory + filename
                    hashed_path = calc_hash(path)
                    conn.send(pickle.dumps(hashed_path))
                    print("Waiting for connection from DS")
                    ds_ns = Thread(target=DS_NS_connection, args=())
                    ds_ns.start()
                    ds_ns.join()
                else:
                    conn.send(pickle.dumps("No such directory"))
                    print(directory)
        else:
            data = "No such command"
            conn.send(pickle.dumps(data))

    conn.close()


def DS_NS_connection():
    print("DSNS in server")
    ds_ns = socket.socket()
    ds_ns.bind(('', ds_ns_port))
    ds_ns.listen(2)
    ds_ns, address = ds_ns.accept()
    print("Connection from: " + str(address))
    info = pickle.loads(ds_ns.recv(1024))
    print(info)
    ds_ns.close()


def mkdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if file_structure.get(current_folder + name):
        msg = "Already exists"
        conn.send(pickle.dumps(msg))
    else:
        file_structure["{}/{}".format(current_folder, name)] = []
        msg = "Successfully created"
        conn.send(pickle.dumps(msg))


def rmdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if file_structure.get("{}/{}".format(current_folder, name)):
        remove_dir("{}/{}".format(current_folder, name))
        file_structure.pop("{}/{}".format(current_folder, name))
        msg = "Directory deleted"
        conn.send(pickle.dumps(msg))
    else:
        msg = "No such directory"
        conn.send(pickle.dumps(msg))


def remove_dir(dir):
    path_content = file_structure.get(dir)
    for elem in path_content:
        if file_structure.get("{}/{}".format(dir, elem)):
            remove_dir("{}/{}".format(dir, elem))
        else:
            remove_file("{}/{}".format(dir, elem))
    file_structure.pop(dir)


def remove_file(file_path):
    path_map.pop(file_path)


def readdir(conn):
    dir = current_folder
    if file_structure.get(dir):
        path_content = file_structure.get(dir)
        if len(path_content) == 0:
            conn.send(pickle.dumps("Empty directory"))
        else:
            data = pickle.dumps(path_content)
            conn.send(data)
    else:
        err = "No such file or directory: " + dir
        conn.send(pickle.dumps(err))


def opendir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    dir = pickle.loads(conn.recv(1024))
    if file_structure.get(dir):
        global current_folder
        current_folder = dir
        conn.send(pickle.dumps(file_structure.get(dir)))
    else:
        err = "No such file or directory: " + dir
        conn.send(pickle.dumps(err))


def mkfile(conn):  # TODO: NS-DS connection & send empty file
    conn.send(pickle.dumps("\nEnter the name of file"))
    filename = pickle.loads(conn.recv(1024))
    path_content = file_structure.get(current_folder)
    if filename in path_content:
        msg = "Already exists"
        conn.send(pickle.dumps(msg))
    else:
        ds = get_server_connection()
        msg = "Create file"
        ds.send(pickle.dumps(msg))
        response = pickle.loads(ds.recv(1024))
        if response == "Success":
            path_content.append(filename)
            file_structure[current_folder] = path_content
            conn.send(pickle.dumps(response))
        else:
            msg = "Error: {}".format(response)
            conn.send(pickle.dumps(msg))


def rmfile(conn):  # TODO in DS recreate file
    conn.send(pickle.dumps("\nEnter the name of file"))
    name = pickle.loads(conn.recv(1024))
    path_content = file_structure.get(current_folder)
    if name not in path_content:
        msg = "No such file"
        conn.send(pickle.dumps(msg))
    elif file_structure.get("{}/{}".format(current_folder, name)):
        msg = name + " is directory"
        conn.send(pickle.dumps(msg))
    else:
        path_content.remove(name)
        file_structure[current_folder] = path_content
        remove_file("{}/{}".format(current_folder, name))
        conn.send(pickle.dumps("Success"))


def file_info(conn):
    conn.send(pickle.dumps("\nEnter the name of file"))
    filename = pickle.loads(conn.recv(1024))
    path = "{}/{}".format(current_folder, filename)
    if path_map.get(path):
        info = path_map.get(path)[1]
        data = pickle.dumps(info)
        conn.send(data)
    else:
        msg = "No such file"
        conn.send(pickle.dumps(msg))


def copy_file(conn):  # TODO NS->DS copy & change filename according to new hashcode
    conn.send(pickle.dumps("\nEnter the path of file"))
    source = pickle.loads(conn.recv(1024))
    conn.send(pickle.dumps("\nEnter the name of file"))
    filename = pickle.loads(conn.recv(1024))
    conn.send(pickle.dumps("\nEnter the destination of file"))
    destination = pickle.loads(conn.recv(1024))
    if not file_structure.get(source):
        msg = "No such directory: {}".format(source)
        conn.send(pickle.dumps(msg))
        return
    if not file_structure.get(destination):
        msg = "No such directory: {}".format(destination)
        conn.send(pickle.dumps(msg))
        return
    if not path_map.get("{}/{}".format(source, filename)):
        msg = "No such file: {}".format(filename)
        conn.send(pickle.dumps(msg))
        return
    if path_map.get("{}/{}".format(destination, filename)):
        msg = "File already exist"
        conn.send(pickle.dumps(msg))
        return
    ds = get_server_connection()
    ds.send(pickle.dumps("Copy file"))
    pickle.loads(ds.recv(1024))
    ds.send(pickle.dumps(path_map.get("{}/{}".format(source, filename))[0]))
    response = pickle.loads(ds.recv(1024))
    consid_file(response)
    dest_content = file_structure[destination]
    dest_content.append(filename)
    file_structure[destination] = dest_content


def consid_file(response):  # TODO write file info after Uploading and replication
    path, filename, hashcode, file_info = response
    path_map["{}/{}".format(path, filename)] = [hashcode, file_info, [True] * 3]


def move_file(conn):  # TODO NS->DS rename file according to new hash
    conn.send(pickle.dumps("\nEnter the path of file"))
    source = pickle.loads(conn.recv(1024))
    data = source.split("/")
    filename = data[-1]
    source = str(data[0])
    for dir in range(1, len(data) - 1):
        source += "/{}".format(dir)

    conn.send(pickle.dumps("\nEnter the destination of file"))
    destination = pickle.loads(conn.recv(1024))
    if not file_structure.get(source):
        msg = "No such directory: {}".format(source)
        conn.send(pickle.dumps(msg))
        return
    if not file_structure.get(destination):
        msg = "No such directory: {}".format(destination)
        conn.send(pickle.dumps(msg))
        return
    if not path_map.get("{}/{}".format(source, filename)):
        msg = "No such file: {}".format(filename)
        conn.send(pickle.dumps(msg))
        return
    if path_map.get("{}/{}".format(destination, filename)):
        msg = "File already exists"
        conn.send(pickle.dumps(msg))
        return
    source_content = file_structure.get(source)
    source_content.remove(filename)
    file_structure[source] = source_content
    destination_content = file_structure.get(destination)
    destination_content.append(filename)
    file_structure[destination] = destination_content
    file = path_map.pop("{}/{}".format(source, filename))
    path_map["{}/{}".format(destination, filename)] = file
    msg = "File moved successfully."
    conn.send(pickle.dumps(msg))


def calc_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()


def start_storage(msg, ip, port):
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
    hostname = connection
    response = os.system("ping -c 1 " + hostname)

    # and then check the response...
    if response == 0:
        print(hostname, 'is up!')
    else:
        print(hostname, 'is down!')


if __name__ == '__main__':
    messages = ["Initialize", "Create file", "Delete file",
                "File info", "Copy file", "Move file", "Open directory", "Read directory",
                "Make directory", "Delete directory", "Connect", "Help"]
    current_folder = "/"
    file_structure["/"] = []
    client_server()


import socket
import pickle
import hashlib

file_structure = dict()     # format - path : list of directories and files inside
current_folder = ""         # string with the path of current folder
servers = []                # list of Data Servers, format of server: [ip: str, free space: float]
path_map = dict()           # format - path/filename : [hashcode, file info, availability]


def calc_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()


def get_server_connection():
    connection = socket.socket
    server_num = 0
    return connection, server_num


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
        if file_structure.get("{}/{}/".format(dir, elem)):
            remove_dir("{}/{}".format(dir, elem))
        else:
            remove_file("{}/{}".format(dir, elem))
    file_structure.pop(dir)


def remove_file(file_path):
    path_map.pop(file_path)


def readdir(conn):
    name = current_folder
    if file_structure.get(name):
        dir_list = file_structure.get(name)
        if len(dir_list) == 0:
            conn.send(pickle.dumps("Empty directory"))
        else:
            data = pickle.dumps(dir_list)
            conn.send(data)
    else:
        err = "No such file or directory: " + name
        conn.send(pickle.dumps(err))


def opendir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if file_structure.get(name):
        global current_folder
        current_folder = name
        conn.send(pickle.dumps(file_structure.get(name)))
    else:
        err = "No such file or directory: " + name
        conn.send(pickle.dumps(err))


# def mkfile(conn):
#     conn.send(pickle.dumps("\nEnter the name of file"))
#     filename = pickle.loads(conn.recv(1024))
#     path_content = file_structure.get(current_folder)
#     if filename in path_content:
#         msg = "Already exists"
#         conn.send(pickle.dumps(msg))
#     else:
#         ds = get_server_connection()
#         msg = "Create file"
#         ds.send(pickle.dumps(msg))
#         response = pickle.loads(ds.recv(1024))
#         if response == "Success":
#             path_content.append(filename)
#             file_structure[current_folder] = path_content
#             conn.send(pickle.dumps(response))
#         else:
#             msg = "Error: {}".format(response)
#             conn.send(pickle.dumps(msg))


def rmfile(conn):
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


def copyfile(conn):
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
    ds = get_server_connection()
    ds.send(pickle.dumps("Copy file"))
    pickle.loads(ds.recv(1024))
    ds.send(path_map.get("{}/{}".format(source, filename))[0])
    response = pickle.loads(ds.recv(1024))
    consid_file(response)
    dest_content = file_structure[destination]
    dest_content.append(filename)
    file_structure[destination] = dest_content


def consid_file(response):
    path, filename, hashcode, file_info = response
    path_map["{}/{}".format(path, filename)] = [hashcode, file_info, [True]*3]


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


print(calc_hash("/home/file.txt"))

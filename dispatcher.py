import socket
import pickle
import hashlib

file_structure = dict()     # format - path : list of directories and files inside
current_folder = ""         # string with the path of current folder
servers = []                # list of Data Servers, format of server: [ip: str, free space: float]
files = dict()              # format - hash : [path, file info]


def calc_hash(file_path):
    return hashlib.sha256(file_path.encode()).hexdigest()


def get_server_connection():
    connection = socket.socket
    return connection


def mkdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if file_structure.get(current_folder + name):
        msg = "Already exists"
        conn.send(pickle.dumps(msg))
    else:
        file_structure[current_folder + name] = []
        msg = "Succesfully created"
        conn.send(pickle.dumps(msg))


def rmdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if file_structure.get(name):
        file_structure.pop(current_folder + name)
        msg = "Directory deleted"
        conn.send(pickle.dumps(msg))
    else:
        msg = "No such directory"
        conn.send(pickle.dumps(msg))


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


def mkfile(conn):
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


def rmfile(conn):
    conn.send(pickle.dumps("\nEnter the name of file"))
    name = pickle.loads(conn.recv(1024))
    path_content = file_structure.get(current_folder)
    if name not in path_content:
        msg = "No such file"
        conn.send(pickle.dumps(msg))
    elif file_structure.get(current_folder + name + "/"):
        msg = name + " is directory"
        conn.send(pickle.dumps(msg))
    else:
        ds = get_server_connection()
        msg = "Delete file"
        ds.send(pickle.dumps(msg))
        response = pickle.loads(ds.recv(1024))
        ds.send(pickle.dumps(name))
        if response == "Success":
            path_content.remove(name)
            file_structure[current_folder] = path_content
            conn.send(pickle.dumps(response))
        else:
            msg = "Error: {}".format(response)
            conn.send(pickle.dumps(msg))


def file_info(conn):
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


print(calc_hash("/home/file.txt"))

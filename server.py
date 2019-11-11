import os
import pickle
import socket
import shutil


def server_program():

    host = socket.gethostname()
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


if __name__ == '__main__':
    messages = ["Initialize", "Create file", "Read file", "Write file", "Delete file",
                "File info", "Copy file", "Move file", "Open directory", "Read directory",
                "Make directory", "Delete directory"]
    server_program()

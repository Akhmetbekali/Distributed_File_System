import os
import pickle
import socket


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
    if os.path.exists(name):
        os.rmdir(name)
        msg = "Directory deleted"
        conn.send(pickle.dumps(msg))
    else:
        msg = "No such directory"
        conn.send(pickle.dumps(msg))


def readdir(conn):
    conn.send(pickle.dumps("\nEnter the name of directory"))
    name = pickle.loads(conn.recv(1024))
    if os.path.exists(name):
        list = os.listdir(name)
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


if __name__ == '__main__':
    messages = ["Initialize", "Create file", "Read file", "Write file", "Delete file",
                "File info", "Copy file", "Move file", "Open directory", "Read directory",
                "Make directory", "Delete directory"]
    server_program()
    # print(os.listdir("DS_project"))

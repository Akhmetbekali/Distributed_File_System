import os
import socket


def server_program():

    host = socket.gethostname()
    port = 8000

    server_socket = socket.socket()
    server_socket.bind((host, port))

    server_socket.listen(2)
    conn, address = server_socket.accept()
    print("Connection from: " + str(address))
    while True:
        data = conn.recv(1024).decode()
        if not data:
            break

        print("from [" + str(address) + "]" + str(data))
        #data = input(' -> ')
        #conn.send(data.encode())

        if any(x == data for x in messages) is True:
            conn.send(data.encode())
            if data == "Make directory":
                conn.send("\nEnter the name of directory".encode())
                name = conn.recv(1024).decode()
                if os.path.exists(name):
                    conn.send("Already exists".encode())
                else:
                    os.mkdir(name)
                    conn.send("Succesfully created".encode())
        else:
            data = "No such command"
            conn.send(data.encode())

    conn.close()


if __name__ == '__main__':
    messages = ["Initialize", "Create file", "Read file", "Write file", "Delete file",
                "File info", "Copy file", "Move file", "Open directory", "Read directory",
                "Make directory", "Delete directory"]
    server_program()

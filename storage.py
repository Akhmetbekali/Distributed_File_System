from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

authorizer = DummyAuthorizer()
authorizer.add_user("user", "12345", "/home/dapimex/PycharmProjects/ds_dfs", perm="elradfmw")
authorizer.add_anonymous("/home/dapimex/PycharmProjects/ds_dfs", perm="elradfmw")

handler = FTPHandler
handler.authorizer = authorizer

server = FTPServer(("127.0.0.1", 8000), handler)
server.serve_forever()
import socket
import threading

from transmission_protocol import get_ip
from transmission_protocol import get_port
from transmission_protocol import send_data
from transmission_protocol import recv_data
from transmission_protocol import EXIT_STR


class ServerThread(threading.Thread):
    def __init__(self, server_s, client_s):
        super(ServerThread, self).__init__()
        self._ser_s = server_s
        self._cli_s = client_s

    def run(self):
        while True:
            recv_info = recv_data(self._cli_s)
            print recv_info

            if str.strip(recv_info) == EXIT_STR:
                self._cli_s.close()
                self._ser_s.close()
                exit(0)

            while True:
                # data = raw_input('> ')
                data = "server: %s" % recv_info
                ret = send_data(self._cli_s, data)
                if ret == -1:
                    continue

                if str.strip(data) == EXIT_STR:
                    self._cli_s.close()
                    self._ser_s.close()
                    exit(0)
                break

host_ip = get_ip()
host_port = get_port()

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((host_ip, host_port))
socket.listen(2)

while True:
    print "server is ready to accept client."
    cli, addr = socket.accept()
    print "accept client from %s" % repr(addr)

    thread = ServerThread(socket, cli)
    thread.start()

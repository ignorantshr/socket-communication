#!/bin/python

import threading
from communication.protocol import *


event = threading.Event()


def init():
    host_ip = get_ip()
    host_port = get_port()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host_ip, host_port))
    server_socket.listen(0)
    ser_name = ""
    while True:
        ser_name = raw_input("your name: ")
        if len(ser_name) == 0:
            continue
        break

    log_communication(MUST, "server is ready to accept a client.")

    cli, address = server_socket.accept()
    log_communication(MUST, "accept client from %s" % repr(address))
    cli_name = _exchange_name(cli, ser_name)

    recv_t = RecvThread(cli, cli_name)
    recv_t.setDaemon(True)
    recv_t.start()
    send_t = SendThread(cli)
    send_t.setDaemon(True)
    send_t.start()

    event.wait()
    log_communication(MUST, "get close signal.")
    server_socket.close()
    exit(0)


def _exchange_name(cli, ser_name):
    _, cli_name = recv_data(cli)
    cli_name = json.loads(cli_name).get("name")
    send_data(cli, '{"name": "%s"}' % ser_name)
    return cli_name


class RecvThread(threading.Thread):
    def __init__(self, client_socket, cli_name):
        super(RecvThread, self).__init__()
        self._cli_s = client_socket
        self._cli_n = cli_name

    def run(self):
        while True:
            _, recv_info = recv_data(self._cli_s)
            print "%s >>>\n%s\n<<<\n" % (self._cli_n, recv_info)

            if str.strip(recv_info) in (EXIT_STR, EXIT_ALL_STR):
                self._cli_s.close()
                event.set()
                exit(0)


class SendThread(threading.Thread):
    def __init__(self, client_socket):
        super(SendThread, self).__init__()
        self._cli_s = client_socket

    def run(self):
        while True:
            data = raw_input("> ")
            ret = send_data(self._cli_s, data)
            if ret == -1:
                continue

            if str.strip(data) in (EXIT_STR, EXIT_ALL_STR):
                self._cli_s.close()
                event.set()
                exit(0)


init()

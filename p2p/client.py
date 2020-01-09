#!/bin/python
# coding=utf-8

import threading
from communication.protocol import *

event = threading.Event()


def init():
    host_ip = get_ip()
    host_port = get_port()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host_ip, host_port))
    except Exception as e:
        print e
        exit(1)

    ser_name = _exchange_name(client)

    recv_t = RecvThread(client, ser_name)
    recv_t.setDaemon(True)
    recv_t.start()
    send_t = SendThread(client)
    send_t.setDaemon(True)
    send_t.start()

    event.wait()
    log_communication(MUST, "get close signal.")
    client.close()
    exit(0)


def _exchange_name(cli):
    # wait server to get ready to receive
    time.sleep(1)
    while True:
        cli_name = raw_input("your name: ")
        if len(cli_name) == 0:
            continue
        send_data(cli, '{"name": "%s"}' %
                  cli_name.decode('utf-8').encode('utf-8'))
        break
    _, ser_name = recv_data(cli)                    # str
    ser_name = json.loads(ser_name).get("name")     # unicode
    return ser_name


class RecvThread(threading.Thread):
    def __init__(self, client_socket, ser_name):
        super(RecvThread, self).__init__()
        self._cli_s = client_socket
        self._ser_n = ser_name

    def run(self):
        while True:
            _, recv_info = recv_data(self._cli_s)   # str
            print "%s >>>\n%s\n<<<\n" % \
                  (self._ser_n, recv_info.decode('utf-8'))

            if str.strip(recv_info) in (EXIT_STR, EXIT_ALL_STR):
                event.set()
                exit(0)


class SendThread(threading.Thread):
    def __init__(self, client_socket):
        super(SendThread, self).__init__()
        self._cli_s = client_socket

    def run(self):
        while True:
            data = raw_input("> ")
            ret = send_data(self._cli_s, data.decode('utf-8').encode('utf-8'))
            if ret == -1:
                continue

            if str.strip(data) in (EXIT_STR, EXIT_ALL_STR):
                event.set()
                exit(0)


init()

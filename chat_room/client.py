#!/bin/python

import threading

from protocol import *


def _receive_message(client_socket):
    while True:
        receive_message = recv_data(client_socket)
        print receive_message

host_ip = get_ip()
host_port = get_port()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((host_ip, host_port))
except Exception as e:
    print e.message
    exit(1)

receive_t = threading.Thread(target=_receive_message, args=(client,))
receive_t.setDaemon(True)
receive_t.start()

while True:
    data = raw_input("> ")
    ret = send_data(client, data)
    if ret == -1:
        continue

    if str.strip(data) in (EXIT_STR, EXIT_ALL_STR):
        client.close()
        exit(0)

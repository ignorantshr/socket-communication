#!/bin/python
# coding=utf-8

import threading
import sys

from communication.protocol import *

reload(sys)
sys.setdefaultencoding('utf-8')


def _receive_message(client_socket):
    while True:
        _, receive_message = recv_data(client_socket)
        print receive_message

host_ip = get_ip()
host_port = get_port()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((host_ip, host_port))
except Exception as e:
    print e
    exit(1)

receive_t = threading.Thread(target=_receive_message, args=(client,))
# quit with main program
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

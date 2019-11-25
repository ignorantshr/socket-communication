#!/bin/python

import socket

from protocol import *

host_ip = get_ip()
host_port = get_port()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((host_ip, host_port))
except Exception as e:
    print e.message
    exit(1)

while True:
    data = raw_input("> ")
    ret = send_data(client, data)
    if ret == -1:
        continue

    if str.strip(data) in (EXIT_STR, EXIT_ALL_STR):
        client.close()
        exit(0)

    _, ret_info = recv_data(client)
    print ret_info
    if str.strip(ret_info) == EXIT_STR:
        client.close()
        exit(0)

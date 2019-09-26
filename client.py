import socket
from transmission_protocol import send_data
from transmission_protocol import recv_data


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect(('127.0.0.1', 9003))

while True:
    data = raw_input("> ")
    ret = send_data(socket, data)
    if ret == -1:
        continue

    if str.strip(data) == 'exit':
        socket.close()
        exit(0)

    ret_info = recv_data(socket)
    print ret_info
    if str.strip(ret_info) == 'exit':
        socket.close()
        exit(0)

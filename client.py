import socket
from transmission_protocol import get_ip
from transmission_protocol import get_port
from transmission_protocol import send_data
from transmission_protocol import recv_data
from transmission_protocol import EXIT_STR

host_ip = get_ip()
host_port = get_port()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host_ip, host_port))

while True:
    data = raw_input("> ")
    ret = send_data(client, data)
    if ret == -1:
        continue

    if str.strip(data) == EXIT_STR:
        client.close()
        exit(0)

    ret_info = recv_data(client)
    print ret_info
    if str.strip(ret_info) == EXIT_STR:
        client.close()
        exit(0)

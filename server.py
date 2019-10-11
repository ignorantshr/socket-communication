import socket
from transmission_protocol import get_ip
from transmission_protocol import get_port
from transmission_protocol import send_data
from transmission_protocol import recv_data
from transmission_protocol import EXIT_STR

host_ip = get_ip()
host_port = get_port()

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind((host_ip, host_port))
socket.listen(1)
cli, addr = socket.accept()
print "accept from %s" % repr(addr)

while True:
    recv_info = recv_data(cli)
    print recv_info

    if str.strip(recv_info) == EXIT_STR:
        cli.close()
        socket.close()
        exit(0)

    while True:
        data = raw_input('> ')
        ret = send_data(cli, data)
        if ret == -1:
            continue

        if str.strip(data) == EXIT_STR:
            cli.close()
            socket.close()
            exit(0)
        break

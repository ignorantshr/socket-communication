import socket
from transmission_protocol import send_data
from transmission_protocol import recv_data


socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.bind(('0.0.0.0', 9003))
socket.listen(1)
cli, addr = socket.accept()
print "accept from %s" % repr(addr)

while True:
    recv_info = recv_data(cli)
    print recv_info

    if str.strip(recv_info) == 'exit':
        cli.close()
        socket.close()
        exit(0)

    data = raw_input('> ')
    ret = send_data(cli, data)
    if ret == -1:
        continue

    if str.strip(data) == 'exit':
        cli.close()
        socket.close()
        exit(0)

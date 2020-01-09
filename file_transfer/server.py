#!/bin/python
import ast
import threading

from communication.protocol import *

event = threading.Event()
threads = []


def init():
    host_ip = get_ip()
    host_port = get_port()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # reuse port
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host_ip, host_port))
    server_socket.listen(2)

    thread_dispatcher = threading.Thread(target=client_dispatcher,
                                         args=(server_socket,))
    # quit with main program
    thread_dispatcher.setDaemon(True)
    thread_dispatcher.start()

    log_communication(MUST, "server is ready to accept client.")

    event.wait()

    for th in threads:
        log_communication(DEBUG, th)
        if th.isAlive():
            th.join()
            log_communication(DEBUG, "%s has exited" % th)
    server_socket.close()
    exit(0)


def client_dispatcher(server_socket):
    while not event.isSet():
        cli, address = server_socket.accept()
        log_communication(MUST, "accept client from %s" % repr(address))

        thread = ServerThread(cli, address)
        threads.append(thread)
        thread.start()


class ServerThread(threading.Thread):
    def __init__(self, client_socket, client_addr):
        super(ServerThread, self).__init__()
        self._cli_s = client_socket
        self._cli_a = client_addr

    def run(self):
        _, recv_info = recv_data(self._cli_s)
        # str -> dict
        file_info = ast.literal_eval(recv_info)
        name = file_info.get('file')
        size = file_info.get('size')
        if name == EXIT_ALL_STR:
            log_communication(MUST, "get close server signal.")
            event.set()
            exit(0)

        time_stamp = time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))
        name = name + '_' + time_stamp + '.transfer'
        log_communication(MUST, "prepare receive: %s %d", name, size)

        received_len = 0
        with open(name, mode='w+') as f:
            while received_len < size:
                tmp_len, recv_info = recv_data(self._cli_s)
                if tmp_len == 0 or len(recv_info) == 0:
                    log_communication(WARN,
                                      'The client has closed the socket.')
                    break
                received_len += tmp_len
                f.write(recv_info)
        log_communication(MUST, 'The file %s has been received[%d].' %
                          (name, received_len))
        self._cli_s.close()
        exit(0)

init()

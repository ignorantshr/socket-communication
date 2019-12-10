#!/bin/python

import threading

from communication.protocol import *

event = threading.Event()
threads = []


def init():
    host_ip = get_ip()
    host_port = get_port()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host_ip, host_port))
    server_socket.listen(2)

    thread_dispatcher = threading.Thread(target=client_dispatcher, args=(server_socket,))
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
        while True:
            _, recv_info = recv_data(self._cli_s)
            log_communication(MUST, "received from %s: %s" % (self._cli_a, recv_info))

            if str.strip(recv_info) == EXIT_STR:
                self._cli_s.close()
                threads.remove(self)
                exit(0)

            if str.strip(recv_info) == EXIT_ALL_STR:
                self._cli_s.close()
                event.set()
                log_communication(MUST, "get close server signal.")
                exit(0)

            data = "server: %s" % recv_info
            send_data(self._cli_s, data)


init()

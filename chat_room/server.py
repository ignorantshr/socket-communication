#!/bin/python
# coding=utf-8

import threading
import sys

from communication.protocol import *

reload(sys)
sys.setdefaultencoding('utf-8')


event = threading.Event()
threads = []
clients = []


def init():
    host_ip = get_ip()
    host_port = get_port()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
        clients.append(cli)
        thread.start()
        for client in clients:
            data = "%s has entered the chat room." % (repr(address),)
            send_data(client, data)


class ServerThread(threading.Thread):
    def __init__(self, client_socket, client_addr):
        super(ServerThread, self).__init__()
        self._cli_s = client_socket
        self._cli_a = client_addr

    def run(self):
        while True:
            _, recv_info = recv_data(self._cli_s)
            log_communication(MUST, "received from %s: %s" %
                              (self._cli_a, recv_info))

            if str.strip(recv_info) == EXIT_STR:
                self._cli_s.close()
                threads.remove(self)
                clients.remove(self._cli_s)
                for cli in clients:
                    send_data(cli, "%s has exited the chat room." %
                              (self._cli_a,))
                exit(0)

            if str.strip(recv_info) == EXIT_ALL_STR:
                self._cli_s.close()
                log_communication(MUST, "get close server signal.")
                threads.remove(self)
                clients.remove(self._cli_s)
                for cli in clients:
                    send_data(cli, "the chat room will be dissolved "
                                   "after all members exit.")
                event.set()
                exit(0)

            for cli in clients:
                if cli is not self._cli_s:
                    data = "%s: %s" % (self._cli_a, recv_info)
                    send_data(cli, data)

init()

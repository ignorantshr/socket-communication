#!/bin/python
import commands
import os
from time import sleep

from communication.protocol import *


def _send_file():
    size = int(_get_file_size(src_path))
    name = os.path.basename(src_path)
    sent_size = 0
    log_communication(MUST, 'file: %s, size: %d' % (src_path, size))
    send_data(client, '{"file": "%s", "size": %d}' % (os.path.join(des_path, name), size))

    with open(src_path, mode='r') as f:
        while size - sent_size > 0:
            data = f.read(MAX_TOTAL_SIZE)
            tmp_len = send_data(client, data)
            if tmp_len == -1:
                break
            sent_size += tmp_len
            sleep(0.1)

    log_communication(MUST, 'The file %s has been sent[%d].' % (name, sent_size))


def _exit_server():
    send_data(client, '{"file": "%s", "size": %d}' % (EXIT_ALL_STR, 0))
    log_communication(MUST, 'close server signal has been sent.')


def _get_file_path():
    while True:
        source_path = raw_input("please input the file's absolute path or %s to close the server: " % EXIT_ALL_STR)
        if len(source_path) == 0:
            print 'the path is invalid!'
            continue
        if source_path == EXIT_STR:
            exit(0)
        if source_path == EXIT_ALL_STR:
            return EXIT_ALL_STR, None
        dest_path = raw_input('please input the destination directory: ')
        if not os.path.isfile(source_path):
            print 'the %s is not a file!' % source_path
            continue
        return source_path, dest_path


def _get_file_size(file_path):
    cmd = ['ls', '-l', file_path]
    status, output = commands.getstatusoutput(' '.join(cmd))
    if status != 0:
        print output
        exit(1)
    return output.split(' ')[4]


host_ip = get_ip()
host_port = get_port()
src_path, des_path = _get_file_path()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((host_ip, host_port))
except Exception as e:
    print e.message
    exit(1)

if src_path != EXIT_ALL_STR:
    _send_file()
else:
    _exit_server()

client.close()
exit(0)

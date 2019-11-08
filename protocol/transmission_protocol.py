import json
import re

from communication_exception import *

DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4

metadata_len = 73
packet_len = 10
all_len = metadata_len + packet_len
EXIT_STR = 'exit'
EXIT_ALL_STR = 'exit_all'
LOG_LEVEL = WARN


def log_communication(level, message):
    def display():
        print message

    if LOG_LEVEL <= level:
        display()


def get_ip(default_ip='0.0.0.0'):
    ip_repx = re.compile(r'^((2([0-4]\d|5[0-5])|[0-1]?\d{1,2})\.){3}(2([0-4]\d|5[0-5])|[0-1]?\d{1,2})$')

    while True:
        tmp_host = raw_input('please input server ip.(default [%s]): ' % default_ip)
        if len(tmp_host) == 0:
            return default_ip
        if tmp_host == EXIT_STR:
            exit(0)

        ret = ip_repx.match(tmp_host)
        if ret is None:
            print "invalid ip address."
        else:
            return ret.group()


def get_port(default_port=9002):
    port_repx = re.compile(r'(([1-5]\d{4}|6([0-4]\d{3}|5([0-4]\d{2}|5([0-2]\d|3[0-6]))))|[8-9]\d{3})$')

    while True:
        tmp_port = raw_input('please input server port.(8000~65536, default [%d]): ' % default_port)
        if len(tmp_port) == 0:
            return default_port
        if tmp_port == EXIT_STR:
            exit(0)

        ret = port_repx.match(tmp_port)
        if ret is None:
            print "invalid port."
        else:
            return int(ret.group())


class _DataPacket:
    def __init__(self, total_size, file_counts, file_index, data):
        """
        initial packet
        :param total_size: total size of file
        :param file_counts: total counts of file pieces
        :param file_index: index of files
        :param data: one of file pieces
        """
        # data = data.encode('utf-8')
        self._total_size = total_size
        self._file_counts = file_counts
        self._file_index = file_index
        self._data_len = len(data)
        self._data = data

    def __repr__(self):
        return '{"total_size": %5d, "counts": %5d, "index": %5d, "data_len": %5d}%s' % (self._total_size,
                                                                                        self._file_counts,
                                                                                        self._file_index,
                                                                                        self._data_len,
                                                                                        self._data)


def _data_pieces(data_size, piece_size):
    if data_size == 0:
        raise DataSizeZeroException("file_size cann't be 0.")
    if piece_size == 0:
        raise PieceSizeZeroException("piece_size cann't be 0.")
    return (data_size + piece_size - 1) / piece_size


def send_data(client, data):
    """
    split big data to many packet to send
    :param client: client socket
    :param data: data to be send
    :return: 0: success; -1: excepted data
    """
    total_size = len(data)
    try:
        pieces = _data_pieces(total_size, packet_len)
    except (DataSizeZeroException, PieceSizeZeroException) as e:
        print e.message
        return -1
    for i in range(1, pieces + 1):
        if i == pieces:
            pack = _DataPacket(total_size, pieces, i, data[(i - 1) * packet_len:])
        else:
            pack = _DataPacket(total_size, pieces, i, data[(i - 1) * packet_len:i * packet_len])
        all_data = repr(pack)
        log_communication(DEBUG, "send: %s" % all_data)
        send_len = client.send(all_data)
        while send_len < len(all_data):
            send_len += client.send(all_data[send_len:])

    return 0


def recv_data(client):
    """
    receive big data from client
    :param client: client socket
    :return: string
    """
    total_data = ''
    tmp_size = 0
    disorder_data = dict()

    recv_info = client.recv(all_len)
    while len(recv_info) < metadata_len:
        recv_info += client.recv(all_len - len(recv_info))
        log_communication(DEBUG, "recv: %s" % recv_info)
    # client stopped the connection
    if recv_info == '':
        return EXIT_STR

    tmp_data = recv_info[metadata_len:]

    metadata = json.loads(recv_info[0:metadata_len])
    total_size = metadata.get('total_size', 0)
    if total_size == 0:
        return ''
    index = metadata.get('index', 0)
    data_len = metadata.get('data_len', 0)
    tmp_size += data_len
    disorder_data[index] = tmp_data

    while tmp_size < total_size:
        recv_info = client.recv(all_len)
        while len(recv_info) < metadata_len:
            recv_info += client.recv(all_len - len(recv_info))
            log_communication(DEBUG, "recv: %s" % recv_info)

        # client stopped the connection
        if recv_info == '':
            return EXIT_STR

        tmp_data = recv_info[metadata_len:]

        metadata = json.loads(recv_info[0:metadata_len])
        index = metadata.get('index', 0)
        data_len = metadata.get('data_len', 0)
        tmp_size += data_len
        disorder_data[index] = tmp_data

    for _, v in sorted(disorder_data.items()):
        total_data += v
    return total_data

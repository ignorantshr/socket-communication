import json
import re

from communication_exception import *

DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4

metadata_len = 56  # Generate values base metadata template
packet_len = 10  # <= MAX_DATA_LEN
all_len = metadata_len + packet_len
EXIT_STR = 'exit'
EXIT_ALL_STR = 'exit_all'
LOG_LEVEL = INFO

# These values can only be adjusted down
MAX_FILE_INDEX = 1024
MAX_DATA_LEN = 1024
MAX_TOTAL_SIZE = MAX_FILE_INDEX * MAX_DATA_LEN


def log_communication(level, message):
    def display():
        print message

    if LOG_LEVEL <= level:
        display()


def get_ip(default_ip='0.0.0.0'):
    ip_repx = re.compile(r'^((2([0-4]\d|5[0-5])|[0-1]?\d{1,2})\.){3}(2([0-4]\d|5[0-5])|[0-1]?\d{1,2})$')

    while True:
        tmp_host = raw_input('please input server ip(default [%s]) or [%s] to exit: ' % (default_ip, EXIT_STR))
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
        tmp_port = raw_input('please input server port(8000~65536, default [%d]) or [%s] to exit: : ' %
                             (default_port, EXIT_STR))
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
    def __init__(self, total_size, file_index, data):
        """
        initial packet
        :param total_size: total size of file
        :param file_index: index of files
        :param data: one of file pieces
        """
        # data = data.encode('utf-8')
        self._total_size = total_size  # <= 1024 * 1024
        self._file_index = file_index  # <= 1024
        self._data_len = len(data)  # <= 1024
        self._data = data

        self._check_args()

    def _check_args(self):
        if type(self._total_size) is not int:
            raise TypeError("total_size is not int.")
        elif self._total_size > MAX_TOTAL_SIZE:
            raise OutOfBoundsException("total_size greater than %d" % MAX_TOTAL_SIZE)

        if type(self._file_index) is not int:
            raise TypeError("file_index is not int.")
        elif self._file_index > MAX_FILE_INDEX:
            raise OutOfBoundsException("file_index greater than %d" % MAX_FILE_INDEX)

        if type(self._data_len) is not int:
            raise TypeError("data_len is not int.")
        elif self._data_len > MAX_DATA_LEN:
            raise OutOfBoundsException("data_len greater than %d" % MAX_DATA_LEN)

    def __repr__(self):
        return '{"total_size": %7d, "index": %4d, "data_len": %4d}%s' % (self._total_size,
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
            pack = _DataPacket(total_size, i, data[(i - 1) * packet_len:])
        else:
            pack = _DataPacket(total_size, i, data[(i - 1) * packet_len:i * packet_len])
        all_data = repr(pack)
        log_communication(DEBUG, "send to %s: %s" % (client.getpeername(), all_data))
        send_len = client.send(all_data)
        log_communication(DEBUG, "send_len = %d" % send_len)
        while send_len < len(all_data):
            send_len += client.send(all_data[send_len:])
            log_communication(DEBUG, "send_len = %d" % send_len)

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
        log_communication(DEBUG, "receive from %s : %s" % (client.getpeername(), recv_info))
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
            log_communication(DEBUG, "receive from %s : %s" % (client.getpeername(), recv_info))

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

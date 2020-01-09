import json
import re
import time

from communication_exception import *

DEBUG = 1
INFO = 2
WARN = 3
ERROR = 4
MUST = 5  # Information that must be logged

LOG_LEVELS = {
    1: 'DEBUG',
    2: 'INFO',
    3: 'WARN',
    4: 'ERROR',
    5: 'MUST'}

LOG_LEVEL = INFO
print 'LOG_LEVEL=', LOG_LEVELS[LOG_LEVEL]

# meta info
TOTAL_SIZE = "total_size"  # %8d
INDEX = "index"  # %4d
DATA_LEN = "data_len"  # %4d


def _generate_template_and_len():
    def _get_int_from_format_str(format_str):
        int_repx = re.compile('[\d]+')
        ret = int_repx.search(format_str)
        if ret is None:
            print '%s is not valid.' % (format_str,)
            return 0
        return int(ret.group())

    def _get_meta_len():
        total_len = 0
        arg_num = len(meta_args)
        for key, value in meta_args.iteritems():
            total_len += len(key)
            total_len += _get_int_from_format_str(value)
        total_len += 2 + arg_num*(2+1+1) + (arg_num-1)*(1+1)
        return total_len

    # custom your meta args in here,
    meta_args = {TOTAL_SIZE: '%8d',
                 INDEX: '%4d',
                 DATA_LEN: '%4d'}
    argc = len(meta_args)
    string = '{'
    for v in meta_args.itervalues():
        if argc == 1:
            string += '"%%s": %s' % (v,)
        else:
            string += '"%%s": %s, ' % (v,)
        argc -= 1
    string += '}%s'

    return _get_meta_len(), string
# print _generate_template_and_len()

# you can excute 'print _generate_template_and_len()' to get len and template
metadata_len = 57  # Generate values according to metadata template
packet_len = 100  # <= MAX_DATA_LEN
all_len = metadata_len + packet_len

# close self client command
EXIT_STR = 'exit'
# close server command
EXIT_ALL_STR = 'exit_all'

# These values can only be adjusted down
MAX_FILE_INDEX = 99  # %4d
MAX_DATA_LEN = 9999  # %4d
MAX_TOTAL_SIZE = min(packet_len * MAX_FILE_INDEX, 99999999)  # %8d


def log_communication(level, format_str, *args):
    def _display():
        if len(args) == 0:
            print "%s [%5s]: %s" % (time.strftime('%Y-%m-%d %H:%M:%S',
                                                  time.localtime(time.time())),
                                    LOG_LEVELS[level],
                                    format_str)
        else:
            print "%s [%5s]: %s" % (time.strftime('%Y-%m-%d %H:%M:%S',
                                                  time.localtime(time.time())),
                                    LOG_LEVELS[level],
                                    format_str % args)

    def _log_to_file():
        pass

    if LOG_LEVEL <= level:
        _display()


def get_ip(default_ip='0.0.0.0'):
    ip_repx = re.compile(r'^((2([0-4]\d|5[0-5])|[0-1]?\d{1,2})\.){3}'
                         r'(2([0-4]\d|5[0-5])|[0-1]?\d{1,2})$')

    while True:
        tmp_host = raw_input('please input server ip(default [%s]) or [%s] '
                             'to exit(any of the following steps can be): '
                             '' % (default_ip, EXIT_STR))
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
    # 1000~9999
    port_repx = re.compile(r'([1-9]\d{3})$')

    while True:
        tmp_port = raw_input('please input server port(8000~65536, '
                             'default [%d]): ' % default_port)
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
        self._template = '{"%s": %8d, "%s": %4d, "%s": %4d}%s'

    def _check_args(self):
        if type(self._total_size) is not int:
            raise TypeError("total_size is not int.")
        elif self._total_size > MAX_TOTAL_SIZE:
            raise OutOfBoundsException("total_size greater than %d" %
                                       MAX_TOTAL_SIZE)

        if type(self._file_index) is not int:
            raise TypeError("file_index is not int.")
        elif self._file_index > MAX_FILE_INDEX:
            raise OutOfBoundsException("file_index greater than %d" %
                                       MAX_FILE_INDEX)

        if type(self._data_len) is not int:
            raise TypeError("data_len is not int.")
        elif self._data_len > MAX_DATA_LEN:
            raise OutOfBoundsException("data_len greater than %d" %
                                       MAX_DATA_LEN)

    def __repr__(self):
        return self._template % (TOTAL_SIZE, self._total_size,
                                 INDEX, self._file_index,
                                 DATA_LEN, self._data_len,
                                 self._data)


def _data_pieces(data_size, piece_size):
    if data_size == 0:
        raise DataSizeZeroException("file_size cann't be 0.")
    if piece_size == 0:
        raise PieceSizeZeroException("piece_size cann't be 0.")
    pieces = (data_size + piece_size - 1) / piece_size
    log_communication(DEBUG, "%d data will be split into %d pieces." %
                      (data_size, pieces))
    return pieces


def send_data(client, data):
    """
    split big data to many packet to send
    :param client: client socket
    :param data: data to be send
    :return: > 0: size has been sent of data; -1: excepted data
    """
    total_size = len(data)
    total_sent = 0

    try:
        pieces = _data_pieces(total_size, packet_len)
    except (DataSizeZeroException, PieceSizeZeroException) as e:
        log_communication(ERROR, e.message)
        return -1

    for i in range(1, pieces + 1):
        if i == pieces:
            pack = _DataPacket(total_size, i, data[(i - 1) * packet_len:])
        else:
            pack = _DataPacket(total_size, i,
                               data[(i - 1) * packet_len:i * packet_len])
        all_data = repr(pack)
        log_communication(DEBUG, "send to %s: %s" %
                          (client.getpeername(), all_data))
        sent_len = client.send(all_data)
        log_communication(DEBUG, "send_len = %d" % sent_len)
        while sent_len < len(all_data):
            sent_len += client.send(all_data[sent_len:])
            log_communication(DEBUG, "send_len = %d" % sent_len)
        total_sent += sent_len
    total_sent -= pieces * metadata_len
    log_communication(DEBUG, "%d has been sent." % (total_sent,))
    return total_sent


def recv_data(client):
    """
    receive big data from client
    :param client: client socket
    :return: int, string
    """
    total_data = ''
    tmp_size = 0
    disorder_data = dict()

    while True:
        # first get the metadata
        recv_info = client.recv(metadata_len)
        log_communication(DEBUG, "received from %s : %s" %
                          (client.getpeername(), recv_info))
        # the client closed the connection
        if len(recv_info) == 0:
            break
        while len(recv_info) < metadata_len:
            recv_info += client.recv(metadata_len - len(recv_info))
            log_communication(DEBUG, "received from %s : %s" %
                              (client.getpeername(), recv_info))
        metadata = json.loads(recv_info)
        total_size = metadata.get(TOTAL_SIZE, 0)
        if total_size == 0:
            return 0, ''
        index = metadata.get(INDEX, 0)
        data_len = metadata.get(DATA_LEN, 0)
        # then get the real data
        tmp_data = client.recv(data_len)
        log_communication(DEBUG, "received from %s : %s" %
                          (client.getpeername(), tmp_data))
        while len(tmp_data) < data_len:
            tmp_data += client.recv(data_len - len(tmp_data))
            log_communication(DEBUG, "received from %s : %s" %
                              (client.getpeername(), tmp_data))
        disorder_data[index] = tmp_data
        tmp_size += data_len

        if tmp_size == total_size:
            break

    for _, v in sorted(disorder_data.items()):
        total_data += v
    return tmp_size, total_data

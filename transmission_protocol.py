import json


class packet:
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


metadata_len = 73
packet_len = 5


class SizeIsZeroException(Exception):
    def __init__(self, msg):
        super(SizeIsZeroException, self).__init__(msg)


def file_pieces(file_size, piece_size):
    if file_size == 0:
        raise SizeIsZeroException("file_size cann't be 0.")
    if piece_size == 0:
        raise SizeIsZeroException("piece_size cann't be 0.")
    return (file_size + piece_size - 1) / piece_size


def send_data(client, data):
    """
    split big data to many packet to send
    :param client: client socket
    :param data: data to be send
    :return: 0: success; -1: excepted data
    """
    total_size = len(data)
    try:
        pieces = file_pieces(total_size, packet_len)
    except SizeIsZeroException as e:
        print e.message
        return -1
    for i in range(1, pieces + 1):
        if i == pieces:
            pack = packet(total_size, pieces, i, data[(i - 1) * packet_len:])
        else:
            pack = packet(total_size, pieces, i, data[(i - 1) * packet_len:i * packet_len])
        client.sendall(repr(pack))

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

    recv_info = client.recv(packet_len + metadata_len)
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
        recv_info = client.recv(packet_len + metadata_len)
        tmp_data = recv_info[metadata_len:]

        metadata = json.loads(recv_info[0:metadata_len])
        index = metadata.get('index', 0)
        data_len = metadata.get('data_len', 0)
        tmp_size += data_len
        disorder_data[index] = tmp_data

    for _, v in sorted(disorder_data.items()):
        total_data += v
    return total_data

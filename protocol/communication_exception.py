class DataSizeZeroException(Exception):
    def __init__(self, msg):
        super(DataSizeZeroException, self).__init__(msg)


class PieceSizeZeroException(Exception):
    def __init__(self, msg):
        super(PieceSizeZeroException, self).__init__(msg)

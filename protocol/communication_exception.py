class DataSizeZeroException(Exception):
    def __init__(self, msg):
        super(DataSizeZeroException, self).__init__(msg)


class PieceSizeZeroException(Exception):
    def __init__(self, msg):
        super(PieceSizeZeroException, self).__init__(msg)


class OutOfBoundsException(Exception):
    def __init__(self, msg):
        super(OutOfBoundsException, self).__init__(msg)

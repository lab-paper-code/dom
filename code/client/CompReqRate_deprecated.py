class CompReqRate:
    def __init__(self):
        self.origin_file_size = 0
        self.compressed_file_size = 0
        self.file_cnt = 0
        self.request_cnt = 0

    def addRequest(self):
        self.request_cnt = self.request_cnt + 1

    def addCompressedRate(self, origin_file_size, comp_file_size):
        self.origin_file_size = self.origin_file_size + origin_file_size
        self.compressed_file_size = self.compressed_file_size + comp_file_size

    def getRequest(self):
        return self.request_cnt

    def getCompressedRate(self):
        comp_rate = (self.origin_file_size - self.compressed_file_size) / self.origin_file_size * 100
        return comp_rate

    def clearCompressedRate(self):
        self.origin_file_size = 0
        self.compressed_file_size = 0

    def clearRequest(self):
        self.request_cnt = 0

    def getCompressedSize(self):
        return self.compressed_file_size

    def getOriginFileSize(self):
        return self.origin_file_size
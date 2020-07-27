import unicodecsv
from dataTypeProcessor import DataTypeProcessor

class CsvProcessor:
    def __init__(self):
        self.dtp = DataTypeProcessor()

    def read(self, filename):
        with open(filename, 'rb') as f:
            reader = unicodecsv.DictReader(f)
            return list(reader)

    def data_type_process(self, oridata, attris):
        self.dtp.process(oridata, attris)

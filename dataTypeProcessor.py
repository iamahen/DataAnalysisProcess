from datetime import datetime as dt

class DataTypeProcessor:
    def __init__(self):
        self.set_date = {'join_date', 'cancel_date', 'utc_date'}
        self.set_integer = {'days_to_cancel'}
        self.set_bool = {'is_udacity', 'is_canceled'}

    # Clean up the data types in ehrollment
    def __parse_date(self, date):
        if date == '':
            return None
        else:
            return dt.strptime(date, '%Y-%m-%d')

    def __parse_integer(self, value):
        if value == '':
            return None
        else:
            return int(value)

    def __parse_bool(self, tf):
        return tf == 'True'

    def process(self, oridata, attriset):
        for data in oridata:
            for attri in attriset:
                if attri in self.set_date:
                    data[attri] = self.__parse_date(data[attri])
                if attri in self.set_integer:
                    data[attri] = self.__parse_integer(data[attri])
                if attri in self.set_bool:
                    data[attri] = self.__parse_bool(data[attri])

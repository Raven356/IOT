from csv import reader, DictReader
import logging


class CustomReader:
    def __init__(self, filename: str):
        self.file = open(filename, "r")
        self.reader = DictReader(self.file)
        self.lines = self.countLines()
        self.cur_index = 0
        self.cur_data = next(self.reader, None)

    # def nextNotEmpty(self):
    #    while True:
    #        val = next(self.reader, None)
    #        if val or val is None:
    #            return val

    def getCurOrNext(self, i: int):
        if i == self.cur_index:
            return self.cur_data
        elif i == self.cur_index + 1:
            self.cur_data = next(self.reader, None)
            self.cur_index += 1
            return self.cur_data
        else:
            raise ValueError(
                f"Something very bad happened! Cannot get next value from csv! i: {i}, self.cur_index: {self.cur_index}"
            )

    def countLines(self):
        count = 0
        while next(self.reader, None) is not None:
            count += 1
        self.reopen()
        return count

    def reopen(self):
        self.file.seek(0)
        self.reader = DictReader(self.file)
        self.cur_index = 0

    def close(self):
        pass

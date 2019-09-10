import os
from Code.Models.data_row import DataRow

class DataSet:
    def __init__(self, file_name, path):
        self.file_name = file_name
        self.path = path
        self.rows = []

    def read_file(self):
        with open(self.path, 'r') as f:
            for line in f.read():
                self.rows.append(DataRow(line.split("\s+")))
import os
import re
import sys
import numpy as np

class DataSet:
    def __init__(self, file_name, path, dimensions):
        self.file_name = file_name
        self.path = path
        self.rows = []
        self.dimensions = dimensions
        self.read_file()

    def read_file(self):
        with open(self.path, 'r') as f:
            for line in f:
                line = line.strip()
                self.rows.append(re.split("\t+", line))

        if self.dimensions > len(self.rows[0]):
            raise Exception("Dimensions can not be more than max dimensions of dataset.")

        self.create_demeanified_matrix()
        self.create_covariance_matrix()

    def create_covariance_matrix(self):
        self.eigen_values, self.eigen_vectors = np.linalg.eig(self.get_covariance_matrix(self.float_array))
        sorted_indexes = np.flip(np.argsort(self.eigen_values))[:self.dimensions]

        
        for i, row in enumerate(self.float_array):
            coordinates = []
            for index in sorted_indexes:
                coordinates.append(np.sum(np.multiply(row, self.eigen_vectors[index])))

            self.result_array[i].append(coordinates)


    def create_demeanified_matrix(self):
        np_array = np.array(self.rows)
        self.result_array = np_array[:, -1:-2:-1].tolist()
        self.float_array = np_array[:,:-1].astype(np.float)
        means = np.mean(self.float_array, axis=0)

        self.float_array = self.float_array - np.vstack([means] * self.float_array.shape[0])

    @staticmethod
    def get_covariance_matrix(np_matrix):
        return 1 / np_matrix.shape[0] * np_matrix.T.dot(np_matrix)


def read_data(dimensions):
    path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'Data'))
    data_sets = []
    for file in os.listdir(path):
        data_sets.append(DataSet(file, os.path.join(path, file), dimensions))

    return data_sets


def main():
    try:
        dimentions = int(input("Enter the number of dimentions to reduce the datasets to:"))
        print("Now Scanning Data directory..")
        data_sets = read_data(dimentions)
        print("Data Read.")
    except Exception as ex:
        print("Something went wrong. Error: " + str(ex))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

if __name__ == '__main__':
    main()

import os
import re
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.manifold import TSNE

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

        np_array = np.array(self.rows)
        self.result_array = np_array[:, -1:-2:-1].tolist()
        self.data = np_array[:,:-1].astype(np.float)
        self.diseases = np_array[:,-1]

        self.PCA()
        self.SVD()
        self.TSNE()

    def PCA(self):
        self.create_demeanified_matrix()
        self.create_covariance_matrix()

        xcoord = []
        ycoord = []
        diseases = []

        for row in self.result_array:
            xcoord.append(row[1])
            ycoord.append(row[2])
            diseases.append(row[0])

        self.plot(np.array(xcoord, dtype=np.float64), np.array(ycoord, dtype=np.float64), self.diseases, self.file_name + " " + "PCA Plot")

    def SVD(self):
        U, D, V = np.linalg.svd(self.data)
        self.plot(U[:,0], U[:,1], self.diseases, self.file_name + " " + "SVD Plot")

    def TSNE(self):
        tsne = TSNE(n_components=2, verbose=1, perplexity=40, n_iter=500)
        result = tsne.fit_transform(self.data)

        self.plot(result[:,0], result[:,1], self.diseases, self.file_name + " " + "TSNE Plot")


    def create_covariance_matrix(self):
        self.eigen_values, self.eigen_vectors = np.linalg.eig(self.get_covariance_matrix(self.float_array))
        sorted_indexes = np.flip(np.argsort(self.eigen_values))[:self.dimensions]

        
        for i, row in enumerate(self.float_array):
            coordinates = []
            for index in sorted_indexes:
                coordinates.append(np.sum(np.multiply(row, self.eigen_vectors[index])))

            self.result_array[i].extend(coordinates)
        

    def create_demeanified_matrix(self):
        means = np.mean(self.data, axis=0)

        self.float_array = self.data - np.vstack([means] * self.data.shape[0])

    @staticmethod
    def get_covariance_matrix(np_matrix):
        return 1 / np_matrix.shape[0] * np_matrix.T.dot(np_matrix)

    @staticmethod
    def plot(xcoord, ycoord, diseases, title):
        df = pd.DataFrame({'PC1':xcoord, 'PC2':ycoord, 'Diseases': np.array(diseases)})
        lm = sns.lmplot(x='PC1', y='PC2', data=df, fit_reg=False, hue='Diseases')
        lm.fig.suptitle(title)
        plt.show()


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

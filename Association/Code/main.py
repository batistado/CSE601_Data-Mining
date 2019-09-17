import os
import re
import sys

class DataSet:
    def __init__(self, file_name, path, support):
        self.file_name = file_name
        self.path = path
        self.rows = []
        self.read_file()
        self.column_count = len(self.rows[0])
        self.transaction_count = len(self.rows)
        self.support_count = support * self.transaction_count // 100
        self.generate_freq_itemsets()

    def read_file(self):
        with open(self.path, 'r') as f:
            for line in f:
                line = line.strip()
                self.rows.append(self.transform_row(re.split("\t+", line)))

    def get_unique_items(self):
        unique_itemset = set()

        for row in self.rows:
            unique_itemset = unique_itemset.union(row)

        return [{item} for item in unique_itemset]

    @staticmethod
    def generate_next_itemset(item_sets, length):
        next_item_set = set()

        i = 0
        while i < len(item_sets):
            j = i + 1
            while j < len(item_sets):
                union_set = tuple(sorted(item_sets[i].union(item_sets[j])))
                if len(union_set) == length:
                    next_item_set.add(union_set)

                j += 1
            
            i += 1

        return [set(item) for item in next_item_set]

    def generate_freq_itemsets(self):
        self.freq_item_set = list()

        current_item_set = self.get_unique_items()

        length = 1
        while len(current_item_set) > 0:
            next_item_set = list()
            for item_set in current_item_set:
                count = 0
                for row in self.rows:
                    if len(row.intersection(item_set)) == length:
                        count += 1

                if count > self.support_count:
                    next_item_set.append(item_set)

            self.print_stats(length, len(next_item_set))
            self.freq_item_set.extend(next_item_set)
            current_item_set = self.generate_next_itemset(next_item_set, length + 1)
            length += 1

    @staticmethod
    def print_stats(length, count):
        print("number of length-{} frequent itemsets:{}".format(length, count))


    def __repr__(self):
        return str(self.rows)

        
    @staticmethod
    def transform_row(row):
        transformed_row = set()
        i = 0
        while i < len(row) - 1:
            transformed_row.add("G{}_{}".format(i, row[i]))
            i += 1

        return transformed_row

def read_data(support):
    path = "./../Data/"
    data_sets = []
    for file in os.listdir(os.path.join(os.path.abspath(path))):
        data_sets.append(DataSet(file, os.path.join(os.path.abspath(path), file), support))

    return data_sets


def main():
    try:
        support = int(input("Enter the support % required:"))
        print("Now Scanning Data directory..")
        data_sets = read_data(support)
        print("Data Read.")
    except Exception as ex:
        print("Something went wrong. Error: " + str(ex))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

if __name__ == '__main__':
    main()

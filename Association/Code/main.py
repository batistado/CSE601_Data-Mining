import os
import re
import sys

class AssociationRule:
    def __init__(self, head, body):
        self.head = head
        self.body = body

    def get_rule(self):
        return self.head.union(self.body)

    def __hash__(self):
        return hash(tuple(sorted(self.head) + sorted(self.body)))

    def __eq__(self, other):
        return sorted(self.head) == sorted(other.head) and sorted(self.body) == sorted(other.body)

    def __repr__(self):
        return "{} -> {}".format(self.head, self.body)


class DataSet:
    def __init__(self, file_name, path, support, confidence):
        self.file_name = file_name
        self.path = path
        self.rows = []
        self.read_file()
        self.column_count = len(self.rows[0])
        self.transaction_count = len(self.rows)
        self.support_count = support * self.transaction_count // 100
        self.confidence = confidence
        self.generate_freq_itemsets()
        self.generate_association_rules()

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

                if count >= self.support_count:
                    next_item_set.append(item_set)

            self.print_stats(length, len(next_item_set))
            self.freq_item_set.extend(next_item_set)
            current_item_set = self.generate_next_itemset(next_item_set, length + 1)
            length += 1

    @staticmethod
    def get_first_level_rules(item_set):
        next_level_rules = list()

        for item in item_set:
            next_level_rules.append(AssociationRule(item_set - set([item]), set([item])))

        return next_level_rules

    @staticmethod
    def generate_next_level_rules(rules, length):
        next_level_rules = list()

        i = 0
        while i < len(rules):
            j = i + 1
            while j < len(rules):
                intersection_set = rules[i].head.intersection(rules[j].head)
                if len(intersection_set) == length:
                    next_level_rules.append(AssociationRule(intersection_set, rules[i].body.union(rules[j].body)))

                j += 1

            i += 1


        return next_level_rules


    def generate_association_rules(self):
        self.association_rules = list()

        for item_set in self.freq_item_set:
            self.association_rules.append(AssociationRule(item_set, set()))
            length = len(item_set) - 1
            current_level_rules = self.get_first_level_rules(item_set)

            while len(current_level_rules) > 0:
                next_level_rules = list()
                for rule in current_level_rules:
                    total_count = head_count = 0
                    for row in self.rows:
                        if rule.head.issubset(row):
                            head_count += 1

                        if rule.get_rule().issubset(row):
                            total_count += 1


                    if total_count / head_count * 100 >= self.confidence:
                        next_level_rules.append(rule)

                
                self.association_rules.extend(next_level_rules)
                current_level_rules = self.generate_next_level_rules(next_level_rules, length - 1)
                length -= 1


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

def read_data(support, confidence):
    path = "./../Data/"
    data_sets = []
    for file in os.listdir(os.path.join(os.path.abspath(path))):
        data_sets.append(DataSet(file, os.path.join(os.path.abspath(path), file), support, confidence))

    return data_sets


def main():
    try:
        support = int(input("Enter the support % required:"))
        confidence = int(input("Enter the confidence % required:"))
        print("Now Scanning Data directory..")
        data_sets = read_data(support, confidence)
        print("Data Read.")
    except Exception as ex:
        print("Something went wrong. Error: " + str(ex))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

if __name__ == '__main__':
    main()

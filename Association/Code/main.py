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

    def template1(self, part, number, items):
        tmp = set()
        if part == "HEAD":
            tmp = self.head
        elif part == "BODY":
            tmp = self.body
        else:
            tmp = self.head.union(self.body)

        if number == "NONE":
            return len(tmp.intersection(set(items))) == 0
        elif number == "ANY":
            return len(tmp.intersection(set(items))) > 0
        else:
            return len(tmp.intersection(set(items))) == number

    def template2(self, part, count):
        tmp = set()

        if part == "HEAD":
            tmp = self.head
        elif part == "BODY":
            tmp = self.body
        else:
            tmp = self.head.union(self.body)

        return len(tmp) >= count

    def template3(self, join, *options):
        isAnd = True
        split = join.split("and")
        if len(split) == 1:
            split = join.split("or")
            isAnd = False
            
        cond1 = split[0]
        cond2 = split[1]

        i = 0
        if cond1 == '1':
            res1 = self.template1(*options[:3])
            i = 3
        else:
            res1 = self.template2(*options[:2])
            i = 2

        res2 = self.template1(*options[i:]) if cond2 == '1' else self.template2(*options[i:])

        return (res1 and res2) if isAnd else (res1 or res2)

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

        next_level_rules = list(set(next_level_rules))

        return next_level_rules


    def generate_association_rules(self):
        self.association_rules = list()

        for item_set in self.freq_item_set:
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


                    if total_count / head_count * 100 >= self.confidence and len(rule.body) > 0 and len(rule.head) > 0:
                        next_level_rules.append(rule)

                
                self.association_rules.extend(next_level_rules)
                current_level_rules = self.generate_next_level_rules(next_level_rules, length - 1)
                length -= 1

    def template1(self, part, number, items):
        result = set()

        for rule in self.association_rules:
            if rule.template1(part, number, items):
                result.add(rule)

        return list(result), len(result)

    def template2(self, part, count):
        result = set()

        for rule in self.association_rules:
            if rule.template2(part, count):
                result.add(rule)

        return list(result), len(result)

    def template3(self, *options):
        result = set()

        for rule in self.association_rules:
            if rule.template3(*options):
                result.add(rule)

        return list(result), len(result)


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

        transformed_row.add(row[i])

        return transformed_row

def read_data(support, confidence):
    path = os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'Data'))
    data_sets = []
    for file in os.listdir(path):
        data_sets.append(DataSet(file, os.path.join(path, file), support, confidence))

    return data_sets

def query(datasets):
    for dataset in datasets:
        (result11, cnt) = dataset.template1("RULE", "ANY", ['G59_Up'])
        print((result11, cnt))
        print("=======================================================")
        (result12, cnt) = dataset.template1("RULE", "NONE", ['G59_Up'])
        print((result12, cnt))
        print("=======================================================")
        (result13, cnt) = dataset.template1("RULE", 1, ['G59_Up', 'G10_Down'])
        print((result13, cnt))
        print("=======================================================")
        (result14, cnt) = dataset.template1("HEAD", "ANY", ['G59_Up'])
        print((result14, cnt))
        print("=======================================================")
        (result15, cnt) = dataset.template1("HEAD", "NONE", ['G59_Up'])
        print((result15, cnt))
        print("=======================================================")
        (result16, cnt) = dataset.template1("HEAD", 1, ['G59_Up', 'G10_Down'])
        print((result16, cnt))
        print("=======================================================")
        (result17, cnt) = dataset.template1("BODY", "ANY", ['G59_Up'])
        print((result17, cnt))
        print("=======================================================")
        (result18, cnt) = dataset.template1("BODY", "NONE", ['G59_Up'])
        print((result18, cnt))
        print("=======================================================")
        (result19, cnt) = dataset.template1("BODY", 1, ['G59_Up', 'G10_Down'])
        print((result19, cnt))
        print("=======================================================")
        (result21, cnt) = dataset.template2("RULE", 3)
        print((result21, cnt))
        print("=======================================================")
        (result22, cnt) = dataset.template2("HEAD", 2)
        print((result22, cnt))
        print("=======================================================")
        (result23, cnt) = dataset.template2("BODY", 1)
        print((result23, cnt))
        print("=======================================================")
        (result31, cnt) = dataset.template3("1or1", "HEAD", "ANY",['G10_Down'], "BODY", 1, ['G59_Up'])
        print((result31, cnt))
        print("=======================================================")
        (result32, cnt) = dataset.template3("1and1", "HEAD", "ANY",['G10_Down'], "BODY", 1, ['G59_Up'])
        print((result32, cnt))
        print("=======================================================")
        (result33, cnt) = dataset.template3("1or2", "HEAD", "ANY",['G10_Down'], "BODY", 2)
        print((result33, cnt))
        print("=======================================================")
        (result34, cnt) = dataset.template3("1and2", "HEAD", "ANY",['G10_Down'], "BODY", 2)
        print((result34, cnt))
        print("=======================================================")
        (result35, cnt) = dataset.template3("2or2", "HEAD", 1, "BODY", 2)
        print((result35, cnt))
        print("=======================================================")
        (result36, cnt) = dataset.template3("2and2", "HEAD", 1, "BODY", 2)
        print((result36, cnt))
        print("=======================================================")
    



def main():
    try:
        support = int(input("Enter the support % required:"))
        confidence = int(input("Enter the confidence % required:"))
        print("Now Scanning Data directory..")
        data_sets = read_data(support, confidence)
        print("Data Read.")
        query(data_sets)
    except Exception as ex:
        print("Something went wrong. Error: " + str(ex))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)

if __name__ == '__main__':
    main()

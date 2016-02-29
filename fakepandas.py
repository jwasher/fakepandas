import operator
def num_rows(d):
    'Get number of data rows. Raise ValueError if they are inconsistent.'
    if len(d) == 0:
        return
    def gen_columns():
        for v in d.values():
            yield v
    columns = gen_columns()
    length = len(next(columns))
    for index, column in enumerate(columns, 1):
        if len(column) != length:
            raise ValueError(index)
    return length

def logical_and(a, b):
    return a and b

def logical_or(a, b):
    return a or b

class Conjunction:
    def __init__(self, left, right, combine):
        self.left = left
        self.right = right
        self.combine = combine
    def apply(self, data, index):
        return self.combine(self.left.apply(data, index), self.right.apply(data, index))

class Comparison:
    def __init__(self, lookup, value, operate):
        self.lookup = lookup
        self.value = value
        self.operate = operate
    def apply(self, data, index):
        other_value = self.lookup(data, index)
        return self.operate(other_value, self.value)
    def __and__(self, other):
        return Conjunction(self, other, logical_and)
    def __or__(self, other):
        return Conjunction(self, other, logical_or)

class SimpleComparison(Comparison):
    def __init__(self, label, value, operate):
        def lookup(data, index):
            return data[label][index]
        super().__init__(lookup, value, operate)
    
class LabelReference:
    def __init__(self, label):
        self.label = label
    def __lt__(self, value):
        return SimpleComparison(self.label, value, operator.lt)
    def __gt__(self, value):
        return SimpleComparison(self.label, value, operator.gt)
    def __ge__(self, value):
        return SimpleComparison(self.label, value, operator.ge)
    def __le__(self, value):
        return SimpleComparison(self.label, value, operator.le)
    def __eq__(self, value):
        return SimpleComparison(self.label, value, operator.eq)
    def __add__(self, other):
        return PairedLabelReference(self, other, operator.add)
    def __sub__(self, other):
        return PairedLabelReference(self, other, operator.sub)

class PairedLabelReference(LabelReference):
    def __init__(self, first, second, operate):
        self.first = first
        self.second = second
        self.operate = operate
    def lookup(self, data, index):
        first_value = data[self.first.label][index]
        second_value = data[self.second.label][index]
        return self.operate(first_value, second_value)
    def __lt__(self, value):
        return Comparison(self.lookup, value, operator.lt)
    def __ge__(self, value):
        return Comparison(self.lookup, value, operator.ge)

class Dataset:
    def __init__(self, data: dict):
        self.data = data
        self.length = num_rows(data)
        self.labels = sorted(data.keys())

    def __str__(self):
        def row(index):
            return '\t'.join([
                str(self.data[label][index])
                for label in self.labels])
        header = '\t'.join(self.labels) + '\n'
        return header + '\n'.join([
            row(index) for index in range(self.length)])

    def __getattr__(self, label):
        if label not in self.data:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, label))
        return LabelReference(label)

    def __getitem__(self, comparison):
        filtered_data = dict((label, []) for label in self.labels)
        def append_row(index):
            for label in self.labels:
                filtered_data[label].append(self.data[label][index])
        for index in range(self.length):
            if comparison.apply(self.data, index):
                append_row(index)
        return Dataset(filtered_data)

    def pprint(self):
        print(self.pprint_str())

    def pprint_str(self):
        # helpers
        def width_of(label):
            width = max(len(str(value)) for value in self.data[label])
            width = max([width, len(str(label))])
            return width
        def format(value, label):
            return '{value:>{width}}'.format(value=str(value), width=field_widths[label])

        # precompute
        field_widths = {label: width_of(label) for label in self.labels}
        table_width = sum(width for width in field_widths.values()) + 3 * (len(self.labels)-1) + 4
        HR = '-' * table_width

        # render lines
        labels_line = '| ' + ' | '.join(format(label, label) for label in self.labels) + ' |'
        lines = [
            HR,
            labels_line,
            HR,
        ]
        for index in range(self.length):
            formatted_values = (format(self.data[label][index], label) for label in self.labels)
            lines.append('| ' + ' | '.join(formatted_values) + ' |')
        lines.append(HR)
        return '\n'.join(lines)
        


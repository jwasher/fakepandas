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
    def apply(self, data, row_number):
        return self.combine(self.left.apply(data, row_number), self.right.apply(data, row_number))

class GeneralComparison:
    def __init__(self, lookup, value, operate):
        self.lookup = lookup
        self.value = value
        self.operate = operate
    def apply(self, data, row_number):
        other_value = self.lookup(data, row_number)
        return self.operate(other_value, self.value)
    def __and__(self, other):
        return Conjunction(self, other, logical_and)
    def __or__(self, other):
        return Conjunction(self, other, logical_or)

class Comparison(GeneralComparison):
    def __init__(self, label: str, value, operate):
        def lookup(data, row_number):
            return data[label][row_number]
        super().__init__(lookup, value, operate)
    
class LabelReference:
    def __init__(self, label: str):
        self.label = label
    def __lt__(self, value):
        return Comparison(self.label, value, operator.lt)
    def __gt__(self, value):
        return Comparison(self.label, value, operator.gt)
    def __ge__(self, value):
        return Comparison(self.label, value, operator.ge)
    def __le__(self, value):
        return Comparison(self.label, value, operator.le)
    def __eq__(self, value):
        return Comparison(self.label, value, operator.eq)
    def __add__(self, other):
        return PairedLabelReference(self, other, operator.add)
    def __sub__(self, other):
        return PairedLabelReference(self, other, operator.sub)
    def __mod__(self, other):
        return PairedLabelReference(self, other, operator.mod)

class PairedLabelReference(LabelReference):
    def __init__(self, first, second, operate):
        self.first = first
        self.second = second
        self.operate = operate
    def lookup(self, data, row_number):
        first_value = data[self.first.label][row_number]
        if isinstance(self.second, LabelReference):
            second_value = data[self.second.label][row_number]
        else:
            second_value = self.second
        return self.operate(first_value, second_value)
    def __lt__(self, value):
        return GeneralComparison(self.lookup, value, operator.lt)
    def __le__(self, value):
        return GeneralComparison(self.lookup, value, operator.le)
    def __ge__(self, value):
        return GeneralComparison(self.lookup, value, operator.ge)
    def __gt__(self, value):
        return GeneralComparison(self.lookup, value, operator.gt)
    def __eq__(self, value):
        return GeneralComparison(self.lookup, value, operator.eq)

class Dataset:
    def __init__(self, data: dict):
        self.data = data
        self.length = num_rows(data)
        self.labels = sorted(data.keys())

    def __getattr__(self, label):
        if label not in self.data:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, label))
        return LabelReference(label)

    def __getitem__(self, comparison):
        filtered_data = dict((label, []) for label in self.labels)
        def append_row(row_number):
            for label in self.labels:
                filtered_data[label].append(self.data[label][row_number])
        for row_number in range(self.length):
            if comparison.apply(self.data, row_number):
                append_row(row_number)
        return Dataset(filtered_data)

    # presentation/rendering methods
    def __str__(self):
        def row(row_number):
            return '\t'.join([
                str(self.data[label][row_number])
                for label in self.labels])
        header = '\t'.join(self.labels) + '\n'
        return header + '\n'.join([
            row(row_number) for row_number in range(self.length)])

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
        for row_number in range(self.length):
            formatted_values = (format(self.data[label][row_number], label) for label in self.labels)
            lines.append('| ' + ' | '.join(formatted_values) + ' |')
        lines.append(HR)
        return '\n'.join(lines)
        


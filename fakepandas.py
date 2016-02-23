import operator
def _validate(d):
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

class Comparison:
    operate = None
    def __init__(self, label, value):
        self.label = label
        self.value = value
    def apply(self, data, index):
        other_value = data[self.label][index]
        return self.operate(other_value, self.value)
    def __and__(self, other):
        return AndConjunction(self, other)
    def __or__(self, other):
        return OrConjunction(self, other)

class LessThanComparison(Comparison):
    operate = operator.lt

class GreaterThanComparison(Comparison):
    operate = operator.gt

class GreaterThanEqualsComparison(Comparison):
    operate = operator.ge

class LessThanEqualsComparison(Comparison):
    operate = operator.le

class EqualsComparison(Comparison):
    operate = operator.eq

class AndConjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def apply(self, data, index):
        return self.left.apply(data, index) and self.right.apply(data, index)

class OrConjunction:
    def __init__(self, left, right):
        self.left = left
        self.right = right
    def apply(self, data, index):
        return self.left.apply(data, index) or self.right.apply(data, index)

class LabelReference:
    def __init__(self, label):
        self.label = label
    def __lt__(self, value):
        return LessThanComparison(self.label, value)
    def __gt__(self, value):
        return GreaterThanComparison(self.label, value)
    def __ge__(self, value):
        return GreaterThanEqualsComparison(self.label, value)
    def __le__(self, value):
        return LessThanEqualsComparison(self.label, value)
    def __eq__(self, value):
        return EqualsComparison(self.label, value)

class Dataset:
    def __init__(self, data: dict):
        self.data = data
        self.length = _validate(data)
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
        


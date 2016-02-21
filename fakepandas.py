import itertools
def _validate(d):
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
    def __init__(self, label, value):
        self.label = label
        self.value = value
    
class LessThanComparison(Comparison):
    def apply(self, other):
        return other < self.value
        
class GreaterThanComparison(Comparison):
    def apply(self, other):
        return other > self.value

class LabelReference:
    def __init__(self, label):
        self.label = label
    def __lt__(self, value):
        return LessThanComparison(self.label, value)
    def __gt__(self, value):
        return GreaterThanComparison(self.label, value)
    def filter(self, row):
        pass

class Dataset:
    def __init__(self, values: dict):
        self.values = values
        self.length = _validate(values)
        self.labels = sorted(values.keys())

    def __str__(self):
        header = '\t'.join(self.labels) + '\n'
        def row(index):
            return '\t'.join([
                str(self.values[label][index])
                for label in self.labels])
        return header + '\n'.join([
            row(index) for index in range(self.length)])

    def __getattr__(self, label):
        if label not in self.values:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, label))
        return LabelReference(label)

    def __getitem__(self, comparison: LessThanComparison):
        data = dict((label, []) for label in self.labels)
        def append_row(index):
            for label in self.labels:
                data[label].append(self.values[label][index])
        for index in range(self.length):
            value = self.values[comparison.label][index]
            if value < comparison.value:
                append_row(index)
        return Dataset(data)

    def pprint(self):
        print(self.pprint_str())

    def pprint_str(self):
        # helpers
        def width_of(label):
            width = max(len(str(value)) for value in self.values[label])
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
            formatted_values = (format(self.values[label][index], label) for label in self.labels)
            lines.append('| ' + ' | '.join(formatted_values) + ' |')
        lines.append(HR)
        return '\n'.join(lines)
        


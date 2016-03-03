import operator

def num_rows(d):
    'Get number of data rows. Raise ValueError if they are inconsistent.'
    if len(d) == 0:
        return 0
    def gen_columns():
        for v in d.values():
            yield v
    columns = gen_columns()
    length = len(next(columns))
    for index, column in enumerate(columns, 1):
        if len(column) != length:
            raise ValueError(index)
    return length

# The operator module does not provide functions for the logical "and"
# and "or" operators, only the bitwise "&" and "|". So we make our own
# functions for the logicals.
def logical_and(a, b):
    return a and b

def logical_or(a, b):
    return a or b

class GeneralComparison:
    '''
    A generic representation of a comparison.

    Used when comparing two columns to each other (i.e., two LabelReferences).
    '''
    def __init__(self, lookup, value, operate):
        self.lookup = lookup
        self.value = value
        self.operate = operate
    def apply(self, data, row_number):
        other_value = self.lookup(data, row_number)
        return self.operate(other_value, self.value)
    # __and__ is actually bitwise and ("a & b"), not logical and ("a
    # and b").  Unfortunately, no current version of Python provides a
    # magic method for logical and.  Thus, we have little choice but
    # to fake it using bitwise and.
    def __and__(self, other):
        return Conjunction(self, other, logical_and)
    # The situation with __or__ is exactly analogous.
    def __or__(self, other):
        return Conjunction(self, other, logical_or)

class Comparison(GeneralComparison):
    '''
    Simplified form of comparison.

    Used when comparing a column (LabelReference) to a constant value.
    '''
    def __init__(self, label: str, value, operate):
        def lookup(data, row_number):
            return data[label][row_number]
        super().__init__(lookup, value, operate)

class Conjunction:
    '''
    Represents a logical "and" or "or" relationship between two expressions.

    combine will generally be set to either logical_and or logical_or.
    '''
    def __init__(self, left: GeneralComparison, right: GeneralComparison, combine: 'func'):
        self.left = left
        self.right = right
        self.combine = combine
    def apply(self, data: dict, row_number: int):
        return self.combine(self.left.apply(data, row_number), self.right.apply(data, row_number))
    
class LabelReference:
    '''
    Represents a labeled column in a Dataset.
    '''
    def __init__(self, label: str):
        self.label = label
    def compare(self, value, operate):
        return Comparison(self.label, value, operate)
    def __lt__(self, value):
        return self.compare(value, operator.lt)
    def __gt__(self, value):
        return self.compare(value, operator.gt)
    def __ge__(self, value):
        return self.compare(value, operator.ge)
    def __le__(self, value):
        return self.compare(value, operator.le)
    def __eq__(self, value):
        return self.compare(value, operator.eq)
    def __add__(self, other):
        return PairedLabelReference(self, other, operator.add)
    def __sub__(self, other):
        return PairedLabelReference(self, other, operator.sub)
    def __mod__(self, other):
        return PairedLabelReference(self, other, operator.mod)

class PairedLabelReference(LabelReference):
    '''
    Represents two separate columns in some comparision relation to each other.
    '''
    def __init__(self, first: LabelReference, second: LabelReference, operate: 'func'):
        self.first = first
        self.second = second
        self.operate = operate
    def lookup(self, data: dict, row_number: int):
        first_value = data[self.first.label][row_number]
        if isinstance(self.second, LabelReference):
            second_value = data[self.second.label][row_number]
        else:
            second_value = self.second
        return self.operate(first_value, second_value)
    def compare(self, value, operate: 'func'):
        return GeneralComparison(self.lookup, value, operate)

class Dataset:
    '''
    Core class representing a set of data.

    Filter rows with obj[expression].
    '''
    def __init__(self, data: dict):
        self.data = data
        self.length = num_rows(data)
        self.labels = sorted(data.keys())

    def __getattr__(self, label: str):
        if label not in self.data:
            raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, label))
        return LabelReference(label)

    def __getitem__(self, comparison: GeneralComparison):
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

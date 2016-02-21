from fakepandas import Dataset
import unittest

dataset1 = Dataset({
    'A': [-1, 2, -3, 4, 5],
    'B': [10, 11, 12, 13, 14],
    'C': [3, 6, 9, 12, 15],
})

dataset2 = Dataset({
    'A': [-137, 22, -3, 4, 5],
    'B': [10, 11, 121, 13, 14],
    'C': [3, 6, 91, 12, 15],
})
class TestDataset(unittest.TestCase):
    maxDiff = None
    def test_str(self):
        as_str = '''A	B	C
-1	10	3
2	11	6
-3	12	9
4	13	12
5	14	15'''
        self.assertEqual(as_str, str(dataset1))

    def test_pprint(self):
        dataset1_pprint = '''----------------
|  A |  B |  C |
----------------
| -1 | 10 |  3 |
|  2 | 11 |  6 |
| -3 | 12 |  9 |
|  4 | 13 | 12 |
|  5 | 14 | 15 |
----------------'''
        self.assertEqual(dataset1_pprint, str(dataset1.pprint_str()))

        dataset2_pprint = '''-------------------
|    A |   B |  C |
-------------------
| -137 |  10 |  3 |
|   22 |  11 |  6 |
|   -3 | 121 | 91 |
|    4 |  13 | 12 |
|    5 |  14 | 15 |
-------------------'''
        self.assertEqual(dataset2_pprint, str(dataset2.pprint_str()))

    def test_filter(self):
        d = dataset1[dataset1.A < 0]
        as_str = '''A	B	C
-1	10	3
-3	12	9'''
        self.assertEqual(as_str, str(d))
        
        d = dataset1[dataset1.A > 0]
        as_str = '''A	B	C
2	11	6
4	13	12
5	14	15'''
        self.assertEqual(as_str, str(d))
        
        d = dataset1[dataset1.B >= 12]
        as_str = '''A	B	C
-3	12	9
4	13	12
5	14	15'''
        self.assertEqual(as_str, str(d))

        d = dataset1[dataset1.B <= 12]
        as_str = '''A	B	C
-1	10	3
2	11	6
-3	12	9'''
        self.assertEqual(as_str, str(d))

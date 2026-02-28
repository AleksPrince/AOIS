import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.binary_processor import BinaryProcessor


class TestBinaryProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()

    def test_create_zero_array(self):
        arr = self.processor.create_zero_array()
        self.assertEqual(len(arr), 32)
        self.assertEqual(sum(arr), 0)

    def test_add_binary_arrays_simple(self):
        a = [0]*31 + [1]
        b = [0]*31 + [1]
        res = self.processor.add_binary_arrays(a,b)
        self.assertEqual(res[-2:], [1,0])

    def test_add_binary_arrays_carry(self):
        a = [0]*30 + [1,1]
        b = [0]*31 + [1]
        res = self.processor.add_binary_arrays(a,b)
        self.assertEqual(res[-3:], [1,0,0])

    def test_add_binary_arrays_overflow(self):
        a = [1]*32
        b = [0]*31 + [1]
        res = self.processor.add_binary_arrays(a,b)
        self.assertEqual(len(res), 32)

    def test_invert_bits(self):
        arr = [1,0,1] + [0]*29
        inv = self.processor.invert_bits(arr)
        self.assertEqual(inv[1], 1)
        self.assertEqual(inv[2], 0)
        self.assertEqual(inv[0], 1)  # знаковый не меняется

    def test_invert_bits_start_from_0(self):
        arr = [1,0,1] + [0]*29
        inv = self.processor.invert_bits(arr, start_from=0)
        self.assertEqual(inv[0], 0)  # знаковый тоже инвертируется

    def test_get_binary_one(self):
        one = self.processor.get_binary_one()
        self.assertEqual(one[-1], 1)
        self.assertEqual(sum(one[:-1]), 0)

    def test_binary_to_decimal_unsigned(self):
        self.assertEqual(self.processor.binary_to_decimal_unsigned([1,0,1]), 5)
        self.assertEqual(self.processor.binary_to_decimal_unsigned([0]), 0)


if __name__ == '__main__':
    unittest.main()
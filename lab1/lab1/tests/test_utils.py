import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils import BinaryArrayUtils, NumberConverter


class TestBinaryArrayUtils(unittest.TestCase):
    def setUp(self):
        self.utils = BinaryArrayUtils()

    def test_create_zero_array(self):
        arr = self.utils.create_zero_array()
        self.assertEqual(len(arr), 32)
        self.assertEqual(arr, [0]*32)

    def test_format_binary(self):
        arr = [1]*32
        fmt = self.utils.format_binary(arr)
        self.assertIsInstance(fmt, str)

    def test_format_binary_short(self):
        arr = [1,0,1]
        fmt = self.utils.format_binary(arr)
        self.assertEqual(fmt, "101")

    def test_format_binary_group_size(self):
        arr = [1]*16
        fmt = self.utils.format_binary(arr, group_size=4)
        self.assertIn(' ', fmt)

    def test_format_binary_short_custom(self):
        arr = [1,0,1]
        fmt = self.utils.format_binary(arr, group_size=2)
        self.assertEqual(fmt, "101")

    def test_validate_binary_array_valid(self):
        arr = [0]*32
        try:
            self.utils.validate_binary_array(arr)
        except ValueError:
            self.fail("validate_binary_array raised ValueError")

    def test_validate_binary_array_invalid_length(self):
        with self.assertRaises(ValueError):
            self.utils.validate_binary_array([0]*10)

    def test_validate_binary_array_invalid_bits(self):
        with self.assertRaises(ValueError):
            self.utils.validate_binary_array([0,1,2] + [0]*29)

    def test_print_binary_with_analysis(self):
        arr = [0]*16 + [1]*16
        try:
            self.utils.print_binary_with_analysis(arr, "Test")
        except:
            self.fail("print_binary_with_analysis raised exception")


class TestNumberConverter(unittest.TestCase):
    def setUp(self):
        self.converter = NumberConverter()

    def test_integer_to_binary_array_zero(self):
        self.assertEqual(self.converter.integer_to_binary_array(0), [0])

    def test_integer_to_binary_array_positive(self):
        self.assertEqual(self.converter.integer_to_binary_array(42), [1,0,1,0,1,0])

    def test_binary_array_to_integer(self):
        self.assertEqual(self.converter.binary_array_to_integer([1,0,1]), 5)

    def test_binary_array_to_integer_with_offset(self):
        self.assertEqual(self.converter.binary_array_to_integer([0,0,1,0,1], 2), 5)

    def test_fraction_to_binary_zero(self):
        self.assertEqual(self.converter.fraction_to_binary(0), [])

    def test_fraction_to_binary(self):
        self.assertEqual(self.converter.fraction_to_binary(0.5), [1])
        self.assertEqual(self.converter.fraction_to_binary(0.25), [0,1])
        self.assertEqual(self.converter.fraction_to_binary(0.75), [1,1])

    def test_fraction_to_binary_max_bits(self):
        res = self.converter.fraction_to_binary(0.1, max_bits=5)
        self.assertEqual(len(res), 5)

    def test_binary_fraction_to_decimal(self):
        self.assertAlmostEqual(self.converter.binary_fraction_to_decimal([1]), 0.5)
        self.assertAlmostEqual(self.converter.binary_fraction_to_decimal([0,1]), 0.25)
        self.assertAlmostEqual(self.converter.binary_fraction_to_decimal([1,0,1]), 0.625)


if __name__ == '__main__':
    unittest.main()
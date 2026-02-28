import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.binary_processor import BinaryProcessor
from src.bcd_operations import BCD8421Converter, BCDArithmetic


class TestBCD8421Converter(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()
        self.converter = BCD8421Converter(self.processor)

    def test_single_digit(self):
        for d in range(10):
            bcd = self.converter.decimal_to_bcd(d)
            self.assertEqual(self.converter.bcd_to_decimal(bcd), d)

    def test_multiple_digits(self):
        val = 123
        bcd = self.converter.decimal_to_bcd(val)
        self.assertEqual(self.converter.bcd_to_decimal(bcd), val)

    def test_zero(self):
        bcd = self.converter.decimal_to_bcd(0)
        self.assertEqual(self.converter.bcd_to_decimal(bcd), 0)

    def test_max_digits(self):
        val = 12345678
        bcd = self.converter.decimal_to_bcd(val)
        self.assertEqual(self.converter.bcd_to_decimal(bcd), val)

    def test_negative_error(self):
        with self.assertRaises(ValueError):
            self.converter.decimal_to_bcd(-1)

    def test_too_large_error(self):
        with self.assertRaises(ValueError):
            self.converter.decimal_to_bcd(123456789)

    def test_get_bcd_digit(self):
        bcd = self.converter.decimal_to_bcd(1234)
        self.assertEqual(self.converter._get_bcd_digit(bcd, 0), 4)
        self.assertEqual(self.converter._get_bcd_digit(bcd, 1), 3)

    def test_set_bcd_digit(self):
        bcd = self.processor.create_zero_array()
        self.converter._set_bcd_digit(bcd, 0, 5)
        self.assertEqual(self.converter._get_bcd_digit(bcd, 0), 5)

    def test_set_bcd_digit_invalid(self):
        bcd = self.processor.create_zero_array()
        with self.assertRaises(ValueError):
            self.converter._set_bcd_digit(bcd, 0, 10)


class TestBCDArithmetic(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()
        self.converter = BCD8421Converter(self.processor)
        self.arithmetic = BCDArithmetic(self.processor, self.converter)

    def test_add_no_carry(self):
        res = self.arithmetic.add(123, 456)
        self.assertEqual(res['result_decimal'], 579)

    def test_add_with_carry(self):
        res = self.arithmetic.add(5, 6)
        self.assertEqual(res['result_decimal'], 11)
        res = self.arithmetic.add(99, 1)
        self.assertEqual(res['result_decimal'], 100)

    def test_add_commutative(self):
        res1 = self.arithmetic.add(12, 34)['result_decimal']
        res2 = self.arithmetic.add(34, 12)['result_decimal']
        self.assertEqual(res1, res2)

    def test_binary_representation(self):
        res = self.arithmetic.add(12, 34)
        self.assertEqual(len(res['result_binary']), 32)
        for bit in res['result_binary']:
            self.assertIn(bit, [0,1])


if __name__ == '__main__':
    unittest.main()
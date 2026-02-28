import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.binary_processor import BinaryProcessor
from src.integer_operations import IntegerCodeConverter, IntegerArithmetic


class TestIntegerCodeConverter(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()
        self.converter = IntegerCodeConverter(self.processor)

    def test_direct_code_positive(self):
        code = self.converter.get_direct_code(42)
        self.assertEqual(code[0], 0)
        self.assertEqual(code[-6:], [1,0,1,0,1,0])

    def test_direct_code_negative(self):
        code = self.converter.get_direct_code(-42)
        self.assertEqual(code[0], 1)

    def test_reverse_code_positive(self):
        rev = self.converter.get_reverse_code(42)
        direct = self.converter.get_direct_code(42)
        self.assertEqual(rev, direct)

    def test_reverse_code_negative(self):
        rev = self.converter.get_reverse_code(-42)
        direct = self.converter.get_direct_code(-42)
        self.assertNotEqual(rev, direct)

    def test_additional_code_positive(self):
        add = self.converter.get_additional_code(42)
        direct = self.converter.get_direct_code(42)
        self.assertEqual(add, direct)

    def test_additional_code_negative(self):
        add = self.converter.get_additional_code(-42)
        recovered = self.converter.additional_to_decimal(add)
        self.assertEqual(recovered, -42)

    def test_additional_to_decimal(self):
        for num in [0, 1, -1, 42, -42, 127, -128]:
            add = self.converter.get_additional_code(num)
            self.assertEqual(self.converter.additional_to_decimal(add), num)

    def test_get_all_codes(self):
        codes = self.converter.get_all_codes(-42)
        self.assertEqual(len(codes), 4)
        self.assertIn('direct', codes)


class TestIntegerArithmetic(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()
        self.converter = IntegerCodeConverter(self.processor)
        self.arithmetic = IntegerArithmetic(self.processor, self.converter)

    def test_addition_basic(self):
        cases = [(25,13,38), (25,-13,12), (-25,13,-12), (-25,-13,-38)]
        for a,b,exp in cases:
            res = self.arithmetic.add_in_additional_code(a,b)
            self.assertEqual(res['result_decimal'], exp)

    def test_addition_with_zero(self):
        res = self.arithmetic.add_in_additional_code(42,0)
        self.assertEqual(res['result_decimal'], 42)
        res = self.arithmetic.add_in_additional_code(0,42)
        self.assertEqual(res['result_decimal'], 42)

    def test_addition_overflow(self):
        res = self.arithmetic.add_in_additional_code(2147483647, 1)
        self.assertEqual(res['result_decimal'], -2147483648)

    def test_subtraction(self):
        res = self.arithmetic.subtract_in_additional_code(30,12)
        self.assertEqual(res['result_decimal'], 18)
        res = self.arithmetic.subtract_in_additional_code(30,-12)
        self.assertEqual(res['result_decimal'], 42)

    def test_binary_add_private(self):
        # Тестируем вспомогательный метод _binary_add
        res = self.arithmetic._binary_add([1,0], [1])
        self.assertEqual(res, [1,1])
        res = self.arithmetic._binary_add([1,1,1], [1])
        self.assertEqual(res, [1,0,0,0])
        res = self.arithmetic._binary_add([1,0,1], [1,0])
        self.assertEqual(res, [1,1,1])
        res = self.arithmetic._binary_add([1,0,1,0], [1,1])
        self.assertEqual(res, [1,1,0,1])

    def test_binary_to_decimal(self):
        self.assertEqual(self.arithmetic._binary_to_decimal([1,0,1]), 5)
        self.assertEqual(self.arithmetic._binary_to_decimal([1,1,1,1]), 15)

    def test_multiplication(self):
        res = self.arithmetic.multiply_in_direct_code(7,6)
        self.assertEqual(res['result_decimal'], 42)
        res = self.arithmetic.multiply_in_direct_code(-7,6)
        self.assertEqual(res['result_decimal'], -42)
        res = self.arithmetic.multiply_in_direct_code(7,-6)
        self.assertEqual(res['result_decimal'], -42)
        res = self.arithmetic.multiply_in_direct_code(-7,-6)
        self.assertEqual(res['result_decimal'], 42)

    def test_multiplication_zero(self):
        res = self.arithmetic.multiply_in_direct_code(0,42)
        self.assertEqual(res['result_decimal'], 0)
        res = self.arithmetic.multiply_in_direct_code(42,0)
        self.assertEqual(res['result_decimal'], 0)

    def test_division(self):
        res = self.arithmetic.divide_in_direct_code(100,7,5)
        self.assertAlmostEqual(res['result_decimal'], 100/7, places=4)

    def test_division_signs(self):
        res = self.arithmetic.divide_in_direct_code(-100,7,5)
        self.assertAlmostEqual(res['result_decimal'], -100/7, places=4)
        res = self.arithmetic.divide_in_direct_code(100,-7,5)
        self.assertAlmostEqual(res['result_decimal'], -100/7, places=4)
        res = self.arithmetic.divide_in_direct_code(-100,-7,5)
        self.assertAlmostEqual(res['result_decimal'], 100/7, places=4)

    def test_division_zero_dividend(self):
        res = self.arithmetic.divide_in_direct_code(0,42,5)
        self.assertEqual(res['result_decimal'], 0)

    def test_division_by_zero(self):
        with self.assertRaises(ValueError):
            self.arithmetic.divide_in_direct_code(10,0,5)

    def test_to_binary_with_prefix(self):
        s = self.arithmetic._to_binary_with_prefix(42)
        self.assertIsInstance(s, str)
        s = self.arithmetic._to_binary_with_prefix(0)
        self.assertEqual(s, "[0]")


if __name__ == '__main__':
    unittest.main()
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.binary_processor import BinaryProcessor
from src.float_operations import IEEE754Converter, FloatArithmetic


class TestIEEE754Converter(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()
        self.converter = IEEE754Converter(self.processor)

    def test_zero(self):
        ieee = self.converter.float_to_ieee754(0)
        recovered = self.converter.ieee754_to_float(ieee)
        self.assertAlmostEqual(recovered, 0, places=5)

    def test_positive(self):
        ieee = self.converter.float_to_ieee754(12.375)
        recovered = self.converter.ieee754_to_float(ieee)
        self.assertAlmostEqual(recovered, 12.375, delta=0.0001)

    def test_negative(self):
        ieee = self.converter.float_to_ieee754(-12.375)
        recovered = self.converter.ieee754_to_float(ieee)
        self.assertAlmostEqual(recovered, -12.375, delta=0.0001)

    def test_sign_bit(self):
        ieee = self.converter.float_to_ieee754(1.0)
        self.assertEqual(ieee[0], 0)
        ieee = self.converter.float_to_ieee754(-1.0)
        self.assertEqual(ieee[0], 1)

    def test_normalization(self):
        exp, norm = self.converter._normalize_number(12.375)
        self.assertGreaterEqual(norm, 1.0)
        self.assertLess(norm, 2.0)

    def test_mantissa_bits(self):
        bits = self.converter._get_mantissa_bits(0.5)
        self.assertEqual(len(bits), 23)
        self.assertEqual(bits[0], 1)

    def test_build_ieee754_array(self):
        arr = self.converter._build_ieee754_array(0, 127, [0]*23)
        self.assertEqual(len(arr), 32)
        self.assertEqual(arr[1:9], [0,1,1,1,1,1,1,1])


class TestFloatArithmetic(unittest.TestCase):
    def setUp(self):
        self.processor = BinaryProcessor()
        self.converter = IEEE754Converter(self.processor)
        self.arithmetic = FloatArithmetic(self.processor, self.converter)

    def test_add(self):
        res = self.arithmetic.add(12.375, 5.25)
        self.assertAlmostEqual(res['result_decimal'], 17.625, delta=0.0001)

    def test_sub(self):
        res = self.arithmetic.subtract(12.375, 5.25)
        self.assertAlmostEqual(res['result_decimal'], 7.125, delta=0.0001)

    def test_mul(self):
        res = self.arithmetic.multiply(12.375, 5.25)
        self.assertAlmostEqual(res['result_decimal'], 64.96875, delta=0.0001)

    def test_div(self):
        res = self.arithmetic.divide(12.375, 5.25)
        self.assertAlmostEqual(res['result_decimal'], 12.375/5.25, delta=0.0001)

    def test_div_by_zero(self):
        with self.assertRaises(ValueError):
            self.arithmetic.divide(1,0)


if __name__ == '__main__':
    unittest.main()
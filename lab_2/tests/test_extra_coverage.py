"""Дополнительные тесты для повышения покрытия до 90%"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.logic_function import LogicFunction
from core.expression_processor import ExpressionProcessor
from operations.derivative_calculator import DerivativeCalculator
from operations.numeric_converter import NumericConverter
from operations.fictitious_detector import FictitiousDetector
from minimization.glue_minimizer import GlueMinimizer
from minimization.table_minimizer import TableMinimizer
from minimization.karnaugh_minimizer import KarnaughMinimizer
from utils.term_processor import TermProcessor


class TestExtraCoverage(unittest.TestCase):
    """Дополнительные тесты для слабых мест"""

    def setUp(self):
        self.p = ExpressionProcessor()

    # ========== ДЛЯ NUMERIC CONVERTER (было 77%) ==========

    def test_numeric_constant_0(self):
        f = LogicFunction("0", self.p)
        c = NumericConverter()
        sdnf, sknf = c.convert_to_numeric(f)
        self.assertEqual(sdnf, "∨()")
        self.assertEqual(sknf, "∧(все)")

    def test_numeric_constant_1(self):
        f = LogicFunction("1", self.p)
        c = NumericConverter()
        sdnf, sknf = c.convert_to_numeric(f)
        self.assertEqual(sdnf, "∨(все)")
        self.assertEqual(sknf, "∧()")

    # ========== ДЛЯ DERIVATIVE CALCULATOR (было 61%) ==========

    def test_derivative_constant(self):
        f = LogicFunction("0", self.p)
        d = DerivativeCalculator()
        deriv = d.partial_derivative(f, 'a')
        self.assertIsInstance(deriv, str)

    def test_derivative_xor(self):
        f = LogicFunction("a~!b", self.p)
        d = DerivativeCalculator()
        deriv = d.partial_derivative(f, 'a')
        self.assertIsInstance(deriv, str)

    def test_derivative_3var(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        d = DerivativeCalculator()
        all_d = d.all_derivatives(f)
        self.assertEqual(len(all_d), 7)  # 3 + 3 + 1

    # ========== ДЛЯ FICTITIOUS DETECTOR (было 82%) ==========

    def test_fictitious_with_constant(self):
        f = LogicFunction("a&(b|!b)", self.p)
        d = FictitiousDetector()
        fict = d.find_fictitious(f)
        self.assertIn('b', fict)

    def test_fictitious_5var(self):
        f = LogicFunction("a&b&c&d&e", self.p)
        d = FictitiousDetector()
        self.assertEqual(d.find_fictitious(f), [])

    # ========== ДЛЯ GLUE MINIMIZER (было 88%) ==========

    def test_glue_minimizer_5var(self):
        f = LogicFunction("(a&b)|(c&d&e)", self.p)
        m = GlueMinimizer()
        minimized, _ = m.minimize(f)
        self.assertIn("a&b", minimized)

    def test_glue_minimizer_xor(self):
        f = LogicFunction("a~!b", self.p)
        m = GlueMinimizer()
        minimized, _ = m.minimize(f)
        self.assertIsInstance(minimized, str)

    # ========== ДЛЯ TABLE MINIMIZER (было 87%) ==========

    def test_table_minimizer_5var(self):
        f = LogicFunction("(a&b)|(c&d&e)", self.p)
        m = TableMinimizer()
        minimized, _, _ = m.minimize(f)
        self.assertIn("a&b", minimized)

    def test_table_minimizer_tautology(self):
        f = LogicFunction("a|!a", self.p)
        m = TableMinimizer()
        minimized, _, _ = m.minimize(f)
        self.assertEqual(minimized, "1")

    # ========== ДЛЯ KARNAUGH MINIMIZER (было 64%) ==========

    def test_karnaugh_2var_xor(self):
        f = LogicFunction("a~!b", self.p)
        m = KarnaughMinimizer()
        minimized, _ = m.minimize(f)
        self.assertIsInstance(minimized, str)

    def test_karnaugh_3var_all_cases(self):
        # Все клетки 1
        f = LogicFunction("1", self.p)
        m = KarnaughMinimizer()
        minimized, _ = m.minimize(f)
        self.assertEqual(minimized, "1")

        # Все клетки 0
        f = LogicFunction("0", self.p)
        minimized, _ = m.minimize(f)
        self.assertEqual(minimized, "0")

    def test_karnaugh_4var_majority(self):
        f = LogicFunction("(a&b)|(a&c)|(a&d)|(b&c)|(b&d)|(c&d)", self.p)
        m = KarnaughMinimizer()
        minimized, _ = m.minimize(f)
        self.assertIsInstance(minimized, str)

    def test_karnaugh_5var_simple(self):
        f = LogicFunction("(a&b)|(c&d&e)", self.p)
        m = KarnaughMinimizer()
        minimized, _ = m.minimize(f)
        self.assertIn("a&b", minimized)

    # ========== ДЛЯ TERM PROCESSOR (было 73%) ==========

    def test_term_processor_edge_cases(self):
        tp = TermProcessor()

        # Пустые списки
        self.assertEqual(tp.join_literals([], '&'), '')

        # Одиночные литералы
        self.assertEqual(tp.join_literals(['a'], '&'), 'a')

        # ДНФ с пробелами
        terms = tp.extract_dnf_terms("a&b | c&d")
        self.assertEqual(len(terms), 2)

        # КНФ с пробелами
        terms = tp.extract_cnf_terms("(a|b) & (c|d)")
        self.assertEqual(len(terms), 2)


if __name__ == "__main__":
    unittest.main()
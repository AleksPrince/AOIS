#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Минимальные, но полные юнит-тесты для анализатора булевых функций.
Запуск: python tests_minimal.py
Или с coverage: coverage run tests_minimal.py && coverage report -m
"""

import unittest
import sys
import os

# Явно добавляем текущую папку в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# --- Импорт проверяемых модулей ---
try:
    from core.expression_processor import ExpressionProcessor
    from core.logic_function import LogicFunction
    from core.truth_matrix import TruthMatrix
    from operations.normal_forms_builder import NormalFormsBuilder
    from operations.numeric_converter import NumericConverter
    from operations.post_checker import PostClassesChecker
    from operations.polynomial_builder import ZhegalkinBuilder
    from operations.fictitious_detector import FictitiousDetector
    from operations.derivative_calculator import DerivativeCalculator
    from minimization.glue_minimizer import GlueMinimizer
    from minimization.table_minimizer import TableMinimizer
    from minimization.karnaugh_minimizer import KarnaughMinimizer
    from utils.term_processor import TermProcessor
    from utils.expression_validator import ExpressionValidator
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Ошибка импорта: {e}")
    print("Убедитесь, что структура папок проекта сохранена, и вы запускаете тест из корневой директории проекта.")
    MODULES_AVAILABLE = False


# ====================== ТЕСТЫ ======================
@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestExpressionValidator(unittest.TestCase):
    def setUp(self):
        self.v = ExpressionValidator()

    def test_valid(self):
        self.assertTrue(self.v.is_valid("a&b"))
        self.assertTrue(self.v.is_valid("!(!a->!b)|c"))
        self.assertTrue(self.v.is_valid("0"))

    def test_invalid(self):
        self.assertFalse(self.v.is_valid("a&"))
        self.assertFalse(self.v.is_valid("(a&b"))

    def test_get_vars(self):
        self.assertEqual(self.v.get_variables("a&b"), ['a', 'b'])


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestExpressionProcessor(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_constants(self):
        self.assertEqual(self.p.evaluate("0", {}), 0)
        self.assertEqual(self.p.evaluate("1", {}), 1)

    def test_ops(self):
        self.assertEqual(self.p.evaluate("a&b", {'a':1,'b':1}), 1)
        self.assertEqual(self.p.evaluate("a|b", {'a':0,'b':1}), 1)
        self.assertEqual(self.p.evaluate("!a", {'a':1}), 0)
        self.assertEqual(self.p.evaluate("a->b", {'a':1,'b':0}), 0)
        self.assertEqual(self.p.evaluate("a~b", {'a':1,'b':0}), 0)

    def test_complex(self):
        self.assertEqual(self.p.evaluate("!(!a->!b)|c", {'a':0,'b':1,'c':0}), 1)


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestTruthMatrix(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_and(self):
        tm = TruthMatrix(['a','b'], "a&b", self.p)
        self.assertEqual(len(tm), 4)
        self.assertEqual(tm.get_sets_where_one(), [(1,1)])
        self.assertEqual(tm.get_indices_where_one(), [3])


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestLogicFunction(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_create(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(set(f.variables), {'a','b'})
        self.assertEqual(f.get_variable_count(), 2)

    def test_const(self):
        f = LogicFunction("0", self.p)
        self.assertEqual(f.variables, [])

    def test_truth(self):
        f = LogicFunction("a&b", self.p)
        for bits,res in f.truth_matrix:
            if bits == (1,1): self.assertEqual(res,1)
            else: self.assertEqual(res,0)


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestNormalFormsBuilder(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.b = NormalFormsBuilder(TermProcessor())

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        sdnf,_ = self.b.build(f)
        self.assertIn("a&b", sdnf)

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        sdnf,_ = self.b.build(f)
        self.assertEqual(len(sdnf.split(' ∨ ')), 5)


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestNumericConverter(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.c = NumericConverter()

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        sdnf_num, _ = self.c.convert_to_numeric(f)
        self.assertEqual(sdnf_num, '∨(3)')

    def test_index(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        self.assertEqual(self.c.get_index_representation(f), '(0,1,1,1,0,1,0,1)_2 = 117_10')


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestPostChecker(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.checker = PostClassesChecker()

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertTrue(self.checker.is_t0(f))
        self.assertTrue(self.checker.is_t1(f))
        self.assertFalse(self.checker.is_self_dual(f))

    def test_not(self):
        f = LogicFunction("!a", self.p)
        self.assertTrue(self.checker.is_self_dual(f))


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestZhegalkin(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.b = ZhegalkinBuilder()

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertIn("&", self.b.build(f))

    def test_or(self):
        f = LogicFunction("a|b", self.p)
        self.assertEqual(len(self.b.build(f).split(' ⊕ ')), 3)


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestFictitious(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.d = FictitiousDetector()

    def test_tautology(self):
        f = LogicFunction("a|!a", self.p)
        self.assertIn('a', self.d.find_fictitious(f))

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(self.d.find_fictitious(f), [])


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestDerivatives(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.c = DerivativeCalculator()

    def test_partial(self):
        f = LogicFunction("a&b", self.p)
        self.assertIsInstance(self.c.partial_derivative(f,'a'), str)

    def test_mixed(self):
        f = LogicFunction("a&b", self.p)
        self.assertIsInstance(self.c.mixed_derivative(f,['a','b']), str)


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestMinimizers(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_glue(self):
        m = GlueMinimizer()
        f = LogicFunction("(a&b)|(a&!b)", self.p)
        self.assertEqual(m.minimize(f)[0], "a")

    def test_table(self):
        m = TableMinimizer()
        f = LogicFunction("(a&b)|(a&!b)", self.p)
        self.assertEqual(m.minimize(f)[0], "a")

    def test_karnaugh(self):
        m = KarnaughMinimizer()
        f = LogicFunction("a&b", self.p)
        self.assertIsInstance(m.minimize(f)[0], str)


@unittest.skipIf(not MODULES_AVAILABLE, "Модули проекта не найдены")
class TestTermProcessor(unittest.TestCase):
    def setUp(self):
        self.tp = TermProcessor()

    def test_split(self):
        self.assertEqual(self.tp.split_into_literals("a&b&c"), ['a','b','c'])

    def test_join(self):
        self.assertEqual(self.tp.join_literals(['a','b'], '&'), '(a&b)')


# ====================== ЗАПУСК ======================
if __name__ == "__main__":
    print("Запуск тестов анализатора булевых функций...")
    unittest.main(verbosity=2)
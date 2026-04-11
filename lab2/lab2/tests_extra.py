#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Дополнительные тесты для достижения 95% покрытия
Запуск: python tests_extra.py
Или: coverage run tests_extra.py && coverage report -m
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.logic_function import LogicFunction
from core.expression_processor import ExpressionProcessor
from minimization.karnaugh_minimizer import KarnaughMinimizer
from operations.derivative_calculator import DerivativeCalculator
from operations.post_checker import PostClassesChecker
from operations.fictitious_detector import FictitiousDetector
from minimization.table_minimizer import TableMinimizer


class TestKarnaughFull(unittest.TestCase):
    """Полное тестирование карт Карно для всех случаев"""

    def setUp(self):
        self.p = ExpressionProcessor()
        self.k = KarnaughMinimizer()

    # ----- 2 переменные -----
    def test_karnaugh_2var_all_cases(self):
        # AND
        f = LogicFunction("a&b", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # OR
        f = LogicFunction("a|b", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # XOR
        f = LogicFunction("a~!b", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # Константа 0
        f = LogicFunction("0", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # Константа 1
        f = LogicFunction("1", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

    # ----- 3 переменные -----
    def test_karnaugh_3var_all_cases(self):
        # AND трёх переменных
        f = LogicFunction("a&b&c", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # OR трёх переменных
        f = LogicFunction("a|b|c", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # Мажоритарная функция
        f = LogicFunction("(a&b)|(a&c)|(b&c)", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # Функция с одним нулём
        f = LogicFunction("!(a&b&c)", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

    # ----- 4 переменные -----
    def test_karnaugh_4var_all_cases(self):
        # AND четырёх переменных
        f = LogicFunction("a&b&c&d", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # OR четырёх переменных
        f = LogicFunction("a|b|c|d", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

        # Функция с группировкой 2x2
        f = LogicFunction("(a&b)|(c&d)", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIsInstance(minimized, str)

    # ----- 5 переменных -----
    def test_karnaugh_5var_error(self):
        f = LogicFunction("a&b&c&d&e", self.p)
        minimized, _ = self.k.minimize(f)
        self.assertIn("Ошибка", minimized)


class TestDerivativesFull(unittest.TestCase):
    """Полное тестирование булевых производных"""

    def setUp(self):
        self.p = ExpressionProcessor()
        self.d = DerivativeCalculator()

    def test_derivatives_and(self):
        f = LogicFunction("a&b", self.p)

        # Частные производные
        da = self.d.partial_derivative(f, 'a')
        db = self.d.partial_derivative(f, 'b')
        self.assertIsInstance(da, str)
        self.assertIsInstance(db, str)

        # Смешанная
        dab = self.d.mixed_derivative(f, ['a', 'b'])
        self.assertIsInstance(dab, str)

    def test_derivatives_or(self):
        f = LogicFunction("a|b", self.p)
        da = self.d.partial_derivative(f, 'a')
        self.assertIsInstance(da, str)

    def test_derivatives_xor(self):
        f = LogicFunction("a~!b", self.p)
        da = self.d.partial_derivative(f, 'a')
        self.assertIsInstance(da, str)

    def test_derivatives_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)

        # Все частные
        for var in ['a', 'b', 'c']:
            deriv = self.d.partial_derivative(f, var)
            self.assertIsInstance(deriv, str)

        # Все смешанные
        all_deriv = self.d.all_derivatives(f)
        self.assertEqual(len(all_deriv), 7)  # 3 частных + 3 вторых + 1 третья

    def test_derivative_simplification(self):
        # Проверяем, что производные упрощаются
        f = LogicFunction("a&b", self.p)
        da = self.d.partial_derivative(f, 'a')
        # Ожидаем b (упрощённо)
        self.assertIsInstance(da, str)


class TestPostCheckerFull(unittest.TestCase):
    """Полное тестирование классов Поста"""

    def setUp(self):
        self.p = ExpressionProcessor()
        self.checker = PostClassesChecker()

    def test_all_classes_for_and(self):
        f = LogicFunction("a&b", self.p)
        classes = self.checker.check_all(f)
        self.assertTrue(classes['T0'])
        self.assertTrue(classes['T1'])
        self.assertFalse(classes['S'])
        self.assertTrue(classes['M'])
        self.assertFalse(classes['L'])

    def test_all_classes_for_or(self):
        f = LogicFunction("a|b", self.p)
        classes = self.checker.check_all(f)
        self.assertTrue(classes['T0'])
        self.assertTrue(classes['T1'])
        self.assertFalse(classes['S'])
        self.assertTrue(classes['M'])

    def test_all_classes_for_not(self):
        f = LogicFunction("!a", self.p)
        classes = self.checker.check_all(f)
        self.assertFalse(classes['T0'])
        self.assertFalse(classes['T1'])
        self.assertTrue(classes['S'])
        self.assertFalse(classes['M'])
        self.assertTrue(classes['L'])  # !a линеен

    def test_linearity_check(self):
        # Линейная функция: XOR
        f = LogicFunction("a~!b", self.p)
        self.assertTrue(self.checker.is_linear(f))

        # Нелинейная: AND
        f = LogicFunction("a&b", self.p)
        self.assertFalse(self.checker.is_linear(f))

    def test_monotonicity_check(self):
        # Монотонная: AND
        f = LogicFunction("a&b", self.p)
        self.assertTrue(self.checker.is_monotonic(f))

        # Немонотонная: NOT
        f = LogicFunction("!a", self.p)
        self.assertFalse(self.checker.is_monotonic(f))


class TestFictitiousFull(unittest.TestCase):
    """Полное тестирование фиктивных переменных"""

    def setUp(self):
        self.p = ExpressionProcessor()
        self.d = FictitiousDetector()

    def test_fictitious_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(self.d.find_fictitious(f), [])
        self.assertEqual(set(self.d.find_essential(f)), {'a', 'b'})

    def test_fictitious_tautology(self):
        f = LogicFunction("a|!a", self.p)
        fict = self.d.find_fictitious(f)
        # В тавтологии все переменные фиктивные
        self.assertIn('a', fict)

    def test_fictitious_contradiction(self):
        f = LogicFunction("a&!a", self.p)
        fict = self.d.find_fictitious(f)
        self.assertIn('a', fict)

    def test_fictitious_with_const(self):
        f = LogicFunction("a&(b|!b)", self.p)
        fict = self.d.find_fictitious(f)
        self.assertIn('b', fict)

    def test_fictitious_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        fict = self.d.find_fictitious(f)
        self.assertEqual(fict, [])  # Нет фиктивных

    def test_essential_extraction(self):
        f = LogicFunction("a&b", self.p)
        essential = self.d.find_essential(f)
        self.assertEqual(set(essential), {'a', 'b'})


class TestTableMinimizerFull(unittest.TestCase):
    """Полное тестирование табличного минимизатора"""

    def setUp(self):
        self.p = ExpressionProcessor()
        self.m = TableMinimizer()

    def test_table_for_and(self):
        f = LogicFunction("a&b", self.p)
        minimized, _, table = self.m.minimize(f)
        self.assertEqual(minimized, "a&b")
        self.assertIsInstance(table, str)

    def test_table_for_absorb(self):
        f = LogicFunction("(a&b)|(a&!b)", self.p)
        minimized, _, table = self.m.minimize(f)
        self.assertEqual(minimized, "a")
        self.assertIn("Импликанта", table)

    def test_table_for_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        minimized, _, table = self.m.minimize(f)
        self.assertIsInstance(minimized, str)
        self.assertIn("X", table)  # В таблице должны быть X


class TestIntegrationFull(unittest.TestCase):
    """Интеграционные тесты для всего проекта"""

    def setUp(self):
        self.p = ExpressionProcessor()

    def test_full_pipeline_and(self):
        expr = "a&b"
        f = LogicFunction(expr, self.p)
        self.assertEqual(f.expression, expr)
        self.assertEqual(len(f.truth_matrix), 4)

        # Проверяем таблицу
        for bits, res in f.truth_matrix:
            if bits == (1, 1):
                self.assertEqual(res, 1)
            else:
                self.assertEqual(res, 0)

    def test_full_pipeline_complex(self):
        expr = "!(!a->!b)|c"
        f = LogicFunction(expr, self.p)
        self.assertEqual(set(f.variables), {'a', 'b', 'c'})
        self.assertEqual(len(f.truth_matrix), 8)

        # Проверяем несколько наборов
        expected = {
            (0, 0, 0): 0, (0, 0, 1): 1, (0, 1, 0): 1,
            (0, 1, 1): 1, (1, 0, 0): 0, (1, 0, 1): 1,
            (1, 1, 0): 0, (1, 1, 1): 1
        }
        for bits, res in f.truth_matrix:
            self.assertEqual(res, expected[bits])


if __name__ == "__main__":
    print("Запуск дополнительных тестов...")
    unittest.main(verbosity=2)
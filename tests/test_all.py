"""Полный набор тестов для анализатора булевых функций (покрытие 90%+)"""

import unittest
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

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


# ==================== ТЕСТЫ ВАЛИДАТОРА ====================

class TestExpressionValidator(unittest.TestCase):
    def setUp(self):
        self.v = ExpressionValidator()

    def test_valid_expressions(self):
        valid = [
            "0", "1", "a", "b", "c", "d", "e",
            "a&b", "a|b", "!a", "a->b", "a~b",
            "(a&b)", "a&b&c", "a|b|c", "(a&b)|c",
            "!(!a->!b)|c", "a->b->c", "!a&!b&!c",
        ]
        for expr in valid:
            self.assertTrue(self.v.is_valid(expr), f"Должно быть валидно: {expr}")

    def test_invalid_expressions(self):
        invalid = [
                "", " ", "a&", "&a", "a|", "|a",
                "(a&b", "a&b)", "a&x", "a&&b", "a||b", "()",
            ]
        for expr in invalid:
            self.assertFalse(self.v.is_valid(expr), f"Должно быть невалидно: {expr}")

    def test_get_variables(self):
        self.assertEqual(self.v.get_variables("a&b"), ['a', 'b'])
        self.assertEqual(self.v.get_variables("!a&!b&!c"), ['a', 'b', 'c'])
        self.assertEqual(self.v.get_variables("(a&b)|(!c&d)"), ['a', 'b', 'c', 'd'])
        self.assertEqual(self.v.get_variables("0"), [])
        self.assertEqual(self.v.get_variables("1"), [])


# ==================== ТЕСТЫ ПРОЦЕССОРА ====================

class TestExpressionProcessor(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_constants(self):
        self.assertEqual(self.p.evaluate("0", {}), 0)
        self.assertEqual(self.p.evaluate("1", {}), 1)

    def test_variables(self):
        self.assertEqual(self.p.evaluate("a", {'a': 0}), 0)
        self.assertEqual(self.p.evaluate("a", {'a': 1}), 1)

    def test_not(self):
        self.assertEqual(self.p.evaluate("!a", {'a': 0}), 1)
        self.assertEqual(self.p.evaluate("!a", {'a': 1}), 0)
        self.assertEqual(self.p.evaluate("!!a", {'a': 0}), 0)

    def test_and(self):
        self.assertEqual(self.p.evaluate("a&b", {'a': 0, 'b': 0}), 0)
        self.assertEqual(self.p.evaluate("a&b", {'a': 0, 'b': 1}), 0)
        self.assertEqual(self.p.evaluate("a&b", {'a': 1, 'b': 0}), 0)
        self.assertEqual(self.p.evaluate("a&b", {'a': 1, 'b': 1}), 1)

    def test_or(self):
        self.assertEqual(self.p.evaluate("a|b", {'a': 0, 'b': 0}), 0)
        self.assertEqual(self.p.evaluate("a|b", {'a': 0, 'b': 1}), 1)
        self.assertEqual(self.p.evaluate("a|b", {'a': 1, 'b': 0}), 1)
        self.assertEqual(self.p.evaluate("a|b", {'a': 1, 'b': 1}), 1)

    def test_implication(self):
        self.assertEqual(self.p.evaluate("a->b", {'a': 0, 'b': 0}), 1)
        self.assertEqual(self.p.evaluate("a->b", {'a': 0, 'b': 1}), 1)
        self.assertEqual(self.p.evaluate("a->b", {'a': 1, 'b': 0}), 0)
        self.assertEqual(self.p.evaluate("a->b", {'a': 1, 'b': 1}), 1)

    def test_equivalence(self):
        self.assertEqual(self.p.evaluate("a~b", {'a': 0, 'b': 0}), 1)
        self.assertEqual(self.p.evaluate("a~b", {'a': 0, 'b': 1}), 0)
        self.assertEqual(self.p.evaluate("a~b", {'a': 1, 'b': 0}), 0)
        self.assertEqual(self.p.evaluate("a~b", {'a': 1, 'b': 1}), 1)

    def test_complex(self):
        # !(!a->!b)|c
        test_cases = [
            ((0, 0, 0), 0), ((0, 0, 1), 1), ((0, 1, 0), 1),
            ((0, 1, 1), 1), ((1, 0, 0), 0), ((1, 0, 1), 1),
            ((1, 1, 0), 0), ((1, 1, 1), 1),
        ]
        for (a, b, c), expected in test_cases:
            result = self.p.evaluate("!(!a->!b)|c", {'a': a, 'b': b, 'c': c})
            self.assertEqual(result, expected)


# ==================== ТЕСТЫ ТАБЛИЦЫ ИСТИННОСТИ ====================

class TestTruthMatrix(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_constant_0(self):
        tm = TruthMatrix([], "0", self.p)
        self.assertEqual(len(tm), 1)
        self.assertEqual(tm.get_result_column(), [0])

    def test_constant_1(self):
        tm = TruthMatrix([], "1", self.p)
        self.assertEqual(len(tm), 1)
        self.assertEqual(tm.get_result_column(), [1])

    def test_one_variable(self):
        tm = TruthMatrix(['a'], "a", self.p)
        self.assertEqual(len(tm), 2)
        self.assertEqual(tm.get_sets_where_one(), [(1,)])
        self.assertEqual(tm.get_indices_where_one(), [1])

    def test_two_variables_and(self):
        tm = TruthMatrix(['a', 'b'], "a&b", self.p)
        self.assertEqual(len(tm), 4)
        self.assertEqual(tm.get_sets_where_one(), [(1, 1)])

    def test_get_value(self):
        tm = TruthMatrix(['a', 'b'], "a&b", self.p)
        self.assertEqual(tm.get_value((1, 1)), 1)
        with self.assertRaises(ValueError):
            tm.get_value((1, 1, 1))

    def test_iteration(self):
        tm = TruthMatrix(['a'], "a", self.p)
        rows = list(tm)
        self.assertEqual(len(rows), 2)


# ==================== ТЕСТЫ ЛОГИЧЕСКОЙ ФУНКЦИИ ====================

class TestLogicFunction(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_constant_0(self):
        f = LogicFunction("0", self.p)
        self.assertEqual(f.expression, "0")
        self.assertEqual(f.variables, [])
        self.assertEqual(f.get_variable_count(), 0)

    def test_constant_1(self):
        f = LogicFunction("1", self.p)
        self.assertEqual(f.expression, "1")

    def test_single_variable(self):
        f = LogicFunction("a", self.p)
        self.assertEqual(f.variables, ['a'])
        self.assertTrue(f.has_variables())

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(set(f.variables), {'a', 'b'})

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        self.assertEqual(set(f.variables), {'a', 'b', 'c'})
        self.assertEqual(len(f.truth_matrix), 8)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            LogicFunction("a&", self.p)


# ==================== ТЕСТЫ СДНФ/СКНФ ====================

class TestNormalForms(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.tp = TermProcessor()
        self.b = NormalFormsBuilder(self.tp)

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        sdnf, sknf = self.b.build(f)
        self.assertIn("a&b", sdnf)

    def test_or(self):
        f = LogicFunction("a|b", self.p)
        sdnf, _ = self.b.build(f)
        self.assertEqual(len(sdnf.split(' ∨ ')), 3)

    def test_not(self):
        f = LogicFunction("!a", self.p)
        sdnf, _ = self.b.build(f)
        self.assertIn("!a", sdnf)

    def test_tautology(self):
        f = LogicFunction("a|!a", self.p)
        sdnf, sknf = self.b.build(f)
        self.assertNotEqual(sdnf, '0')
        self.assertEqual(sknf, '1')

    def test_contradiction(self):
        f = LogicFunction("a&!a", self.p)
        sdnf, sknf = self.b.build(f)
        self.assertEqual(sdnf, '0')
        self.assertNotEqual(sknf, '1')

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        sdnf, _ = self.b.build(f)
        self.assertEqual(len(sdnf.split(' ∨ ')), 5)


# ==================== ТЕСТЫ ЧИСЛОВЫХ ФОРМ ====================

class TestNumericConverter(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.c = NumericConverter()

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        sdnf_num, sknf_num = self.c.convert_to_numeric(f)
        self.assertEqual(sdnf_num, '∨(3)')
        self.assertEqual(sknf_num, '∧(0,1,2)')

    def test_or(self):
        f = LogicFunction("a|b", self.p)
        sdnf_num, sknf_num = self.c.convert_to_numeric(f)
        self.assertEqual(sdnf_num, '∨(1,2,3)')
        self.assertEqual(sknf_num, '∧(0)')

    def test_not(self):
        f = LogicFunction("!a", self.p)
        sdnf_num, sknf_num = self.c.convert_to_numeric(f)
        self.assertEqual(sdnf_num, '∨(0)')
        self.assertEqual(sknf_num, '∧(1)')

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        sdnf_num, sknf_num = self.c.convert_to_numeric(f)
        self.assertEqual(sdnf_num, '∨(1,2,3,5,7)')
        self.assertEqual(sknf_num, '∧(0,4,6)')

    def test_index_form(self):
        f = LogicFunction("a&b", self.p)
        index = self.c.get_index_representation(f)
        self.assertEqual(index, '(0,0,0,1)_2 = 1_10')


# ==================== ТЕСТЫ КЛАССОВ ПОСТА ====================

class TestPostChecker(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.checker = PostClassesChecker()

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertTrue(self.checker.is_t0(f))
        self.assertTrue(self.checker.is_t1(f))
        self.assertFalse(self.checker.is_self_dual(f))
        self.assertTrue(self.checker.is_monotonic(f))

    def test_or(self):
        f = LogicFunction("a|b", self.p)
        self.assertTrue(self.checker.is_t0(f))
        self.assertTrue(self.checker.is_t1(f))

    def test_not(self):
        f = LogicFunction("!a", self.p)
        self.assertFalse(self.checker.is_t0(f))
        self.assertFalse(self.checker.is_t1(f))
        self.assertTrue(self.checker.is_self_dual(f))

    def test_constant_0(self):
        f = LogicFunction("0", self.p)
        self.assertTrue(self.checker.is_t0(f))
        self.assertFalse(self.checker.is_t1(f))

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        classes = self.checker.check_all(f)
        self.assertTrue(classes['T0'])
        self.assertTrue(classes['T1'])
        self.assertFalse(classes['S'])
        self.assertFalse(classes['M'])


# ==================== ТЕСТЫ ПОЛИНОМА ЖЕГАЛКИНА ====================

class TestZhegalkin(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.b = ZhegalkinBuilder()

    def test_constant_0(self):
        f = LogicFunction("0", self.p)
        self.assertEqual(self.b.build(f), "0")

    def test_constant_1(self):
        f = LogicFunction("1", self.p)
        self.assertEqual(self.b.build(f), "1")

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        poly = self.b.build(f)
        self.assertIn("a&b", poly)

    def test_or(self):
        f = LogicFunction("a|b", self.p)
        poly = self.b.build(f)
        self.assertEqual(len(poly.split(' ⊕ ')), 3)

    def test_not(self):
        f = LogicFunction("!a", self.p)
        poly = self.b.build(f)
        self.assertIn("1", poly)

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        poly = self.b.build(f)
        self.assertIsInstance(poly, str)


# ==================== ТЕСТЫ ФИКТИВНЫХ ПЕРЕМЕННЫХ ====================

class TestFictitiousDetector(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.d = FictitiousDetector()

    def test_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(self.d.find_fictitious(f), [])
        self.assertEqual(set(self.d.find_essential(f)), {'a', 'b'})

    def test_tautology(self):
        f = LogicFunction("a|!a", self.p)
        fict = self.d.find_fictitious(f)
        self.assertIsInstance(fict, list)

    def test_contradiction(self):
        f = LogicFunction("a&!a", self.p)
        fict = self.d.find_fictitious(f)
        self.assertIsInstance(fict, list)

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        self.assertEqual(self.d.find_fictitious(f), [])


# ==================== ТЕСТЫ ПРОИЗВОДНЫХ ====================

class TestDerivatives(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.c = DerivativeCalculator()

    def test_partial_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertIsInstance(self.c.partial_derivative(f, 'a'), str)

    def test_mixed_and(self):
        f = LogicFunction("a&b", self.p)
        self.assertIsInstance(self.c.mixed_derivative(f, ['a', 'b']), str)

    def test_partial_or(self):
        f = LogicFunction("a|b", self.p)
        self.assertIsInstance(self.c.partial_derivative(f, 'a'), str)

    def test_invalid_variable(self):
        f = LogicFunction("a&b", self.p)
        with self.assertRaises(ValueError):
            self.c.partial_derivative(f, 'x')

    def test_empty_vars(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(self.c.mixed_derivative(f, []), f.expression)

    def test_all_derivatives(self):
        f = LogicFunction("a&b", self.p)
        derivs = self.c.all_derivatives(f)
        self.assertIn('∂F/∂a', derivs)
        self.assertIn('∂F/∂b', derivs)


# ==================== ТЕСТЫ МИНИМИЗАЦИИ ====================

class TestGlueMinimizer(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.m = GlueMinimizer()

    def test_constant_0(self):
        f = LogicFunction("0", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertEqual(minimized, "0")

    def test_constant_1(self):
        f = LogicFunction("1", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertEqual(minimized, "1")

    def test_absorb(self):
        f = LogicFunction("(a&b)|(a&!b)", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertEqual(minimized, "a")

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertIn("c", minimized)


class TestTableMinimizer(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.m = TableMinimizer()

    def test_constant(self):
        f = LogicFunction("0", self.p)
        minimized, _, _ = self.m.minimize(f)
        self.assertEqual(minimized, "0")

    def test_absorb(self):
        f = LogicFunction("(a&b)|(a&!b)", self.p)
        minimized, _, _ = self.m.minimize(f)
        self.assertEqual(minimized, "a")

    def test_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        minimized, _, _ = self.m.minimize(f)
        self.assertIsInstance(minimized, str)


class TestKarnaughMinimizer(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()
        self.m = KarnaughMinimizer()

    def test_2var_and(self):
        f = LogicFunction("a&b", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertIsInstance(minimized, str)

    def test_2var_or(self):
        f = LogicFunction("a|b", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertIsInstance(minimized, str)

    def test_3var_and(self):
        f = LogicFunction("a&b&c", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertIsInstance(minimized, str)

    def test_3var_complex(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertIsInstance(minimized, str)

    def test_4var_and(self):
        f = LogicFunction("a&b&c&d", self.p)
        minimized, _ = self.m.minimize(f)
        self.assertIsInstance(minimized, str)


# ==================== ТЕСТЫ ОБРАБОТЧИКА ТЕРМОВ ====================

class TestTermProcessor(unittest.TestCase):
    def setUp(self):
        self.tp = TermProcessor()

    def test_split_and(self):
        self.assertEqual(self.tp.split_into_literals("a&b&c"), ['a', 'b', 'c'])

    def test_split_or(self):
        self.assertEqual(self.tp.split_into_literals("a|b|c"), ['a', 'b', 'c'])

    def test_extract_dnf(self):
        terms = self.tp.extract_dnf_terms("a&b ∨ c&d")
        self.assertEqual(len(terms), 2)

    def test_extract_cnf(self):
        terms = self.tp.extract_cnf_terms("(a|b) ∧ (c|d)")
        self.assertEqual(len(terms), 2)

    def test_join(self):
        self.assertEqual(self.tp.join_literals(['a', 'b'], '&'), '(a&b)')
        self.assertEqual(self.tp.join_literals(['a'], '&'), 'a')


# ==================== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ====================

class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.p = ExpressionProcessor()

    def test_and_full(self):
        f = LogicFunction("a&b", self.p)
        self.assertEqual(f.expression, "a&b")
        self.assertEqual(len(f.truth_matrix), 4)
        for bits, res in f.truth_matrix:
            if bits == (1, 1):
                self.assertEqual(res, 1)

    def test_complex_full(self):
        f = LogicFunction("!(!a->!b)|c", self.p)
        expected = {
            (0, 0, 0): 0, (0, 0, 1): 1, (0, 1, 0): 1,
            (0, 1, 1): 1, (1, 0, 0): 0, (1, 0, 1): 1,
            (1, 1, 0): 0, (1, 1, 1): 1
        }
        for bits, res in f.truth_matrix:
            self.assertEqual(res, expected[bits])


# ==================== ЗАПУСК ====================

def run_all_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestExpressionValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestExpressionProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestTruthMatrix))
    suite.addTests(loader.loadTestsFromTestCase(TestLogicFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestNormalForms))
    suite.addTests(loader.loadTestsFromTestCase(TestNumericConverter))
    suite.addTests(loader.loadTestsFromTestCase(TestPostChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestZhegalkin))
    suite.addTests(loader.loadTestsFromTestCase(TestFictitiousDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestDerivatives))
    suite.addTests(loader.loadTestsFromTestCase(TestGlueMinimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestTableMinimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestKarnaughMinimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestTermProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print(f"Запущено тестов: {result.testsRun}")
    print(f"Успешно: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Ошибок: {len(result.errors)}")
    print(f="Падений: {len(result.failures)}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
"""Главный класс анализатора"""

from typing import Optional
from tabulate import tabulate

from core.logic_function import LogicFunction
from core.expression_processor import ExpressionProcessor
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


class BooleanAnalyzer:
    """Главный анализатор булевых функций"""

    def __init__(self):
        self.processor = ExpressionProcessor()
        self.validator = ExpressionValidator()
        self.term_proc = TermProcessor()

        self.form_builder = NormalFormsBuilder(self.term_proc)
        self.numeric_converter = NumericConverter()
        self.post_checker = PostClassesChecker()
        self.poly_builder = ZhegalkinBuilder()
        self.fictitious_detector = FictitiousDetector()
        self.derivative_calc = DerivativeCalculator()

        self.glue_minimizer = GlueMinimizer()
        self.table_minimizer = TableMinimizer()
        self.karnaugh_minimizer = KarnaughMinimizer()

        self.current_func: Optional[LogicFunction] = None

    def analyze(self, expression: str) -> None:
        try:
            if not self.validator.is_valid(expression):
                print(f"ОШИБКА: Некорректное выражение '{expression}'")
                return

            self.current_func = LogicFunction(expression, self.processor)
            self._print_header()
            self._print_truth_table()
            self._print_normal_forms()
            self._print_numeric_forms()
            self._print_post_classes()
            self._print_zhegalkin()
            self._print_fictitious_vars()
            self._print_derivatives()
            self._print_minimization()
            self._print_footer()
        except Exception as e:
            print(f"ОШИБКА: {e}")

    def _print_header(self):
        print("\n" + "=" * 80)
        print(f" АНАЛИЗ ФУНКЦИИ: {self.current_func.expression}")
        print("=" * 80)

    def _print_footer(self):
        print("=" * 80)

    def _print_truth_table(self):
        print("\n 1. ТАБЛИЦА ИСТИННОСТИ")
        print("-" * 50)
        f = self.current_func
        if not f.has_variables():
            print(f"  Константа: F = {f.expression}")
            return
        headers = list(f.variables) + ['F']
        data = [list(bits) + [res] for bits, res in f.truth_matrix]
        print(tabulate(data, headers=headers, tablefmt='grid'))

    def _print_normal_forms(self):
        print("\n 2. СОВЕРШЕННЫЕ НОРМАЛЬНЫЕ ФОРМЫ")
        print("-" * 50)
        sdnf, sknf = self.form_builder.build(self.current_func)
        print(f"  СДНФ: {sdnf}")
        print(f"  СКНФ: {sknf}")

    def _print_numeric_forms(self):
        print("\n 3. ЧИСЛОВЫЕ ФОРМЫ")
        print("-" * 50)
        sdnf_num, sknf_num = self.numeric_converter.convert_to_numeric(self.current_func)
        idx_form = self.numeric_converter.get_index_representation(self.current_func)
        print(f"  Числовая СДНФ: {sdnf_num}")
        print(f"  Числовая СКНФ: {sknf_num}")
        print(f"  Индексная форма: {idx_form}")

    def _print_post_classes(self):
        print("\n 4. КЛАССЫ ПОСТА")
        print("-" * 50)
        classes = self.post_checker.check_all(self.current_func)
        names = {'T0': 'T0 - Сохранение 0', 'T1': 'T1 - Сохранение 1',
                 'S': 'S - Самодвойственность', 'M': 'M - Монотонность',
                 'L': 'L - Линейность'}
        for key, val in classes.items():
            print(f"  {names[key]}: {'ДА' if val else 'НЕТ'}")

    def _print_zhegalkin(self):
        print("\n 5. ПОЛИНОМ ЖЕГАЛКИНА")
        print("-" * 50)
        print(f"  P(x) = {self.poly_builder.build(self.current_func)}")

    def _print_fictitious_vars(self):
        print("\n 6. ФИКТИВНЫЕ ПЕРЕМЕННЫЕ")
        print("-" * 50)
        fict = self.fictitious_detector.find_fictitious(self.current_func)
        ess = self.fictitious_detector.find_essential(self.current_func)
        print(f"  Фиктивные: {', '.join(fict) if fict else 'нет'}")
        print(f"  Существенные: {', '.join(ess) if ess else 'нет'}")

    def _print_derivatives(self):
        print("\n 7. БУЛЕВЫ ПРОИЗВОДНЫЕ")
        print("-" * 50)
        derivatives = self.derivative_calc.all_derivatives(self.current_func)
        for name, expr in derivatives.items():
            print(f"    {name} = {expr}")

    def _print_minimization(self):
        """Выводит результаты минимизации"""
        print("\n 8. МИНИМИЗАЦИЯ")
        print("-" * 50)

        f = self.current_func

        # А. Расчетный метод
        print("\n  А. Расчетный метод:")
        result_glue, stages_glue = self.glue_minimizer.minimize(f)

        # Выводим ВСЕ этапы из stages_glue
        for stage in stages_glue:
            if stage.startswith("=") or stage.startswith("-"):
                print(f"    {stage}")
            elif stage.startswith("МИНИМИЗАЦИЯ") or stage.startswith("СРАВНЕНИЕ"):
                print(f"\n    {stage}")
            elif stage.startswith("Исходная СДНФ") or stage.startswith("Исходная СКНФ"):
                print(f"    {stage}")
            elif stage.startswith("Этап склеивания"):
                print(f"    {stage}")
            elif stage.startswith("Простые импликанты") or stage.startswith("Простые имплиценты"):
                print(f"    {stage}")
            elif stage.startswith("Существенные импликанты") or stage.startswith("Существенные имплиценты"):
                print(f"    {stage}")
            elif stage.startswith("Результат ДНФ") or stage.startswith("Результат КНФ"):
                print(f"    {stage}")
            elif stage.startswith("ДНФ:") or stage.startswith("КНФ:"):
                print(f"    {stage}")
            elif stage.startswith("Лучший результат"):
                print(f"    {stage}")
            elif stage.strip() and not stage.startswith("+"):
                print(f"    {stage}")

        print(f"\n    РЕЗУЛЬТАТ: {result_glue}")

        # Б. Расчетно-табличный метод
        print("\n  Б. Расчетно-табличный метод:")
        result_table, stages_table, table_str = self.table_minimizer.minimize(f)

        for stage in stages_table:
            if stage.startswith("+") or stage.startswith("|"):
                print(f"    {stage}")
            elif stage.startswith("-") or stage.startswith("МИНИМИЗАЦИЯ") or stage.startswith("СРАВНЕНИЕ"):
                print(f"\n    {stage}")
            elif stage.startswith("Результат ДНФ") or stage.startswith("Результат КНФ"):
                print(f"    {stage}")
            elif stage.startswith("ДНФ:") or stage.startswith("КНФ:"):
                print(f"    {stage}")
            elif stage.startswith("Лучший результат"):
                print(f"    {stage}")
            elif stage.strip():
                print(f"    {stage}")

        print(f"\n    РЕЗУЛЬТАТ: {result_table}")

        # В. Карта Карно
        print("\n  В. Карта Карно:")
        result_karnaugh, karnaugh_map = self.karnaugh_minimizer.minimize(f)
        for line in karnaugh_map.split('\n'):
            print(f"    {line}")
        print(f"\n    РЕЗУЛЬТАТ: {result_karnaugh}")
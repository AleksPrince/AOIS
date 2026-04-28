"""Минимизация расчетно-табличным методом для ДНФ и КНФ"""

from typing import List, Tuple, Set
from tabulate import tabulate
from core.logic_function import LogicFunction
from utils.term_processor import TermProcessor
from operations.normal_forms_builder import NormalFormsBuilder


class TableMinimizer:
    """Минимизация с построением таблицы покрытия (ДНФ и КНФ)"""

    def __init__(self):
        self.term_proc = TermProcessor()
        self.form_builder = NormalFormsBuilder(self.term_proc)

    def minimize(self, function: LogicFunction) -> Tuple[str, List[str], str]:
        """
        Выполняет минимизацию и возвращает (результат, этапы, таблица)
        Показывает обе таблицы (ДНФ и КНФ) и выбирает лучший результат
        """
        stages = []
        stages.append("=" * 60)
        stages.append("МИНИМИЗАЦИЯ РАСЧЕТНО-ТАБЛИЧНЫМ МЕТОДОМ")
        stages.append("=" * 60)

        # Получаем СДНФ и СКНФ
        sdnf, sknf = self.form_builder.build(function)

        # ========== МИНИМИЗАЦИЯ ПО ДНФ ==========
        stages.append("\n" + "-" * 50)
        stages.append("МИНИМИЗАЦИЯ ПО ДНФ (ПО ЕДИНИЦАМ)")
        stages.append("-" * 50)

        result_dnf, table_dnf, implicants_dnf = self._minimize_dnf_with_table(sdnf, function)
        stages.append(table_dnf)
        stages.append(f"\nРезультат ДНФ: {result_dnf}")

        # ========== МИНИМИЗАЦИЯ ПО КНФ ==========
        stages.append("\n" + "-" * 50)
        stages.append("МИНИМИЗАЦИЯ ПО КНФ (ПО НУЛЯМ)")
        stages.append("-" * 50)

        result_cnf, table_cnf, implicants_cnf = self._minimize_cnf_with_table(sknf, function)
        stages.append(table_cnf)
        stages.append(f"\nРезультат КНФ: {result_cnf}")

        # ========== СРАВНЕНИЕ ==========
        len_dnf = len(result_dnf.replace(' ', ''))
        len_cnf = len(result_cnf.replace(' ', ''))

        stages.append("\n" + "-" * 50)
        stages.append("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
        stages.append("-" * 50)
        stages.append(f"ДНФ: {result_dnf} (длина: {len_dnf})")
        stages.append(f"КНФ: {result_cnf} (длина: {len_cnf})")

        if len_dnf <= len_cnf:
            stages.append(f"\nЛучший результат (ДНФ): {result_dnf}")
            return result_dnf, stages, table_dnf
        else:
            stages.append(f"\nЛучший результат (КНФ): {result_cnf}")
            return result_cnf, stages, table_cnf

    def _minimize_dnf_with_table(self, dnf: str, function: LogicFunction) -> Tuple[str, str, List[str]]:
        """Минимизация ДНФ с построением таблицы покрытия"""
        if dnf == '0':
            return '0', "Нет единиц", []
        if dnf == '1':
            return '1', "Функция-константа 1", []

        # Получаем простые импликанты
        implicants = self._get_prime_implicants_dnf(dnf, function)
        ones_sets = function.truth_matrix.get_sets_where_one()

        if not implicants or not ones_sets:
            return dnf, "Таблица покрытия не требуется", implicants

        # Строим таблицу покрытия
        table_str = self._build_table_dnf(implicants, ones_sets, function.variables)

        # Находим минимальное покрытие
        essential = self._find_min_cover_dnf(implicants, ones_sets, function.variables)

        result = ' ∨ '.join(essential) if essential else '0'
        return result, table_str, essential

    def _minimize_cnf_with_table(self, cnf: str, function: LogicFunction) -> Tuple[str, str, List[str]]:
        """Минимизация КНФ с построением таблицы покрытия"""
        if cnf == '1':
            return '1', "Нет нулей (функция-константа 1)", []
        if cnf == '0':
            return '0', "Функция-константа 0", []

        # Получаем простые имплиценты
        implicants = self._get_prime_implicants_cnf(cnf, function)
        zeros_sets = function.truth_matrix.get_sets_where_zero()

        if not implicants or not zeros_sets:
            return cnf, "Таблица покрытия не требуется", implicants

        # Строим таблицу покрытия
        table_str = self._build_table_cnf(implicants, zeros_sets, function.variables)

        # Находим минимальное покрытие
        essential = self._find_min_cover_cnf(implicants, zeros_sets, function.variables)

        result = ' ∧ '.join(essential) if essential else '1'
        return result, table_str, essential

    def _get_prime_implicants_dnf(self, dnf: str, function: LogicFunction) -> List[str]:
        """Получает простые импликанты методом склеивания для ДНФ"""
        terms = self.term_proc.extract_dnf_terms(dnf)
        current_terms = set(terms)

        while True:
            new_terms, used = self._glue_terms_dnf(list(current_terms), function.variables)
            for term in current_terms:
                if term not in used:
                    new_terms.add(term)
            if not new_terms or new_terms == current_terms:
                return list(new_terms)
            current_terms = new_terms

    def _get_prime_implicants_cnf(self, cnf: str, function: LogicFunction) -> List[str]:
        """Получает простые имплиценты методом склеивания для КНФ"""
        terms = self.term_proc.extract_cnf_terms(cnf)
        current_terms = set(terms)

        while True:
            new_terms, used = self._glue_terms_cnf(list(current_terms), function.variables)
            for term in current_terms:
                if term not in used:
                    new_terms.add(term)
            if not new_terms or new_terms == current_terms:
                return list(new_terms)
            current_terms = new_terms

    def _glue_terms_dnf(self, terms: List[str], variables: List[str]) -> Tuple[Set[str], Set[str]]:
        """Склеивание термов в ДНФ"""
        new_terms = set()
        used = set()
        n = len(terms)

        for i in range(n):
            for j in range(i + 1, n):
                lit1 = set(self.term_proc.split_into_literals(terms[i]))
                lit2 = set(self.term_proc.split_into_literals(terms[j]))
                diff = lit1.symmetric_difference(lit2)

                if len(diff) == 2:
                    diff_list = list(diff)
                    a, b = diff_list[0], diff_list[1]
                    if (a[0] == '!' and a[1:] == b) or (b[0] == '!' and b[1:] == a):
                        common = lit1.intersection(lit2)
                        if common:
                            glued = self.term_proc.join_literals(sorted(common), '&')
                            new_terms.add(glued)
                            used.add(terms[i])
                            used.add(terms[j])

        return new_terms, used

    def _glue_terms_cnf(self, terms: List[str], variables: List[str]) -> Tuple[Set[str], Set[str]]:
        """Склеивание термов в КНФ"""
        new_terms = set()
        used = set()
        n = len(terms)

        for i in range(n):
            for j in range(i + 1, n):
                lit1 = set(self.term_proc.split_into_literals(terms[i]))
                lit2 = set(self.term_proc.split_into_literals(terms[j]))
                diff = lit1.symmetric_difference(lit2)

                if len(diff) == 2:
                    diff_list = list(diff)
                    a, b = diff_list[0], diff_list[1]
                    if (a[0] == '!' and a[1:] == b) or (b[0] == '!' and b[1:] == a):
                        common = lit1.intersection(lit2)
                        if common:
                            glued = self.term_proc.join_literals(sorted(common), '|')
                            new_terms.add(glued)
                            used.add(terms[i])
                            used.add(terms[j])

        return new_terms, used

    def _build_table_dnf(self, implicants: List[str], ones: List[Tuple[int, ...]], variables: List[str]) -> str:
        """Строит таблицу покрытия для ДНФ"""
        if not ones:
            return "Нет наборов с результатом 1"

        headers = ['Импликанта'] + [''.join(str(b) for b in bits) for bits in ones]
        data = []
        for imp in implicants:
            row = [imp]
            for bits in ones:
                if self._covers_dnf(imp, bits, variables):
                    row.append('X')
                else:
                    row.append('')
            data.append(row)

        return tabulate(data, headers=headers, tablefmt='grid')

    def _build_table_cnf(self, implicants: List[str], zeros: List[Tuple[int, ...]], variables: List[str]) -> str:
        """Строит таблицу покрытия для КНФ"""
        if not zeros:
            return "Нет наборов с результатом 0"

        headers = ['Имплицента'] + [''.join(str(b) for b in bits) for bits in zeros]
        data = []
        for imp in implicants:
            row = [imp]
            for bits in zeros:
                if self._covers_cnf(imp, bits, variables):
                    row.append('X')
                else:
                    row.append('')
            data.append(row)

        return tabulate(data, headers=headers, tablefmt='grid')

    def _find_min_cover_dnf(self, implicants: List[str], ones: List[Tuple[int, ...]], variables: List[str]) -> List[
        str]:
        """Находит минимальное покрытие для ДНФ"""
        if not ones:
            return []

        coverage = {}
        for imp in implicants:
            covered = []
            for bits in ones:
                if self._covers_dnf(imp, bits, variables):
                    covered.append(bits)
            if covered:
                coverage[imp] = covered

        essential = []
        covered_sets = set()

        for imp, covered in coverage.items():
            for bits in covered:
                if sum(1 for other in coverage.values() if bits in other) == 1:
                    if imp not in essential:
                        essential.append(imp)
                        covered_sets.update(covered)

        remaining = [b for b in ones if b not in covered_sets]

        while remaining:
            best = None
            best_cnt = 0
            for imp, covered in coverage.items():
                if imp in essential:
                    continue
                cnt = sum(1 for b in remaining if b in covered)
                if cnt > best_cnt:
                    best_cnt = cnt
                    best = imp
            if best:
                essential.append(best)
                covered_sets.update(coverage[best])
                remaining = [b for b in ones if b not in covered_sets]
            else:
                break

        return essential

    def _find_min_cover_cnf(self, implicants: List[str], zeros: List[Tuple[int, ...]], variables: List[str]) -> List[
        str]:
        """Находит минимальное покрытие для КНФ"""
        if not zeros:
            return []

        coverage = {}
        for imp in implicants:
            covered = []
            for bits in zeros:
                if self._covers_cnf(imp, bits, variables):
                    covered.append(bits)
            if covered:
                coverage[imp] = covered

        essential = []
        covered_sets = set()

        for imp, covered in coverage.items():
            for bits in covered:
                if sum(1 for other in coverage.values() if bits in other) == 1:
                    if imp not in essential:
                        essential.append(imp)
                        covered_sets.update(covered)

        remaining = [b for b in zeros if b not in covered_sets]

        while remaining:
            best = None
            best_cnt = 0
            for imp, covered in coverage.items():
                if imp in essential:
                    continue
                cnt = sum(1 for b in remaining if b in covered)
                if cnt > best_cnt:
                    best_cnt = cnt
                    best = imp
            if best:
                essential.append(best)
                covered_sets.update(coverage[best])
                remaining = [b for b in zeros if b not in covered_sets]
            else:
                break

        return essential

    def _covers_dnf(self, term: str, bits: Tuple[int, ...], variables: List[str]) -> bool:
        """Проверка, покрывает ли терм ДНФ набор"""
        literals = self.term_proc.split_into_literals(term)
        vmap = dict(zip(variables, bits))
        for lit in literals:
            if lit.startswith('!'):
                if vmap.get(lit[1:]) != 0:
                    return False
            else:
                if vmap.get(lit) != 1:
                    return False
        return True

    def _covers_cnf(self, term: str, bits: Tuple[int, ...], variables: List[str]) -> bool:
        """
        Проверка, покрывает ли терм КНФ нулевой набор
        Терм покрывает набор, если на этом наборе он равен 1
        """
        literals = self.term_proc.split_into_literals(term)
        vmap = dict(zip(variables, bits))
        for lit in literals:
            if lit.startswith('!'):
                if vmap.get(lit[1:]) == 0:
                    return True
            else:
                if vmap.get(lit) == 1:
                    return True
        return False
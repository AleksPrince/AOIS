"""Минимизация расчетным методом (склеивание) для ДНФ и КНФ"""

from typing import List, Tuple, Set
from core.logic_function import LogicFunction
from utils.term_processor import TermProcessor
from operations.normal_forms_builder import NormalFormsBuilder


class GlueMinimizer:
    """Минимизация булевой функции методом склеивания"""

    def __init__(self):
        self.term_proc = TermProcessor()
        self.form_builder = NormalFormsBuilder(self.term_proc)

    def minimize(self, function: LogicFunction) -> Tuple[str, List[str]]:
        """Минимизация - показывает оба метода (ДНФ и КНФ) и выбирает лучший"""
        stages = []
        stages.append("=" * 60)
        stages.append("МИНИМИЗАЦИЯ РАСЧЕТНЫМ МЕТОДОМ (СКЛЕИВАНИЕ)")
        stages.append("=" * 60)

        # Получаем СДНФ и СКНФ
        sdnf, sknf = self.form_builder.build(function)

        # ========== МИНИМИЗАЦИЯ ПО ДНФ ==========
        stages.append("\n" + "-" * 50)
        stages.append("МИНИМИЗАЦИЯ ПО ДНФ (ПО ЕДИНИЦАМ)")
        stages.append("-" * 50)

        result_dnf, stages_dnf = self._minimize_by_dnf(sdnf, function)
        stages.extend(stages_dnf)
        stages.append(f"\nРезультат ДНФ: {result_dnf}")

        # ========== МИНИМИЗАЦИЯ ПО КНФ ==========
        stages.append("\n" + "-" * 50)
        stages.append("МИНИМИЗАЦИЯ ПО КНФ (ПО НУЛЯМ)")
        stages.append("-" * 50)

        result_cnf, stages_cnf = self._minimize_by_cnf(sknf, function)
        stages.extend(stages_cnf)
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
            return result_dnf, stages
        else:
            stages.append(f"\nЛучший результат (КНФ): {result_cnf}")
            return result_cnf, stages

    def _minimize_by_dnf(self, dnf: str, function: LogicFunction) -> Tuple[str, List[str]]:
        """Минимизация по ДНФ (склеивание конъюнкций)"""
        stages = []

        if dnf == '0':
            return '0', stages
        if dnf == '1':
            return '1', stages

        terms = self.term_proc.extract_dnf_terms(dnf)
        stages.append(f"Исходная СДНФ: {' ∨ '.join(terms)}")

        current_terms = set(terms)
        iteration = 1

        while True:
            new_terms, used = self._glue_dnf_terms(list(current_terms), function.variables)

            for term in current_terms:
                if term not in used:
                    new_terms.add(term)

            if not new_terms or new_terms == current_terms:
                all_implicants = list(new_terms)
                break

            stages.append(f"Этап склеивания {iteration}: {' ∨ '.join(sorted(new_terms))}")
            current_terms = new_terms
            iteration += 1

        stages.append(f"Простые импликанты: {' ∨ '.join(all_implicants)}")

        essential = self._find_essential_dnf(all_implicants, function)
        stages.append(f"Существенные импликанты: {' ∨ '.join(essential) if essential else 'нет'}")

        result = ' ∨ '.join(essential) if essential else '0'
        return result, stages

    def _minimize_by_cnf(self, cnf: str, function: LogicFunction) -> Tuple[str, List[str]]:
        """Минимизация по КНФ (склеивание дизъюнкций)"""
        stages = []

        if cnf == '1':
            return '1', stages
        if cnf == '0':
            return '0', stages

        terms = self.term_proc.extract_cnf_terms(cnf)
        stages.append(f"Исходная СКНФ: {' ∧ '.join(terms)}")

        current_terms = set(terms)
        iteration = 1

        while True:
            new_terms, used = self._glue_cnf_terms(list(current_terms), function.variables)

            for term in current_terms:
                if term not in used:
                    new_terms.add(term)

            if not new_terms or new_terms == current_terms:
                all_implicants = list(new_terms)
                break

            stages.append(f"Этап склеивания {iteration}: {' ∧ '.join(sorted(new_terms))}")
            current_terms = new_terms
            iteration += 1

        stages.append(f"Простые имплиценты: {' ∧ '.join(all_implicants)}")

        essential = self._find_essential_cnf(all_implicants, function)
        stages.append(f"Существенные имплиценты: {' ∧ '.join(essential) if essential else 'нет'}")

        result = ' ∧ '.join(essential) if essential else '1'
        return result, stages

    def _glue_dnf_terms(self, terms: List[str], variables: List[str]) -> Tuple[Set[str], Set[str]]:
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

    def _glue_cnf_terms(self, terms: List[str], variables: List[str]) -> Tuple[Set[str], Set[str]]:
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
                    # Для КНФ проверяем противоположные литералы
                    if (a[0] == '!' and a[1:] == b) or (b[0] == '!' and b[1:] == a):
                        common = lit1.intersection(lit2)
                        if common:
                            glued = self.term_proc.join_literals(sorted(common), '|')
                            new_terms.add(glued)
                            used.add(terms[i])
                            used.add(terms[j])

        return new_terms, used

    def _find_essential_dnf(self, implicants: List[str], function: LogicFunction) -> List[str]:
        """Поиск существенных импликант для ДНФ"""
        ones = function.truth_matrix.get_sets_where_one()
        if not ones:
            return []

        coverage = {}
        for imp in implicants:
            covered = []
            for bits in ones:
                if self._covers_dnf(imp, bits, function.variables):
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

    def _find_essential_cnf(self, implicants: List[str], function: LogicFunction) -> List[str]:
        """Поиск существенных имплицент для КНФ"""
        zeros = function.truth_matrix.get_sets_where_zero()
        if not zeros:
            return []

        coverage = {}
        for imp in implicants:
            covered = []
            for bits in zeros:
                if self._covers_cnf(imp, bits, function.variables):
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
        """Проверка, покрывает ли терм КНФ нулевой набор"""
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
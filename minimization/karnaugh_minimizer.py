"""Минимизация картами Карно для 2, 3, 4 и 5 переменных (ДНФ и КНФ)"""

from typing import List, Tuple, Dict, Set
from core.logic_function import LogicFunction


class KarnaughMinimizer:
    """Минимизация булевых функций с помощью карт Карно (ДНФ и КНФ)"""

    def __init__(self):
        self._last_dnf = ""
        self._last_cnf = ""

    def minimize(self, function: LogicFunction) -> Tuple[str, str]:
        """
        Возвращает (минимизированное_выражение, карта_в_виде_строки)
        Выбирает лучший результат между ДНФ и КНФ
        """
        var_count = function.get_variable_count()

        if var_count == 0:
            return function.expression, "Функция-константа"

        # Получаем оба результата
        result_dnf = self._minimize_dnf(function)
        result_cnf = self._minimize_cnf(function)

        # Строим карту для отображения
        if var_count == 1:
            map_str = self._build_map_1var(function)
        elif var_count == 2:
            map_str = self._build_map_2var(function)
        elif var_count == 3:
            map_str = self._build_map_3var(function)
        elif var_count == 4:
            map_str = self._build_map_4var(function)
        elif var_count == 5:
            map_str = self._build_map_5var(function)
        else:
            return "Ошибка: карты Карно поддерживаются до 5 переменных", ""

        # Выбираем лучший результат (по длине)
        len_dnf = len(result_dnf.replace(' ', ''))
        len_cnf = len(result_cnf.replace(' ', ''))

        if len_dnf <= len_cnf:
            return result_dnf, map_str
        else:
            return result_cnf, map_str

    # ==================== МИНИМИЗАЦИЯ ДНФ ====================

    def _minimize_dnf(self, function: LogicFunction) -> str:
        """Минимизация по ДНФ (по единицам)"""
        var_count = function.get_variable_count()

        if var_count == 1:
            return self._minimize_1var_dnf(function)
        elif var_count == 2:
            return self._minimize_2var_dnf(function)
        elif var_count == 3:
            return self._minimize_3var_dnf(function)
        elif var_count == 4:
            return self._minimize_4var_dnf(function)
        elif var_count == 5:
            return self._minimize_5var_dnf(function)
        else:
            return "0"

    # ==================== МИНИМИЗАЦИЯ КНФ ====================

    def _minimize_cnf(self, function: LogicFunction) -> str:
        """Минимизация по КНФ (по нулям)"""
        var_count = function.get_variable_count()

        if var_count == 1:
            return self._minimize_1var_cnf(function)
        elif var_count == 2:
            return self._minimize_2var_cnf(function)
        elif var_count == 3:
            return self._minimize_3var_cnf(function)
        elif var_count == 4:
            return self._minimize_4var_cnf(function)
        elif var_count == 5:
            return self._minimize_5var_cnf(function)
        else:
            return "1"

    # ==================== 1 ПЕРЕМЕННАЯ ====================

    def _minimize_1var_dnf(self, function: LogicFunction) -> str:
        results = function.truth_matrix.get_result_column()
        if results[0] == 1 and results[1] == 1:
            self._last_dnf, self._last_cnf = "1", "1"
            return "1"
        elif results[0] == 0 and results[1] == 0:
            self._last_dnf, self._last_cnf = "0", "0"
            return "0"
        elif results[0] == 1 and results[1] == 0:
            self._last_dnf, self._last_cnf = "!a", "a"
            return "!a"
        else:
            self._last_dnf, self._last_cnf = "a", "!a"
            return "a"

    def _minimize_1var_cnf(self, function: LogicFunction) -> str:
        results = function.truth_matrix.get_result_column()
        if results[0] == 1 and results[1] == 1:
            return "1"
        elif results[0] == 0 and results[1] == 0:
            return "0"
        elif results[0] == 1 and results[1] == 0:
            return "a"
        else:
            return "!a"

    # ==================== 2 ПЕРЕМЕННЫЕ ====================

    def _minimize_2var_dnf(self, function: LogicFunction) -> str:
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1])] = res

        groups = self._find_groups_2var(kmap, ones=True)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_2var(group, variables)
            if term and term not in terms:
                terms.append(term)

        result = " ∨ ".join(terms) if terms else "0"
        self._last_dnf = result
        return result

    def _minimize_2var_cnf(self, function: LogicFunction) -> str:
        # Для КНФ работаем с нулями
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1])] = 1 - res

        groups = self._find_groups_2var(kmap, ones=True)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_2var(group, variables)
            if term and term not in terms:
                term = self._invert_term(term)
                terms.append(term)

        if not terms:
            self._last_cnf = "1"
            return "1"
        result = " ∧ ".join(terms)
        self._last_cnf = result
        return result

    # ==================== 3 ПЕРЕМЕННЫЕ ====================

    def _minimize_3var_dnf(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2])] = res

        groups = self._find_groups_3var(kmap, gray, ones=True)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_3var(group, variables)
            if term and term not in terms:
                terms.append(term)

        result = " ∨ ".join(terms) if terms else "0"
        self._last_dnf = result
        return result

    def _minimize_3var_cnf(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2])] = 1 - res

        groups = self._find_groups_3var(kmap, gray, ones=True)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_3var(group, variables)
            if term and term not in terms:
                term = self._invert_term(term)
                terms.append(term)

        if not terms:
            self._last_cnf = "1"
            return "1"
        result = " ∧ ".join(terms)
        self._last_cnf = result
        return result

    # ==================== 4 ПЕРЕМЕННЫЕ ====================

    def _minimize_4var_dnf(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2], bits[3])] = res

        groups = self._find_groups_4var(kmap, gray, ones=True)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_4var(group, variables)
            if term and term not in terms:
                terms.append(term)

        result = " ∨ ".join(terms) if terms else "0"
        self._last_dnf = result
        return result

    def _minimize_4var_cnf(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2], bits[3])] = 1 - res

        groups = self._find_groups_4var(kmap, gray, ones=True)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_4var(group, variables)
            if term and term not in terms:
                term = self._invert_term(term)
                terms.append(term)

        if not terms:
            self._last_cnf = "1"
            return "1"
        result = " ∧ ".join(terms)
        self._last_cnf = result
        return result

    # ==================== 5 ПЕРЕМЕННЫЕ ====================

    def _minimize_5var_dnf(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2], bits[3], bits[4])] = res

        layer0 = {}
        layer1 = {}
        for (a, b, c, d, e), res in kmap.items():
            if a == 0:
                layer0[(b, c, d, e)] = res
            else:
                layer1[(b, c, d, e)] = res

        groups0 = self._find_groups_4var_from_dict(layer0, gray, ones=True)
        groups1 = self._find_groups_4var_from_dict(layer1, gray, ones=True)

        variables = function.variables
        a_var = variables[0]
        rest_vars = variables[1:]

        terms = set()

        for group in groups0:
            term = self._term_from_group_4var(group, rest_vars)
            if term and term != "1":
                found = False
                for g1 in groups1:
                    t1 = self._term_from_group_4var(g1, rest_vars)
                    if t1 == term:
                        found = True
                        break
                if found:
                    terms.add(term)
                else:
                    terms.add(f"!{a_var} & {term}")

        for group in groups1:
            term = self._term_from_group_4var(group, rest_vars)
            if term and term != "1":
                found = False
                for g0 in groups0:
                    t0 = self._term_from_group_4var(g0, rest_vars)
                    if t0 == term:
                        found = True
                        break
                if not found:
                    terms.add(f"{a_var} & {term}")

        result = " ∨ ".join(sorted(terms)) if terms else "0"
        result = self._simplify_dnf(result)
        self._last_dnf = result
        return result

    def _minimize_5var_cnf(self, function: LogicFunction) -> str:
        """Минимизация по КНФ для 5 переменных - используем результат расчётного метода"""
        from minimization.glue_minimizer import GlueMinimizer
        from operations.normal_forms_builder import NormalFormsBuilder
        from utils.term_processor import TermProcessor

        # Получаем СКНФ
        builder = NormalFormsBuilder(TermProcessor())
        _, sknf = builder.build(function)

        # Минимизируем КНФ через расчётный метод
        glue = GlueMinimizer()
        result, _ = glue._minimize_by_cnf(sknf, function)
        self._last_cnf = result
        return result

    def _simplify_dnf(self, expression: str) -> str:
        """Упрощает ДНФ"""
        if expression == "0" or expression == "1":
            return expression

        terms = expression.split(' ∨ ')
        terms = list(dict.fromkeys(terms))

        simplified = []
        for i, t1 in enumerate(terms):
            is_absorbed = False
            lits1 = set(t1.split('&'))
            for j, t2 in enumerate(terms):
                if i != j:
                    lits2 = set(t2.split('&'))
                    if lits2.issubset(lits1):
                        is_absorbed = True
                        break
            if not is_absorbed:
                simplified.append(t1)

        if not simplified:
            return "0"
        return " ∨ ".join(sorted(simplified))

    # ==================== ОБЩИЕ МЕТОДЫ ДЛЯ ПОИСКА ГРУПП ====================

    def _find_groups_2var(self, kmap: Dict[Tuple[int, int], int], ones: bool = True) -> List[Set[Tuple[int, int]]]:
        """Находит группы единиц в карте 2x2"""
        cells = [pos for pos, val in kmap.items() if val == 1]
        if not cells:
            return []

        groups = []
        used = set()

        all_cells = {(0, 0), (0, 1), (1, 0), (1, 1)}
        if all(kmap.get(cell, 0) == 1 for cell in all_cells):
            return [all_cells]

        for a in [0, 1]:
            if kmap.get((a, 0), 0) == 1 and kmap.get((a, 1), 0) == 1:
                group = {(a, 0), (a, 1)}
                groups.append(group)
                used.update(group)

        for b in [0, 1]:
            if kmap.get((0, b), 0) == 1 and kmap.get((1, b), 0) == 1:
                group = {(0, b), (1, b)}
                if group not in groups:
                    groups.append(group)
                    used.update(group)

        for pos in cells:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

    def _find_groups_3var(self, kmap: Dict[Tuple[int, int, int], int], gray: List[Tuple[int, int]],
                          ones: bool = True) -> List[Set[Tuple[int, int, int]]]:
        """Находит группы единиц в карте 3 переменных"""
        cells = [pos for pos, val in kmap.items() if val == 1]
        if not cells:
            return []

        groups = []
        used = set()

        if len(cells) == 8:
            return [set(cells)]

        for a in [0, 1]:
            row = [(a, bc[0], bc[1]) for bc in gray]
            if all(kmap.get(cell, 0) == 1 for cell in row):
                group = set(row)
                groups.append(group)
                used.update(group)

        for col_start in range(4):
            c1 = gray[col_start]
            c2 = gray[(col_start + 1) % 4]
            cells_2x2 = [
                (0, c1[0], c1[1]), (0, c2[0], c2[1]),
                (1, c1[0], c1[1]), (1, c2[0], c2[1])
            ]
            if all(kmap.get(cell, 0) == 1 for cell in cells_2x2):
                group = set(cells_2x2)
                if group not in groups:
                    groups.append(group)
                    used.update(group)

        for a in [0, 1]:
            for col_start in range(4):
                c1 = gray[col_start]
                c2 = gray[(col_start + 1) % 4]
                group = {(a, c1[0], c1[1]), (a, c2[0], c2[1])}
                if all(kmap.get(cell, 0) == 1 for cell in group):
                    if group not in groups:
                        groups.append(group)
                        used.update(group)

        for bc in gray:
            group = {(0, bc[0], bc[1]), (1, bc[0], bc[1])}
            if all(kmap.get(cell, 0) == 1 for cell in group):
                if group not in groups:
                    groups.append(group)
                    used.update(group)

        c1_cells = [(a, bc[0], bc[1]) for a in [0, 1] for bc in gray if bc[1] == 1]
        c0_cells = [(a, bc[0], bc[1]) for a in [0, 1] for bc in gray if bc[1] == 0]

        if len(c1_cells) == 4 and all(kmap.get(cell, 0) == 1 for cell in c1_cells):
            group = set(c1_cells)
            if group not in groups:
                groups.append(group)
                used.update(group)

        if len(c0_cells) == 4 and all(kmap.get(cell, 0) == 1 for cell in c0_cells):
            group = set(c0_cells)
            if group not in groups:
                groups.append(group)
                used.update(group)

        for pos in cells:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

    def _find_groups_4var(self, kmap: Dict[Tuple[int, int, int, int], int], gray: List[Tuple[int, int]],
                          ones: bool = True) -> List[Set[Tuple[int, int, int, int]]]:
        """Находит группы единиц в карте 4 переменных"""
        cells = [pos for pos, val in kmap.items() if val == 1]
        if not cells:
            return []

        if len(cells) == 16:
            return [set(cells)]

        groups = []
        used = set()

        for rows in [1, 2, 4]:
            for cols in [1, 2, 4]:
                for row_start in range(4):
                    for col_start in range(4):
                        group = set()
                        valid = True
                        for dr in range(rows):
                            r = (row_start + dr) % 4
                            for dc in range(cols):
                                c = (col_start + dc) % 4
                                a, b = gray[r]
                                cd = gray[c]
                                pos = (a, b, cd[0], cd[1])
                                if kmap.get(pos, 0) == 1:
                                    group.add(pos)
                                else:
                                    valid = False
                                    break
                            if not valid:
                                break
                        if valid and len(group) >= 2 and group not in groups:
                            groups.append(group)
                            used.update(group)

        for pos in cells:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

    def _find_groups_4var_from_dict(self, layer: Dict[Tuple[int, int, int, int], int], gray: List[Tuple[int, int]],
                                    ones: bool = True) -> List[Set[Tuple[int, int, int, int]]]:
        """Находит группы в одном слое 4-переменной карты"""
        cells = [pos for pos, val in layer.items() if val == 1]
        if not cells:
            return []

        if len(cells) == 16:
            return [set(cells)]

        groups = []
        used = set()

        for rows in [1, 2, 4]:
            for cols in [1, 2, 4]:
                for row_start in range(4):
                    for col_start in range(4):
                        group = set()
                        valid = True
                        for dr in range(rows):
                            r = (row_start + dr) % 4
                            for dc in range(cols):
                                c = (col_start + dc) % 4
                                a, b = gray[r]
                                cd = gray[c]
                                pos = (a, b, cd[0], cd[1])
                                if layer.get(pos, 0) == 1:
                                    group.add(pos)
                                else:
                                    valid = False
                                    break
                            if not valid:
                                break
                        if valid and len(group) >= 2 and group not in groups:
                            groups.append(group)
                            used.update(group)

        for pos in cells:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

    # ==================== ПРЕОБРАЗОВАНИЕ ТЕРМОВ ====================

    def _term_from_group_2var(self, group: Set[Tuple[int, int]], vars_list: List[str]) -> str:
        a, b = vars_list[0], vars_list[1]
        literals = []

        a_vals = {p[0] for p in group}
        if len(a_vals) == 1:
            literals.append(a if list(a_vals)[0] == 1 else f"!{a}")

        b_vals = {p[1] for p in group}
        if len(b_vals) == 1:
            literals.append(b if list(b_vals)[0] == 1 else f"!{b}")

        if not literals:
            return "1"
        if len(literals) == 1:
            return literals[0]
        return "&".join(literals)

    def _term_from_group_3var(self, group: Set[Tuple[int, int, int]], vars_list: List[str]) -> str:
        a, b, c = vars_list[0], vars_list[1], vars_list[2]
        literals = []

        a_vals = {p[0] for p in group}
        if len(a_vals) == 1:
            literals.append(a if list(a_vals)[0] == 1 else f"!{a}")

        b_vals = {p[1] for p in group}
        if len(b_vals) == 1:
            literals.append(b if list(b_vals)[0] == 1 else f"!{b}")

        c_vals = {p[2] for p in group}
        if len(c_vals) == 1:
            literals.append(c if list(c_vals)[0] == 1 else f"!{c}")

        if not literals:
            return "1"
        literals.sort()
        if len(literals) == 1:
            return literals[0]
        return "&".join(literals)

    def _term_from_group_4var(self, group: Set[Tuple[int, int, int, int]], vars_list: List[str]) -> str:
        if not group:
            return ""

        a, b, c, d = vars_list[0], vars_list[1], vars_list[2], vars_list[3]
        literals = []

        a_vals = {p[0] for p in group}
        if len(a_vals) == 1:
            literals.append(a if list(a_vals)[0] == 1 else f"!{a}")

        b_vals = {p[1] for p in group}
        if len(b_vals) == 1:
            literals.append(b if list(b_vals)[0] == 1 else f"!{b}")

        c_vals = {p[2] for p in group}
        if len(c_vals) == 1:
            literals.append(c if list(c_vals)[0] == 1 else f"!{c}")

        d_vals = {p[3] for p in group}
        if len(d_vals) == 1:
            literals.append(d if list(d_vals)[0] == 1 else f"!{d}")

        if not literals:
            return "1"
        literals.sort()
        if len(literals) == 1:
            return literals[0]
        return "&".join(literals)

    def _invert_term(self, term: str) -> str:
        """Инвертирует терм: a&b -> !a|!b, a -> !a"""
        if term == "1":
            return "0"
        if term == "0":
            return "1"

        if '&' in term:
            literals = term.split('&')
            inverted = []
            for lit in literals:
                if lit.startswith('!'):
                    inverted.append(lit[1:])
                else:
                    inverted.append(f"!{lit}")
            return "|".join(inverted)
        else:
            if term.startswith('!'):
                return term[1:]
            else:
                return f"!{term}"

    # ==================== ОБЩИЕ МЕТОДЫ ====================

    def _deduplicate(self, groups: List[Set]) -> List[Set]:
        """Удаляет группы, которые являются подмножествами других"""
        result = []
        groups_sorted = sorted(groups, key=len, reverse=True)
        for i, g in enumerate(groups_sorted):
            is_subset = False
            for j, h in enumerate(groups_sorted):
                if i != j and g.issubset(h):
                    is_subset = True
                    break
            if not is_subset:
                result.append(g)
        return result

    # ==================== ВИЗУАЛИЗАЦИЯ ====================

    def _build_map_1var(self, function: LogicFunction) -> str:
        r = function.truth_matrix.get_result_column()
        lines = [
            f"Карта Карно (1):",
            f"  0 1",
            f"a {r[0]} {r[1]}",
            f"\nДНФ: {self._normalize_dnf(self._last_dnf)}",
            f"КНФ: {self._normalize_cnf(self._last_cnf)}"
        ]
        return "\n".join(lines)

    def _build_map_2var(self, function: LogicFunction) -> str:
        values = {}
        for bits, res in function.truth_matrix:
            values[(bits[0], bits[1])] = res
        lines = [
            "Карта Карно (2):",
            "    b0 b1"
        ]
        for a in [0, 1]:
            lines.append(f"a{a}  {values.get((a, 0), 0)}  {values.get((a, 1), 0)}")
        lines.append(f"\nДНФ: {self._normalize_dnf(self._last_dnf)}")
        lines.append(f"КНФ: {self._normalize_cnf(self._last_cnf)}")
        return "\n".join(lines)

    def _build_map_3var(self, function: LogicFunction) -> str:
        values = {}
        for bits, res in function.truth_matrix:
            values[(bits[0], bits[1], bits[2])] = res
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        lines = [
            "┌─────────────────────────────────────┐",
            "│           Карта Карно               │",
            "├─────────┬─────┬─────┬─────┬─────┬───┤",
            "│ a \\ bc  │ 00  │ 01  │ 11  │ 10  │   │",
            "├─────────┼─────┼─────┼─────┼─────┼───┤"
        ]
        for a in [0, 1]:
            row = f"│   {a}     │"
            for b, c in gray:
                row += f"  {values.get((a, b, c), 0)}  │"
            row += "   │"
            lines.append(row)
        lines.append("└─────────┴─────┴─────┴─────┴─────┴───┘")
        lines.append("\nПорядок bc: код Грея (00,01,11,10)")
        lines.append(f"\nДНФ: {self._normalize_dnf(self._last_dnf)}")
        lines.append(f"КНФ: {self._normalize_cnf(self._last_cnf)}")
        return "\n".join(lines)

    def _build_map_4var(self, function: LogicFunction) -> str:
        values = {}
        for bits, res in function.truth_matrix:
            values[(bits[0], bits[1], bits[2], bits[3])] = res
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        lines = [
            "┌─────────────────────────────────────────────────────────┐",
            "│                    Карта Карно                          │",
            "├──────────┬──────┬──────┬──────┬──────┬─────────────────┤",
            "│ ab \\ cd  │ 00   │ 01   │ 11   │ 10   │                 │",
            "├──────────┼──────┼──────┼──────┼──────┼─────────────────┤"
        ]
        for a, b in gray:
            row = f"│  {a}{b}    │"
            for c, d in gray:
                row += f"  {values.get((a, b, c, d), 0)}   │"
            row += "                 │"
            lines.append(row)
        lines.append("└──────────┴──────┴──────┴──────┴──────┴─────────────────┘")
        lines.append("\nПорядок ab и cd: код Грея (00,01,11,10)")
        lines.append(f"\nДНФ: {self._normalize_dnf(self._last_dnf)}")
        lines.append(f"КНФ: {self._normalize_cnf(self._last_cnf)}")
        return "\n".join(lines)

    def _build_map_5var(self, function: LogicFunction) -> str:
        values = {}
        for bits, res in function.truth_matrix:
            values[(bits[0], bits[1], bits[2], bits[3], bits[4])] = res
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        lines = [
            "╔════════════════════════════════════════════════════════════════════════════════╗",
            "│                        Карта Карно (5 переменных)                              │",
            "╠════════════════════════════════════════════════════════════════════════════════╣",
            "│   Слой a = 0                                                                   │",
            "├──────────┬──────┬──────┬──────┬──────┬─────────────────────────────────────────┤",
            "│  bc \ de │ 00   │ 01   │ 11   │ 10   │                                         │",
            "├──────────┼──────┼──────┼──────┼──────┼─────────────────────────────────────────┤"
        ]
        for b, c in gray:
            row = f"│  {b}{c}    │"
            for d, e in gray:
                row += f"  {values.get((0, b, c, d, e), 0)}   │"
            row += "                                         │"
            lines.append(row)
        lines.append("├──────────┴──────┴──────┴──────┴──────┴─────────────────────────────────────────┤")
        lines.append("│   Слой a = 1                                                                   │")
        lines.append("├──────────┬──────┬──────┬──────┬──────┬─────────────────────────────────────────┤")
        for b, c in gray:
            row = f"│  {b}{c}    │"
            for d, e in gray:
                row += f"  {values.get((1, b, c, d, e), 0)}   │"
            row += "                                         │"
            lines.append(row)
        lines.append("└──────────┴──────┴──────┴──────┴──────┴─────────────────────────────────────────┘")
        lines.append("\nПорядок bc и de: код Грея (00,01,11,10)")
        lines.append(f"\nДНФ: {self._normalize_dnf(self._last_dnf)}")
        lines.append(f"КНФ: {self._normalize_cnf(self._last_cnf)}")
        return "\n".join(lines)

    def _normalize_dnf(self, expr: str) -> str:
        """Нормализует ДНФ: сортирует термы и литералы"""
        if not expr or expr == "0" or expr == "1":
            return expr

        terms = expr.split(' ∨ ')
        normalized_terms = []
        for t in terms:
            t = t.strip()
            if '&' in t:
                literals = t.split('&')
                literals = [l.strip() for l in literals]
                literals.sort()
                if len(literals) > 1:
                    normalized_terms.append("&".join(literals))
                else:
                    normalized_terms.append(literals[0])
            else:
                normalized_terms.append(t)

        normalized_terms.sort()
        return " ∨ ".join(normalized_terms)

    def _normalize_cnf(self, expr: str) -> str:
        """Нормализует КНФ: убирает скобки, сортирует термы и литералы"""
        if not expr or expr == "1" or expr == "0":
            return expr

        expr_clean = expr.replace('(', '').replace(')', '')
        terms = expr_clean.split(' ∧ ')

        normalized_terms = []
        for t in terms:
            t = t.strip()
            if '|' in t:
                literals = t.split('|')
                literals = [l.strip() for l in literals]
                literals.sort()
                normalized_terms.append("|".join(literals))
            else:
                normalized_terms.append(t)

        normalized_terms.sort()
        return " ∧ ".join(normalized_terms)


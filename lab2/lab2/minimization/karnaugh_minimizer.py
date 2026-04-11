"""Минимизация картами Карно для 2, 3, 4 и 5 переменных"""

from typing import List, Tuple, Dict, Set
from core.logic_function import LogicFunction


class KarnaughMinimizer:
    """Минимизация булевых функций с помощью карт Карно"""

    def minimize(self, function: LogicFunction) -> Tuple[str, str]:
        var_count = function.get_variable_count()

        if var_count == 0:
            return function.expression, "Функция-константа"
        elif var_count == 1:
            return self._minimize_1var(function), self._build_map_1var(function)
        elif var_count == 2:
            return self._minimize_2var(function), self._build_map_2var(function)
        elif var_count == 3:
            return self._minimize_3var(function), self._build_map_3var(function)
        elif var_count == 4:
            return self._minimize_4var(function), self._build_map_4var(function)
        elif var_count == 5:
            return self._minimize_5var(function), self._build_map_5var(function)
        else:
            return "Ошибка: карты Карно поддерживаются до 5 переменных", ""

    # ==================== 1 ПЕРЕМЕННАЯ ====================

    def _minimize_1var(self, function: LogicFunction) -> str:
        results = function.truth_matrix.get_result_column()
        if results[0] == 1 and results[1] == 1:
            return "1"
        elif results[0] == 0 and results[1] == 0:
            return "0"
        elif results[0] == 1 and results[1] == 0:
            return "!a"
        else:
            return "a"

    # ==================== 2 ПЕРЕМЕННЫЕ ====================

    def _minimize_2var(self, function: LogicFunction) -> str:
        # Строим карту 2x2
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1])] = res

        groups = self._find_groups_2var(kmap)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_2var(group, variables)
            if term and term not in terms:
                terms.append(term)

        if not terms:
            return "0"
        return " ∨ ".join(terms)

    def _find_groups_2var(self, kmap: Dict[Tuple[int, int], int]) -> List[Set[Tuple[int, int]]]:
        ones = [pos for pos, val in kmap.items() if val == 1]
        if not ones:
            return []

        groups = []
        used = set()

        # Группа 2x2 (все 4 клетки)
        all_cells = {(0, 0), (0, 1), (1, 0), (1, 1)}
        if all(kmap.get(cell, 0) == 1 for cell in all_cells):
            return [all_cells]

        # Группы по строкам 1x2
        for a in [0, 1]:
            if kmap.get((a, 0), 0) == 1 and kmap.get((a, 1), 0) == 1:
                group = {(a, 0), (a, 1)}
                groups.append(group)
                used.update(group)

        # Группы по столбцам 2x1
        for b in [0, 1]:
            if kmap.get((0, b), 0) == 1 and kmap.get((1, b), 0) == 1:
                group = {(0, b), (1, b)}
                if group not in groups:
                    groups.append(group)
                    used.update(group)

        # Одиночные
        for pos in ones:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

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

    # ==================== 3 ПЕРЕМЕННЫЕ ====================

    def _minimize_3var(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2])] = res

        groups = self._find_groups_3var(kmap, gray)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_3var(group, variables)
            if term and term not in terms:
                terms.append(term)

        if not terms:
            return "0"
        return " ∨ ".join(terms)

    def _find_groups_3var(self, kmap: Dict[Tuple[int, int, int], int], gray: List[Tuple[int, int]]) -> List[
        Set[Tuple[int, int, int]]]:
        ones = [pos for pos, val in kmap.items() if val == 1]
        if not ones:
            return []

        groups = []
        used = set()

        # Все 8 клеток
        if len(ones) == 8:
            return [set(ones)]

        # Группа 1x4 (целая строка по a)
        for a in [0, 1]:
            row = [(a, bc[0], bc[1]) for bc in gray]
            if all(kmap.get(cell, 0) == 1 for cell in row):
                group = set(row)
                groups.append(group)
                used.update(group)

        # Группа 2x2
        for col_start in range(4):
            c1 = gray[col_start]
            c2 = gray[(col_start + 1) % 4]
            cells = [
                (0, c1[0], c1[1]), (0, c2[0], c2[1]),
                (1, c1[0], c1[1]), (1, c2[0], c2[1])
            ]
            if all(kmap.get(cell, 0) == 1 for cell in cells):
                group = set(cells)
                if group not in groups:
                    groups.append(group)
                    used.update(group)

        # Группа 1x2
        for a in [0, 1]:
            for col_start in range(4):
                c1 = gray[col_start]
                c2 = gray[(col_start + 1) % 4]
                cells = {(a, c1[0], c1[1]), (a, c2[0], c2[1])}
                if all(kmap.get(cell, 0) == 1 for cell in cells):
                    if cells not in groups:
                        groups.append(cells)
                        used.update(cells)

        # Группа 2x1
        for bc in gray:
            cells = {(0, bc[0], bc[1]), (1, bc[0], bc[1])}
            if all(kmap.get(cell, 0) == 1 for cell in cells):
                if cells not in groups:
                    groups.append(cells)
                    used.update(cells)

        # Группа ПО СТОЛБЦАМ (c=1 и c=0)
        c1_cells = []
        c0_cells = []
        for a in [0, 1]:
            for idx, bc in enumerate(gray):
                if bc[1] == 1:
                    c1_cells.append((a, bc[0], bc[1]))
                else:
                    c0_cells.append((a, bc[0], bc[1]))

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

        # Одиночные
        for pos in ones:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

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

    # ==================== 4 ПЕРЕМЕННЫЕ ====================

    def _minimize_4var(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2], bits[3])] = res

        groups = self._find_groups_4var(kmap, gray)
        variables = function.variables
        terms = []
        for group in groups:
            term = self._term_from_group_4var(group, variables)
            if term and term not in terms:
                terms.append(term)

        if not terms:
            return "0"
        return " ∨ ".join(terms)

    def _find_groups_4var(self, kmap: Dict[Tuple[int, int, int, int], int], gray: List[Tuple[int, int]]) -> List[
        Set[Tuple[int, int, int, int]]]:
        ones = [pos for pos, val in kmap.items() if val == 1]
        if not ones:
            return []

        if len(ones) == 16:
            return [set(ones)]

        groups = []
        used = set()

        # Все возможные прямоугольники
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

        # Одиночные
        for pos in ones:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

    def _term_from_group_4var(self, group: Set[Tuple[int, int, int, int]], vars_list: List[str]) -> str:
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

    # ==================== 5 ПЕРЕМЕННЫХ ====================

    def _minimize_5var(self, function: LogicFunction) -> str:
        gray = [(0, 0), (0, 1), (1, 1), (1, 0)]
        kmap = {}
        for bits, res in function.truth_matrix:
            kmap[(bits[0], bits[1], bits[2], bits[3], bits[4])] = res

        # Разделяем на два слоя
        layer0 = {}
        layer1 = {}
        for (a, b, c, d, e), res in kmap.items():
            if a == 0:
                layer0[(b, c, d, e)] = res
            else:
                layer1[(b, c, d, e)] = res

        # Находим группы в каждом слое
        groups0 = self._find_groups_4var_from_dict(layer0, gray)
        groups1 = self._find_groups_4var_from_dict(layer1, gray)

        variables = function.variables
        a_var = variables[0]
        rest_vars = variables[1:]

        terms = set()

        # Группы только в слое 0
        for group in groups0:
            term = self._term_from_group_4var(group, rest_vars)
            if term and term != "1":
                # Проверяем, есть ли такая же группа в слое 1
                found_in_layer1 = False
                for g1 in groups1:
                    t1 = self._term_from_group_4var(g1, rest_vars)
                    if t1 == term:
                        found_in_layer1 = True
                        break

                if found_in_layer1:
                    # Общая группа - a уходит
                    terms.add(term)
                else:
                    # Только в слое 0
                    terms.add(f"!{a_var} & {term}" if '&' in term else f"!{a_var} & {term}")

        # Группы только в слое 1
        for group in groups1:
            term = self._term_from_group_4var(group, rest_vars)
            if term and term != "1":
                # Проверяем, есть ли такая же группа в слое 0
                found_in_layer0 = False
                for g0 in groups0:
                    t0 = self._term_from_group_4var(g0, rest_vars)
                    if t0 == term:
                        found_in_layer0 = True
                        break

                if not found_in_layer0:
                    # Только в слое 1
                    terms.add(f"{a_var} & {term}" if '&' in term else f"{a_var} & {term}")

        if not terms:
            return "0"

        result = " ∨ ".join(sorted(terms))
        # Упрощаем: убираем лишние скобки
        result = result.replace("& (", "&(")
        return result

    def _find_groups_4var_from_dict(self, layer: Dict[Tuple[int, int, int, int], int], gray: List[Tuple[int, int]]) -> \
    List[Set[Tuple[int, int, int, int]]]:
        """Находит группы в одном слое 4-переменной карты"""
        ones = [pos for pos, val in layer.items() if val == 1]
        if not ones:
            return []

        if len(ones) == 16:
            return [set(ones)]

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

        for pos in ones:
            if pos not in used:
                groups.append({pos})

        return self._deduplicate(groups)

    def _term_from_group_4var(self, group: Set[Tuple[int, int, int, int]], vars_list: List[str]) -> str:
        """Преобразует группу в терм для 4 переменных"""
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
        return f"Карта Карно (1):\n  0 1\na {r[0]} {r[1]}"

    def _build_map_2var(self, function: LogicFunction) -> str:
        values = {}
        for bits, res in function.truth_matrix:
            values[(bits[0], bits[1])] = res
        lines = ["Карта Карно (2):", "    b0 b1"]
        for a in [0, 1]:
            lines.append(f"a{a}  {values.get((a, 0), 0)}  {values.get((a, 1), 0)}")
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
            "│                                                                                │",
            "│   Слой a = 0                                                                   │",
            "│                                                                                │",
            "├──────────┬──────┬──────┬──────┬──────┬─────────────────────────────────────────┤",
            "│  bc \\ de │ 00   │ 01   │ 11   │ 10   │                                         │",
            "├──────────┼──────┼──────┼──────┼──────┼─────────────────────────────────────────┤"
        ]
        for b, c in gray:
            row = f"│  {b}{c}    │"
            for d, e in gray:
                row += f"  {values.get((0, b, c, d, e), 0)}   │"
            row += "                                         │"
            lines.append(row)
        lines.append("├──────────┴──────┴──────┴──────┴──────┴─────────────────────────────────────────┤")
        lines.append("│                                                                                │")
        lines.append("│   Слой a = 1                                                                   │")
        lines.append("│                                                                                │")
        lines.append("├──────────┬──────┬──────┬──────┬──────┬─────────────────────────────────────────┤")
        for b, c in gray:
            row = f"│  {b}{c}    │"
            for d, e in gray:
                row += f"  {values.get((1, b, c, d, e), 0)}   │"
            row += "                                         │"
            lines.append(row)
        lines.append("└──────────┴──────┴──────┴──────┴──────┴─────────────────────────────────────────┘")
        lines.append("\nПорядок bc и de: код Грея (00,01,11,10)")
        return "\n".join(lines)
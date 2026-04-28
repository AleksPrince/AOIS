from typing import Dict
from core.logic_function import LogicFunction
from .polynomial_builder import ZhegalkinBuilder


class PostClassesChecker:
    def __init__(self):
        self._poly_builder = None

    def _get_poly_builder(self):
        if self._poly_builder is None:
            self._poly_builder = ZhegalkinBuilder()
        return self._poly_builder

    def check_all(self, function: LogicFunction) -> Dict[str, bool]:
        return {
            'T0': self.is_t0(function),
            'T1': self.is_t1(function),
            'S': self.is_self_dual(function),
            'M': self.is_monotonic(function),
            'L': self.is_linear(function)
        }

    def is_t0(self, function: LogicFunction) -> bool:
        if not function.truth_matrix:
            return False
        return function.truth_matrix.get_result_column()[0] == 0

    def is_t1(self, function: LogicFunction) -> bool:
        if not function.truth_matrix:
            return False
        return function.truth_matrix.get_result_column()[-1] == 1

    def is_self_dual(self, function: LogicFunction) -> bool:
        results = function.truth_matrix.get_result_column()
        count = len(results)
        if count == 0:
            return False
        for i in range(count // 2):
            if results[i] == results[count - 1 - i]:
                return False
        return True

    def is_monotonic(self, function: LogicFunction) -> bool:
        if not function.has_variables():
            return True
        var_count = len(function.variables)
        results = function.truth_matrix.get_result_column()
        table = list(function.truth_matrix)
        for i in range(len(table)):
            for j in range(len(table)):
                bits_i = table[i][0]
                bits_j = table[j][0]
                if all(bits_i[k] <= bits_j[k] for k in range(var_count)):
                    if results[i] > results[j]:
                        return False
        return True

    def is_linear(self, function: LogicFunction) -> bool:
        if not function.has_variables():
            return True
        polynomial = self._get_poly_builder().build(function)
        return '&' not in polynomial or function.get_variable_count() <= 1
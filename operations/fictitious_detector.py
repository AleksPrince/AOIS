from typing import List, Set
from core.logic_function import LogicFunction


class FictitiousDetector:
    def find_fictitious(self, function: LogicFunction) -> List[str]:
        if function.get_variable_count() <= 1:
            return []
        fictitious = []
        for idx, var_name in enumerate(function.variables):
            if self._is_fictitious(function, idx):
                fictitious.append(var_name)
        return fictitious

    def find_essential(self, function: LogicFunction) -> List[str]:
        if function.get_variable_count() == 0:
            return []
        all_vars = set(function.variables)
        fictitious = set(self.find_fictitious(function))
        return list(all_vars - fictitious)

    def _is_fictitious(self, function: LogicFunction, var_index: int) -> bool:
        for bits, result in function.truth_matrix:
            opposite = list(bits)
            opposite[var_index] = 1 - opposite[var_index]
            try:
                opposite_result = function.truth_matrix.get_value(tuple(opposite))
                if result != opposite_result:
                    return False
            except ValueError:
                continue
        return True
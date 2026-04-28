from typing import Tuple
from core.logic_function import LogicFunction


class NumericConverter:
    def convert_to_numeric(self, function: LogicFunction) -> Tuple[str, str]:
        if not function.has_variables():
            result = function.truth_matrix.get_result_column()
            if result and result[0] == 1:
                return "∨(все)", "∧()"
            return "∨()", "∧(все)"

        one_idx = function.truth_matrix.get_indices_where_one()
        zero_idx = function.truth_matrix.get_indices_where_zero()
        sdnf_form = f"∨({','.join(map(str, one_idx))})" if one_idx else "∨()"
        sknf_form = f"∧({','.join(map(str, zero_idx))})" if zero_idx else "∧()"
        return sdnf_form, sknf_form

    def get_index_representation(self, function: LogicFunction) -> str:
        results = function.truth_matrix.get_result_column()
        if not results:
            return "()_2 = 0_10"
        vector_str = ','.join(map(str, results))
        binary_str = ''.join(map(str, results))
        decimal_value = int(binary_str, 2)
        return f"({vector_str})_2 = {decimal_value}_10"
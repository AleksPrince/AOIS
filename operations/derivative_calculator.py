from typing import List, Dict
from itertools import product
from core.logic_function import LogicFunction
from core.expression_processor import ExpressionProcessor


class DerivativeCalculator:
    def __init__(self):
        self._processor = ExpressionProcessor()

    def partial_derivative(self, function: LogicFunction, variable: str) -> str:
        if variable not in function.variables:
            raise ValueError(f"Переменная '{variable}' не найдена")
        return self._compute_derivative_table(function, [variable])

    def mixed_derivative(self, function: LogicFunction, variables: List[str]) -> str:
        if not variables:
            return function.expression
        for var in variables:
            if var not in function.variables:
                raise ValueError(f"Переменная '{var}' не найдена")
        return self._compute_derivative_table(function, variables)

    def _compute_derivative_table(self, function: LogicFunction, vars_list: List[str]) -> str:
        remaining_vars = [v for v in function.variables if v not in vars_list]

        if not remaining_vars:
            all_bits_count = 1 << len(vars_list)
            results = []
            for mask in range(all_bits_count):
                values = {}
                for i, var in enumerate(vars_list):
                    bit = (mask >> (len(vars_list) - 1 - i)) & 1
                    values[var] = bit
                result = self._processor.evaluate(function.expression, values)
                results.append(result)
            xor_result = 0
            for r in results:
                xor_result ^= r
            return '1' if xor_result else '0'

        truth_values = []
        var_names = sorted(remaining_vars)

        for bits in product([0, 1], repeat=len(var_names)):
            base_values = dict(zip(var_names, bits))
            hypercube_size = 1 << len(vars_list)
            xor_sum = 0
            for mask in range(hypercube_size):
                test_values = base_values.copy()
                for i, var in enumerate(vars_list):
                    bit = (mask >> (len(vars_list) - 1 - i)) & 1
                    test_values[var] = bit
                f_val = self._processor.evaluate(function.expression, test_values)
                xor_sum ^= f_val
            truth_values.append(xor_sum)

        sdnf_terms = []
        for idx, val in enumerate(truth_values):
            if val == 1:
                term_parts = []
                for i, var in enumerate(var_names):
                    bit = (idx >> (len(var_names) - 1 - i)) & 1
                    if bit == 1:
                        term_parts.append(var)
                    else:
                        term_parts.append(f"!{var}")
                sdnf_terms.append('&'.join(term_parts))

        if not sdnf_terms:
            return "0"
        if len(sdnf_terms) == 1:
            return sdnf_terms[0]

        simplified = self._simplify_dnf(sdnf_terms)
        return simplified

    def _simplify_dnf(self, terms: List[str]) -> str:
        if len(terms) <= 1:
            return terms[0] if terms else "0"

        changed = True
        current_terms = set(terms)

        while changed:
            changed = False
            new_terms = set()
            used = set()
            term_list = list(current_terms)

            for i in range(len(term_list)):
                for j in range(i + 1, len(term_list)):
                    t1 = term_list[i]
                    t2 = term_list[j]

                    lits1 = set(t1.split('&')) if '&' in t1 else {t1}
                    lits2 = set(t2.split('&')) if '&' in t2 else {t2}

                    diff = lits1.symmetric_difference(lits2)

                    if len(diff) == 2:
                        diff_list = list(diff)
                        a, b = diff_list[0], diff_list[1]
                        if (a[0] == '!' and a[1:] == b) or (b[0] == '!' and b[1:] == a):
                            common = lits1.intersection(lits2)
                            if common:
                                new_term = '&'.join(sorted(common))
                                new_terms.add(new_term)
                                used.add(t1)
                                used.add(t2)
                                changed = True

            for t in term_list:
                if t not in used:
                    new_terms.add(t)

            if new_terms:
                current_terms = new_terms
            else:
                break

        if not current_terms:
            return "0"
        if len(current_terms) == 1:
            return list(current_terms)[0]
        return " ∨ ".join(sorted(current_terms))

    def all_derivatives(self, function: LogicFunction) -> Dict[str, str]:
        result = {}
        vars_list = function.variables

        for var in vars_list:
            result[f"∂F/∂{var}"] = self.partial_derivative(function, var)

        if len(vars_list) >= 2:
            for i in range(len(vars_list)):
                for j in range(i + 1, len(vars_list)):
                    name = f"∂²F/∂{vars_list[i]}∂{vars_list[j]}"
                    result[name] = self.mixed_derivative(function, [vars_list[i], vars_list[j]])

        if len(vars_list) >= 3:
            for i in range(len(vars_list)):
                for j in range(i + 1, len(vars_list)):
                    for k in range(j + 1, len(vars_list)):
                        name = f"∂³F/∂{vars_list[i]}∂{vars_list[j]}∂{vars_list[k]}"
                        result[name] = self.mixed_derivative(function, [vars_list[i], vars_list[j], vars_list[k]])

        return result
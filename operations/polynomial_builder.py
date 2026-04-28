from typing import List
from core.logic_function import LogicFunction


class ZhegalkinBuilder:
    def build(self, function: LogicFunction) -> str:
        vector = function.truth_matrix.get_result_column()
        var_count = function.get_variable_count()
        coeffs = self._compute_coefficients(vector, var_count)
        monomials = self._coefficients_to_monomials(coeffs, function.variables, var_count)
        return self._format_polynomial(monomials)

    def _compute_coefficients(self, vector: List[int], dimension: int) -> List[int]:
        coeffs = vector.copy()
        for bit in range(dimension):
            bit_mask = 1 << bit
            for mask in range(1 << dimension):
                if mask & bit_mask:
                    coeffs[mask] ^= coeffs[mask ^ bit_mask]
        return coeffs

    def _coefficients_to_monomials(self, coeffs: List[int], variables: List[str], var_count: int) -> List[str]:
        monomials = []
        for idx, coeff in enumerate(coeffs):
            if coeff == 1:
                if idx == 0:
                    monomials.append("1")
                else:
                    parts = []
                    for i in range(var_count):
                        bit_pos = var_count - 1 - i
                        if idx & (1 << bit_pos):
                            parts.append(variables[i])
                    if parts:
                        if len(parts) == 1:
                            monomials.append(parts[0])
                        else:
                            monomials.append('&'.join(parts))
        monomials.sort(key=lambda m: (0 if m == '1' else 1 if '&' not in m else 2, m))
        return monomials

    def _format_polynomial(self, monomials: List[str]) -> str:
        if not monomials:
            return "0"
        return " ⊕ ".join(monomials)
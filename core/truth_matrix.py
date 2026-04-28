from itertools import product
from typing import List, Tuple, Iterator
from core.expression_processor import ExpressionProcessor


class TruthMatrix:
    """Таблица истинности"""

    def __init__(self, variables: List[str], expression: str, processor: ExpressionProcessor):
        self.variables = variables
        self.expression = expression
        self.processor = processor
        self._matrix = self._build_matrix()

    def _build_matrix(self) -> List[Tuple[Tuple[int, ...], int]]:
        matrix = []
        var_count = len(self.variables)
        if var_count == 0:
            return [((), 1 if self.expression == '1' else 0)]
        for bits in product([0, 1], repeat=var_count):
            values = dict(zip(self.variables, bits))
            result = self.processor.evaluate(self.expression, values)
            matrix.append((bits, result))
        return matrix

    def get_matrix(self) -> List[Tuple[Tuple[int, ...], int]]:
        return self._matrix.copy()

    def get_result_column(self) -> List[int]:
        return [res for _, res in self._matrix]

    def get_indices_where_one(self) -> List[int]:
        return [i for i, (_, res) in enumerate(self._matrix) if res == 1]

    def get_indices_where_zero(self) -> List[int]:
        return [i for i, (_, res) in enumerate(self._matrix) if res == 0]

    def get_sets_where_one(self) -> List[Tuple[int, ...]]:
        return [bits for bits, res in self._matrix if res == 1]

    def get_sets_where_zero(self) -> List[Tuple[int, ...]]:
        return [bits for bits, res in self._matrix if res == 0]

    def get_value(self, bits: Tuple[int, ...]) -> int:
        for b, res in self._matrix:
            if b == bits:
                return res
        raise ValueError(f"Набор {bits} не найден")

    def __len__(self) -> int:
        return len(self._matrix)

    def __iter__(self):
        return iter(self._matrix)
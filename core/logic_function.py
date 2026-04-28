from typing import Optional
from core.expression_processor import ExpressionProcessor
from core.truth_matrix import TruthMatrix
from utils.expression_validator import ExpressionValidator


class LogicFunction:
    """Модель логической функции"""

    def __init__(self, expression: str, processor: Optional[ExpressionProcessor] = None):
        self.processor = processor or ExpressionProcessor()
        self.validator = ExpressionValidator()

        expr_clean = expression.replace(' ', '')
        if expr_clean in ['0', '1']:
            self.raw_expression = expression
            self.variables = []
            self.truth_matrix = TruthMatrix(self.variables, expression, self.processor)
            return

        if not self.validator.is_valid(expression):
            raise ValueError(f"Некорректное выражение: {expression}")

        self.raw_expression = expression
        self.variables = self.validator.get_variables(expression)
        self.truth_matrix = TruthMatrix(self.variables, expression, self.processor)

    @property
    def expression(self) -> str:
        return self.raw_expression

    def get_variable_count(self) -> int:
        return len(self.variables)

    def has_variables(self) -> bool:
        return len(self.variables) > 0
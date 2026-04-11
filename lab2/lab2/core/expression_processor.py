from typing import Dict, List
from utils.expression_validator import ExpressionValidator


class ExpressionProcessor:
    """Рекурсивный парсер логических выражений"""

    def __init__(self):
        self.validator = ExpressionValidator()
        self._tokens = []
        self._position = 0

    def evaluate(self, expression: str, values: Dict[str, int]) -> int:
        expr = expression.replace(' ', '')
        if expr == '0':
            return 0
        if expr == '1':
            return 1

        substituted = expr
        for var, val in values.items():
            substituted = substituted.replace(var, str(val))

        try:
            result = self._parse_expression(substituted)
            return 1 if result else 0
        except Exception:
            return 0

    def _parse_expression(self, expr: str) -> bool:
        self._tokens = self._tokenize(expr)
        self._position = 0
        return self._parse_implication()

    def _tokenize(self, expr: str) -> List[str]:
        tokens = []
        i = 0
        length = len(expr)
        while i < length:
            ch = expr[i]
            if ch in '01':
                tokens.append(ch)
            elif ch == '!':
                tokens.append('NOT')
            elif ch == '&':
                tokens.append('AND')
            elif ch == '|':
                tokens.append('OR')
            elif ch == '-':
                if i + 1 < length and expr[i + 1] == '>':
                    tokens.append('IMPLY')
                    i += 1
            elif ch == '~':
                tokens.append('EQ')
            elif ch == '(':
                tokens.append('(')
            elif ch == ')':
                tokens.append(')')
            else:
                if ch.isdigit() or ch.isalpha():
                    tokens.append(ch)
            i += 1
        return tokens

    def _parse_implication(self) -> bool:
        left = self._parse_equivalence()
        while self._position < len(self._tokens) and self._tokens[self._position] == 'IMPLY':
            self._position += 1
            right = self._parse_equivalence()
            left = (not left) or right
        return left

    def _parse_equivalence(self) -> bool:
        left = self._parse_or()
        while self._position < len(self._tokens) and self._tokens[self._position] == 'EQ':
            self._position += 1
            right = self._parse_or()
            left = (left == right)
        return left

    def _parse_or(self) -> bool:
        left = self._parse_and()
        while self._position < len(self._tokens) and self._tokens[self._position] == 'OR':
            self._position += 1
            right = self._parse_and()
            left = left or right
        return left

    def _parse_and(self) -> bool:
        left = self._parse_not()
        while self._position < len(self._tokens) and self._tokens[self._position] == 'AND':
            self._position += 1
            right = self._parse_not()
            left = left and right
        return left

    def _parse_not(self) -> bool:
        if self._position < len(self._tokens) and self._tokens[self._position] == 'NOT':
            self._position += 1
            return not self._parse_not()
        return self._parse_atom()

    def _parse_atom(self) -> bool:
        if self._position >= len(self._tokens):
            return False
        token = self._tokens[self._position]
        if token == '(':
            self._position += 1
            result = self._parse_implication()
            if self._position < len(self._tokens) and self._tokens[self._position] == ')':
                self._position += 1
            return result
        self._position += 1
        return token == '1'
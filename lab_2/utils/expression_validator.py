import re
from typing import List, Set


class ExpressionValidator:
    VALID_VARS: Set[str] = {'a', 'b', 'c', 'd', 'e'}
    VALID_OPS: Set[str] = {'&', '|', '!', '-', '>', '~', '(', ')', '¬', '→', '≡', '+'}
    CONSTANTS: Set[str] = {'0', '1'}

    @classmethod
    def is_valid(cls, expression: str) -> bool:
        if not expression or not expression.strip():
            return False
        expr = expression.replace(' ', '')
        if expr in cls.CONSTANTS:
            return True
        if not cls._check_allowed_chars(expr):
            return False
        if not cls._check_balanced_parentheses(expr):
            return False
        if not cls._check_operator_placement(expr):
            return False
        return True

    @classmethod
    def _check_allowed_chars(cls, expr: str) -> bool:
        i = 0
        length = len(expr)
        while i < length:
            ch = expr[i]
            if ch.isalpha():
                if ch not in cls.VALID_VARS and ch not in cls.CONSTANTS:
                    return False
            elif ch not in cls.VALID_OPS:
                return False
            if ch == '-' and i + 1 < length and expr[i + 1] == '>':
                i += 1
            i += 1
        return True

    @classmethod
    def _check_balanced_parentheses(cls, expr: str) -> bool:
        balance = 0
        for ch in expr:
            if ch == '(':
                balance += 1
            elif ch == ')':
                balance -= 1
                if balance < 0:
                    return False
        return balance == 0

    @classmethod
    def _check_operator_placement(cls, expr: str) -> bool:
        if expr[0] in '&|~→≡+':
            return False
        if expr[-1] in '&|!-~→≡+':
            return False
        i = 0
        while i < len(expr) - 1:
            curr = expr[i]
            nxt = expr[i + 1]
            if curr in '&|~→≡+' and nxt in '&|~→≡+':
                return False
            i += 1
        return True

    @classmethod
    def get_variables(cls, expression: str) -> List[str]:
        expr = expression.replace(' ', '')
        found = set(re.findall(r'[a-e]', expr))
        return sorted(list(found))
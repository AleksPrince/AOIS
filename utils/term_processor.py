"""Обработчик логических термов"""

from typing import List


class TermProcessor:
    """Обработчик логических термов"""

    @staticmethod
    def split_into_literals(term: str) -> List[str]:
        """Разбивает терм на литералы"""
        cleaned = term.strip('()')
        if '&' in cleaned:
            return cleaned.split('&')
        elif '|' in cleaned:
            return cleaned.split('|')
        return [cleaned]

    @staticmethod
    def extract_dnf_terms(dnf_expr: str) -> List[str]:
        """Извлекает конъюнктивные термы из ДНФ"""
        if '∨' in dnf_expr:
            terms = dnf_expr.split(' ∨ ')
        elif '|' in dnf_expr:
            terms = dnf_expr.split(' | ')
        elif '+' in dnf_expr:
            terms = dnf_expr.split(' + ')
        else:
            terms = [dnf_expr]
        return [t.strip('()') for t in terms]

    @staticmethod
    def extract_cnf_terms(cnf_expr: str) -> List[str]:
        """Извлекает дизъюнктивные термы из КНФ"""
        if '∧' in cnf_expr:
            terms = cnf_expr.split(' ∧ ')
        elif '&' in cnf_expr:
            terms = cnf_expr.split(' & ')
        else:
            terms = [cnf_expr]
        return [t.strip('()') for t in terms]

    @staticmethod
    def join_literals(literals: List[str], operator: str) -> str:
        """Объединяет литералы в терм с оператором"""
        if not literals:
            return ''
        if len(literals) == 1:
            return literals[0]
        return f'({operator.join(literals)})'

    @staticmethod
    def get_variable_name(literal: str) -> str:
        """Извлекает имя переменной из литерала"""
        return literal.replace('!', '').replace('¬', '')

    @staticmethod
    def is_negated(literal: str) -> bool:
        """Проверяет, является ли литерал отрицанием"""
        return literal.startswith('!') or literal.startswith('¬')
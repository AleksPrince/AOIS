from typing import List, Tuple
from core.logic_function import LogicFunction
from utils.term_processor import TermProcessor


class NormalFormsBuilder:
    def __init__(self, term_proc: TermProcessor = None):
        self.term_proc = term_proc or TermProcessor()

    def build(self, function: LogicFunction) -> Tuple[str, str]:
        if not function.has_variables():
            result = function.truth_matrix.get_result_column()
            if result and result[0] == 1:
                return "1", "1"
            return "0", "0"

        sdnf_terms = self._build_sdnf_terms(function)
        sknf_terms = self._build_sknf_terms(function)

        sdnf_expr = self._format_sdnf(sdnf_terms, function.variables)
        sknf_expr = self._format_sknf(sknf_terms, function.variables)

        return sdnf_expr, sknf_expr

    def _build_sdnf_terms(self, function: LogicFunction) -> List[List[Tuple[str, bool]]]:
        terms = []
        for bits in function.truth_matrix.get_sets_where_one():
            term = []
            for var, bit in zip(function.variables, bits):
                term.append((var, bit == 0))  # True если нужно отрицание
            terms.append(term)
        return terms

    def _build_sknf_terms(self, function: LogicFunction) -> List[List[Tuple[str, bool]]]:
        terms = []
        for bits in function.truth_matrix.get_sets_where_zero():
            term = []
            for var, bit in zip(function.variables, bits):
                term.append((var, bit == 1))  # True если нужно отрицание
            terms.append(term)
        return terms

    def _format_sdnf(self, terms: List[List[Tuple[str, bool]]], variables: List[str]) -> str:
        if not terms:
            return "0"
        formatted = []
        for term in terms:
            literals = [f"!{var}" if neg else var for var, neg in term]
            formatted.append("&".join(literals))
        return " ∨ ".join(formatted)

    def _format_sknf(self, terms: List[List[Tuple[str, bool]]], variables: List[str]) -> str:
        if not terms:
            return "1"
        formatted = []
        for term in terms:
            literals = [f"!{var}" if neg else var for var, neg in term]
            formatted.append("|".join(literals))
        if len(formatted) == 1:
            return formatted[0]
        return " ∧ ".join(f"({t})" for t in formatted)
from typing import List, Tuple
from tabulate import tabulate
from core.logic_function import LogicFunction
from utils.term_processor import TermProcessor
from .glue_minimizer import GlueMinimizer


class TableMinimizer:
    def __init__(self):
        self.glue_minimizer = GlueMinimizer()
        self.term_proc = TermProcessor()

    def minimize(self, function: LogicFunction) -> Tuple[str, List[str], str]:
        minimized, stages = self.glue_minimizer.minimize(function)
        if minimized == '0' or minimized == '1':
            return minimized, stages, "Таблица не требуется"
        implicants = self.term_proc.extract_dnf_terms(minimized)
        ones = function.truth_matrix.get_sets_where_one()
        table_str = self._build_table(implicants, ones, function.variables)
        return minimized, stages, table_str

    def _build_table(self, implicants: List[str], ones: List[Tuple[int, ...]], variables: List[str]) -> str:
        if not ones:
            return "Нет наборов с результатом 1"
        headers = ['Импликанта'] + [''.join(str(b) for b in bits) for bits in ones]
        data = []
        for imp in implicants:
            row = [imp]
            for bits in ones:
                if self._covers(imp, bits, variables):
                    row.append('X')
                else:
                    row.append('')
            data.append(row)
        return tabulate(data, headers=headers, tablefmt='grid')

    def _covers(self, imp: str, bits: Tuple[int, ...], variables: List[str]) -> bool:
        literals = self.term_proc.split_into_literals(imp)
        vmap = dict(zip(variables, bits))
        for lit in literals:
            if lit.startswith('!'):
                if vmap.get(lit[1:]) != 0:
                    return False
            else:
                if vmap.get(lit) != 1:
                    return False
        return True
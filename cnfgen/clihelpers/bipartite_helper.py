from cnfgen.families.bipartite import BipartiteOddCycle

from .formula_helpers import FormulaHelper

class BipartiteCmdHelper(FormulaHelper):
    name = 'bipartite'
    description = 'bipartite vs odd cycle principle'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N', type=int, help="domain size")

    @staticmethod
    def build_cnf(args):
        return BipartiteOddCycle(args.N, False)

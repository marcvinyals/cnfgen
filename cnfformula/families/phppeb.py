#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cnfformula.cmdline import DirectedAcyclicGraphHelper
from cnfformula.cmdline import BipartiteGraphHelper

from cnfformula.cnf import CNF,disj
from cnfformula.families.pigeonhole import PigeonholePrinciple
from cnfformula.families.pebbling import PebblingFormula
from cnfformula.transformations.substitutions import XorSubstitution,FormulaLifting

import cnfformula.cmdline

@cnfformula.cmdline.register_cnfgen_subcommand
class PHPPEBCmdHelper(object):
    name='phppeb'
    description='pigeonhole + pebbling'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('pigeons',metavar='<pigeons>',type=int,help="Number of pigeons")
        parser.add_argument('holes',metavar='<holes>',type=int,help="Number of holes")
        DirectedAcyclicGraphHelper.setup_command_line(parser)

    @staticmethod
    def build_cnf(args):
        """Build a PHP formula according to the arguments

        Arguments:
        - `args`: command line options
        """
        D= DirectedAcyclicGraphHelper.obtain_graph(args)
        PHP = PigeonholePrinciple(args.pigeons,
                                  args.holes)
        Peb = PebblingFormula(D)
        #Peb = XorSubstitution(Peb,3)
        Peb = FormulaLifting(Peb,3)

        F = CNF()
        for x in PHP.variables():
            F.add_variable(x)
        for x in Peb.variables():
            F.add_variable(x)

        def moar_vars(clause):
            return disj(
                *F._check_and_compress_literals(
                    Peb._uncompress_literals(clause)
                ))

        F._add_compressed_constraints([
            c
            for c in PHP._constraints
        ])
        F._add_compressed_constraints([
            disj(
                *F._check_and_compress_literals(
                    Peb._uncompress_literals(c)
                ))
            for c in Peb._constraints
            if not c == disj(1)
        ])
        return F

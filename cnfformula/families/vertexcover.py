#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cnfformula.cnf import CNF

from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cmdline  import register_cnfgen_subcommand
from cnfformula.families import register_cnf_generator

from cnfformula.graphs import enumerate_vertices,neighbors

@register_cnf_generator
def Roth(n):
    F=CNF()

    def X(i):
        return "x_{{{0}}}".format(i)

    # Create variables
    for i in range(1,n+1):
        F.add_variable(X(i))

    # Conditions
    for i in range(1,n+1):
        for k in range(i+1,n+1):
            for j in range(k+1,n+1):
                if (i+j!=2*k): continue
                F.add_clause([ (False,X(i)), (False,X(j)), (False,X(k)) ])
        
    return F

@register_cnfgen_subcommand
class VertexCoverCmdHelper(object):
    """Command line helper for k-dominating set
    """
    name='roth'
    description='Roth Set'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for dominating set formula

        Arguments:
        - `parser`: parser to load with options.
        """
        parser.add_argument('n',type=int)


    @staticmethod
    def build_cnf(args):
        """Build the k-dominating set formula

        Arguments:
        - `args`: command line options
        """

        return Roth(args.n)

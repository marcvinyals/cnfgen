#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Formulas that encode coloring related problems
"""

from cnfformula.csp import CSP

from cnfformula.cmdline import SimpleGraphHelper

from cnfformula.cmdline  import register_cnfgen_subcommand
from cnfformula.families import register_cnf_generator

from cnfformula.graphs import enumerate_vertices,neighbors

@register_cnf_generator
def DominatingSetOPB(G):
    F=CSP()

    def D(v):
        return "x_{{{0}}}".format(v)

    def N(v):
        return tuple(sorted([ v ] + [ u for u in G.neighbors(v) ]))

    # Fix the vertex order
    V=enumerate_vertices(G)

    avgdegree=sum(len(set(N(v))) for v in V)/len(V)
    d=len(V)/avgdegree
    
    # Create variables
    for v in V:
        F.add_variable(D(v))

    # Not too many true variables
    for c in F.less_or_equal_constraint([D(v) for v in V],d):
        F.add_clause(c)

    # Every neighborhood must have a true D variable
    neighborhoods = sorted( set(N(v) for v in V) )
    for N in neighborhoods:
        F.add_clause([ (True,D(v)) for v in N])
        
    return F

@register_cnfgen_subcommand
class DominatingSetCmdHelper(object):
    """Command line helper for k-dominating set
    """
    name='domsetopb'
    description='k-Dominating set'

    @staticmethod
    def setup_command_line(parser):
        """Setup the command line options for dominating set formula

        Arguments:
        - `parser`: parser to load with options.
        """
        SimpleGraphHelper.setup_command_line(parser)


    @staticmethod
    def build_cnf(args):
        """Build the k-dominating set formula

        Arguments:
        - `args`: command line options
        """
        G = SimpleGraphHelper.obtain_graph(args)
        return DominatingSetOPB(G)

#!/usr/bin/env python
# -*- coding:utf-8 -*-


import random


from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

from ..cnf import CNF


@register_cnf_transformation
def Guarding(cnf):
    out=CNF(header='')

    out.header="Guarding of:\n\n"+cnf.header

    variables=list(cnf.variables())
    N=len(variables)
    M=len(cnf)

    for v in variables:
        out.add_variable(v)

    for c in cnf.clauses():
        varsc = set([x for (_,x) in c])
        newvariable = random.choice(variables)
        while newvariable in varsc:
            newvariable = random.choice(variables)
        c1 = c + [(True,newvariable)]
        out.add_clause(c1)
        c2 = c + [(False,newvariable)]
        out.add_clause(c2)

    assert out._check_coherence(force=True)
    return out


@register_cnf_transformation_subcommand
class GuardingCmd:
    """Guarding
    """
    name='guard'
    description='Replace each clause C with C v x and C v ~x'

    @staticmethod
    def setup_command_line(parser):
        pass
    
    @staticmethod
    def transform_cnf(F,args):
        return Guarding(F)

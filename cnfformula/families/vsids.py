#!/usr/bin/env python
# -*- coding:utf-8 -*-

from cnfformula.cnf import CNF

import cnfformula.cmdline
import cnfformula.families

from cnfformula.graphs import neighbors
from itertools import product
import random

@cnfformula.families.register_cnf_generator
def VsidsFormula(n):
    pigeons=n+1
    holes=n
    
    def php_var_name(p,h):
        return 'p_{{{0},{1}}}'.format(p,h)

    vsids=CNF()
    vsids.header="VSIDS formula with parameter {0}\n".format(n)\
        + vsids.header

    mapping=vsids.unary_mapping(
        xrange(1,pigeons+1),
        xrange(1,holes+1),
        var_name=php_var_name,
        injective = True,
        functional = False,
        surjective = False)

    m=n*n
    k=4
    xx = [php_var_name(p,h) for p in range(1,pigeons+1) for h in range(1,holes+1)]
    xx1 = [php_var_name(p,h) for p in range(1,pigeons+1) for h in range(1,holes//2+1)]
    xx2 = [php_var_name(p,h) for p in range(1,pigeons+1) for h in range(holes//2+1,holes+1)]
    yy1 = ["y"+str(i) for i in range(1,m+1)]
    yy2 = ["yy"+str(i) for i in range(1,m+1)]
    zz = ["z"+str(i) for i in range(1,k+1)]

    def add_variables12xz21():
        for y in yy1[0:len(yy1)//2]:
            vsids.add_variable(y)
        for y in yy2[0:len(yy2)//2]:
            vsids.add_variable(y)
        for x in xx:
            vsids.add_variable(x)
        for z in zz:
            vsids.add_variable(z)
        for y in yy2[len(yy2)//2:]:
            vsids.add_variable(y)
        for y in yy1[len(yy1)//2:]:
            vsids.add_variable(y)
    add_variables12xz21()

    for c in mapping.clauses():
        vsids.add_clause_unsafe(c)

    def add_pitfall_seq(y,S):
        c=[(True,y)]
        for x in S:
            vsids.add_clause(c+[(False,x)])
            c.append((True,x))
        vsids.add_clause(c)

    def add_pitfall_par(y,S):
        c=[(True,y)]
        for x in S:
            vsids.add_clause([(True,y)]+[(False,x)])
            c.append((True,x))
        vsids.add_clause(c)

    def add_pitfall(y,S):
        add_pitfall_seq(y,S)

    def add_clauses1212():
        for y in yy1:
            add_pitfall(y,xx1)
        for y in yy2:
            add_pitfall(y,xx2)

    def add_clauses23rand():
        for y in yy1+yy2:
            add_pitfall(y,random.sample(xx,2*len(xx)//3))

    add_clauses23rand()

    for polarity in product((True,False),repeat=k):
        vsids.add_clause(zip(polarity,zz))

    return vsids

@cnfformula.cmdline.register_cnfgen_subcommand
class VsidsCmdHelper(object):    
    name='vsids'
    description='hard VSIDS formula'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('n',metavar='<n>',type=int,help="PHP parameter")

    @staticmethod
    def build_cnf(args):
        return VsidsFormula(args.n)

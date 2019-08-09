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

import networkx
from cnfformula.families.tseitin import TseitinFormula
from itertools import combinations

@cnfformula.families.register_cnf_generator
def VsidsFormulaTs(n,d,m,l,k):
    vsids=CNF()
    graph=networkx.random_regular_graph(d,n)
    charge=[1]+[0]*(n-1)
    ts = TseitinFormula(graph,charge)

    X = list(ts.variables())
    for x in X:
        vsids.add_variable(x)

    def yname(j,i):
        return "y_{}_{}".format(j,i)

    def zname(j,i):
        return "z_{}_{}".format(j,i)

    def tname(y,z,i):
        return "t_{}_{}_{}".format(y,z,i)

    Y = [0]*k
    Z = [0]*k
    for j in range(k):
        Y[j] = [yname(j,i) for i in range(m)]
        Z[j] = [zname(j,i) for i in range(l)]

    # Ts_j
    for j in range(k):
        append = [(True,z) for z in Z[j]]
        for C in ts:
            vsids.add_clause(C + append)

    # Psi
    def pitfall1(y,S):
        C = [(True,y)]
        for s in S:
            vsids.add_clause(C+[(False,s)])
            C.append((True,s))

    for j in range(k):
        for y in range(m):
            #pitfall1(yname(j,y),X+Z[j])
            pass

    def pitfall2(y1,y2,S):
        C = [(True,y1),(True,y2)]
        for s in S:
            vsids.add_clause(C+[(False,s)])
            C.append((True,s))

    for j in range(k):
        for (y1,y2) in combinations(range(m),2):
            pitfall2(yname(j,y1),yname(j,y2),X+Z[j])
            #pass

    # Delta
    def tail1(z):
        vsids.add_clause([(True,tname('',z,1)),(False,z)])
        vsids.add_clause([(False,tname('',z,1)),(False,z)])

    for j in range(k):
        for z in Z[j]:
            #tail1(z)
            pass

    def tail2(y,z):
        vsids.add_clause([(True,tname(y,z,1)),(True,tname(y,z,3)),(False,y)])
        vsids.add_clause([(True,tname(y,z,2)),(False,tname(y,z,3)),(False,y)])
        vsids.add_clause([(False,tname(y,z,1)),(False,z),(False,y)])
        vsids.add_clause([(False,tname(y,z,2)),(False,z),(False,y)])

    for j in range(k):
        for (y,z) in product(Y[j],Z[j]):
            tail2(y,z)
            #pass

    # Gamma
    vsids.add_clause([(False,yname(j,i)) for i in range(m) for j in range(k)])

    for i in range(m):
        vsids.add_clause([(False,yname(j,i)) for j in range(k)])

    for i in range(0,m,2):
        #vsids.add_clause([(False,yname(j,i)) for j in range(k)] +
        #                 [(False,yname(j,i+1)) for j in range(k)])
        pass

    return vsids

@cnfformula.cmdline.register_cnfgen_subcommand
class VsidsCmdHelper(object):
    name='vsidsts'
    description='hard VSIDS formula'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('n',metavar='<n>',type=int,help="n")
        parser.add_argument('d',metavar='<d>',type=int,help="d")
        parser.add_argument('m',metavar='<m>',type=int,help="m")
        parser.add_argument('l',metavar='<l>',type=int,help="l")
        parser.add_argument('k',metavar='<k>',type=int,help="k")

    @staticmethod
    def build_cnf(args):
        return VsidsFormulaTs(args.n, args.d, args.m, args.l, args.k)
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
def VsidsFormulaTs(n,d,m,l,k,long_gamma,split_gamma):
    hardenedPsi=True
    sequentialPsi=False
    hardenedDelta=True
    completeTautology=False

    vsids=CNF()
    graph=networkx.random_regular_graph(d,n)
    charge=[1]+[0]*(n-1)
    ts = TseitinFormula(graph,charge)

    def yname(j,i):
        return "y_{}_{}".format(j,i)

    def zname(j,i):
        return "z_{}_{}".format(j,i)

    def tname(y,z,i):
        return "t_{}_{}_{}".format(y,z,i)

    def aname(i):
        return "a_{}".format(i)

    X = list(ts.variables())

    Y = [0]*k
    Z = [0]*k
    for j in range(k):
        Y[j] = [yname(j,i) for i in range(m)]
        Z[j] = [zname(j,i) for i in range(l)]

    for YY in Y:
        for y in YY:
            vsids.add_variable(y)

    for x in X:
        vsids.add_variable(x)


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

    def pitfall2(y1,y2,S):
        C = [(True,y1),(True,y2)]
        for s in S:
            vsids.add_clause(C+[(False,s)])
            C.append((True,s))

    if hardenedPsi:
        for YY in Y:
            if sequentialPsi:
                for y1 in range(0,m,2):
                    y2 = y1+1
                    pitfall2(YY[y1],YY[y2],X+Z[j])
            else:
                for (y1,y2) in combinations(range(m),2):
                    pitfall2(YY[y1],YY[y2],X+Z[j])
    else:
        for YY in Y:
            for y in YY:
                pitfall1(y,X+Z[j])

    # Delta
    def tail1(z):
        vsids.add_clause([(True,tname('',z,1)),(False,z)])
        vsids.add_clause([(False,tname('',z,1)),(False,z)])

    def tail2(y,z):
        vsids.add_clause([(True,tname(y,z,1)),(True,tname(y,z,3))])
        vsids.add_clause([(True,tname(y,z,2)),(False,tname(y,z,3))])
        vsids.add_clause([(False,tname(y,z,1)),(False,z),(False,y)])
        vsids.add_clause([(False,tname(y,z,2)),(False,z),(False,y)])

    if hardenedDelta:
        for j in range(k):
            for (y,z) in product(Y[j],Z[j]):
                tail2(y,z)
    else:
        for j in range(k):
            for z in Z[j]:
                tail1(z)

    # Gamma
    if long_gamma:
        vsids.add_clause([(False,yname(j,i)) for i in range(m) for j in range(k)])

    if split_gamma:
        for i in range(0,m,split_gamma):
            vsids.add_clause([(False,yname(j,i+ii)) for j in range(k) for ii in range(split_gamma)])
            pass

    if completeTautology:
        kk=10
        A = [aname(i) for i in range(kk)]
        #kk=k
        #A=[Y[i][0] for i in range(k)]
        for polarity in product((True,False),repeat=kk):
            vsids.add_clause(list(zip(polarity,A)))

    return vsids

@cnfformula.cmdline.register_cnfgen_subcommand
class VsidsCmdHelper(object):
    name='vsidsts'
    description='hard VSIDS formula'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('n',type=int)
        parser.add_argument('d',type=int)
        parser.add_argument('m',type=int)
        parser.add_argument('l',type=int)
        parser.add_argument('k',type=int)
        parser.add_argument('--long-gamma',action="store_true")
        parser.add_argument('--split-gamma',type=int)

    @staticmethod
    def build_cnf(args):
        return VsidsFormulaTs(args.n, args.d, args.m, args.l, args.k, args.long_gamma, args.split_gamma)

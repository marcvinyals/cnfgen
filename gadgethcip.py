#!/usr/bin/env python
# -*- coding:utf-8 -*-

opb = False
write = True

from sys import argv

from itertools import permutations
if opb:
    from cnfformula.opb import OPB
else:
    from cnfformula.cnf import CNF, less_or_equal_constraint, equal_to_constraint, parity_constraint

def partitionvar(a,b,v):
    return "p_{}_{}_{}".format(a,b,v)

def edgevarA(a,v,w):
    return "ea_{}_{}_{}".format(a,v,w)

def edgevarB(b,v,w):
    return "eb_{}_{}_{}".format(b,v,w)

def edgevar(a,b,v,w):
    return "e_{}_{}_{}_{}".format(a,b,v,w)

def ordervar(a,b,v,i):
    return "o_{}_{}_{}_{}".format(a,b,v,i)

allvars = []

def GadgetHCIP(n):
    sources =  ["s0", "s1"]
    targets = ["t0", "t1"]
    extravertices = list(map(str,range(n)))
    nonsources = targets + extravertices
    nontargets = sources + extravertices
    vertices = sources + targets + extravertices

    if opb:
        F = OPB()
    else:
        F = CNF()
    for a in range(2):
        for b in range(2):
            for v in vertices:
                F.add_variable(partitionvar(a,b,v))
                allvars.append(partitionvar(a,b,v))
    for a in range(2):
        for v in vertices:
            for w in vertices:
                if v==w : continue
                F.add_variable(edgevarA(a,v,w))
                F.add_variable(edgevarB(a,v,w))
                allvars.append(edgevarA(a,v,w))
                allvars.append(edgevarB(a,v,w))

    for a in range(2):
        for b in range(2):
            for v in vertices:
                for w in vertices:
                    if v==w: continue
                    F.add_variable(edgevar(a,b,v,w))
                    allvars.append(edgevar(a,b,v,w))

    for a in range(2):
        for b in range(2):
            # s0 in partition 0
            F.add_clause([(False,partitionvar(a,b,"s0"))])
            # s1 in partition 1
            F.add_clause([(True,partitionvar(a,b,"s1"))])
            # t0 in partition a^b
            F.add_clause([(a and b,partitionvar(a,b,"t0"))])
            # t1 in partition ~(a^b)
            F.add_clause([(not (a and b),partitionvar(a,b,"t1"))])

    # Definition of edge variables
    for a in range(2):
        for b in range(2):
            for v in vertices:
                for w in vertices:
                    if v==w: continue
                    # edgevar == (edgevarA v edgevarB)
                    F.add_clause([
                        (False,edgevar(a,b,v,w)),
                        (True,edgevarA(a,v,w)),
                        (True,edgevarB(b,v,w)),
                    ])
                    F.add_clause([
                        (True,edgevar(a,b,v,w)),
                        (False,edgevarA(a,v,w)),
                    ])
                    F.add_clause([
                        (True,edgevar(a,b,v,w)),
                        (False,edgevarB(b,v,w)),
                    ])
            
    # Edges are held by one player only
    for v in vertices:
        for w in vertices:
            if v==w : continue
            variables = [
                edgevarA(0,v,w),
                edgevarA(1,v,w),
                edgevarB(0,v,w),
                edgevarB(1,v,w),
            ]
            if opb :
                F.add_leq_constraint(variables,1)
            else:
                for cls in less_or_equal_constraint(variables,1):
                    F.add_clause(cls,strict=True)

    # A node is in the same partition as its predecessor
    for a in range(2):
        for b in range(2):
            for v in nontargets:
                for w in nonsources:
                    if v==w : continue
                    # edgevar -> [partitionvar(v) == partitionvar(w)]
                    F.add_clause([
                        (False,edgevar(a,b,v,w)),
                        (False,partitionvar(a,b,v)),
                        (True,partitionvar(a,b,w))
                    ])
                    F.add_clause([
                        (False,edgevar(a,b,v,w)),
                        (True,partitionvar(a,b,v)),
                        (False,partitionvar(a,b,w)),
                    ])

    # Sources are not pointed at by anything
    for a in range(2):
        for b in range(2):
            for v in vertices:
                for w in sources:
                    if v==w : continue
                    F.add_clause([(False,edgevar(a,b,v,w))],strict=True)

    # Targets do not point to anything
    for a in range(2):
        for b in range(2):
            for v in targets:
                for w in vertices:
                    if v==w : continue
                    F.add_clause([(False,edgevar(a,b,v,w))],strict=True)

    # Non-targets point to exactly one non-source
    for a in range(2):
        for b in range(2):
            for v in nontargets:
                edges = [edgevar(a,b,v,w) for w in nonsources if v!=w]
                if opb:
                    F.add_eq_constraint(edges,1)
                else:
                    for cls in equal_to_constraint(edges,1):
                        F.add_clause(cls,strict=True)

    # Non-sources are pointed at by exactly one non-target
    for a in range(2):
        for b in range(2):
            for w in nonsources:
                edges = [edgevar(a,b,v,w) for v in nontargets if v!=w]
                if opb:
                    F.add_eq_constraint(edges,1)
                else:
                    for cls in equal_to_constraint(edges,1):
                        F.add_clause(cls,strict=True)

    # No loops
    #for a in range(2):
    #    for b in range(2):
    #        for l in range(2,n+1):
    #            for cycle in permutations(extravertices,l):
    #                edges = [edgevar(a,b,cycle[i],cycle[(i+1)%l]) for i in range(l)]
    #                if opb:
    #                    F.add_leq_constraint(edges,l-1)
    #                else:
    #                    for cls in less_or_equal_constraint(edges,l-1):
    #                        F.add_clause(cls,strict=True)

    maxlen = 6
    for a in range(2):
        for b in range(2):
            for v in vertices:
                for i in range(maxlen):
                    F.add_variable(ordervar(a,b,v,i))
                    allvars.append(ordervar(a,b,v,i))

    for a in range(2):
        for b in range(2):
            for v in vertices:
                for w in vertices:
                    if v==w : continue
                    for i in range(maxlen-1):
                        F.add_clause([
                            (False,edgevar(a,b,v,w)),
                            (False,ordervar(a,b,v,i)),
                            (True,ordervar(a,b,w,i+1))
                        ])
                        F.add_clause([
                            (False,edgevar(a,b,v,w)),
                            (True,ordervar(a,b,v,i)),
                            (False,ordervar(a,b,w,i+1))
                        ])

    for a in range(2):
        for b in range(2):
            for v in sources:
                F.add_clause([(True,ordervar(a,b,v,0))],strict=True)
            for v in nontargets:
                F.add_clause([(False,ordervar(a,b,v,maxlen-1))],strict=True)
                uniq = [ordervar(a,b,v,i) for i in range(maxlen-1)]
                for cls in equal_to_constraint(uniq,1):
                    F.add_clause(cls,strict=True)

    # Some symmetry-breaking (might be too strong)
    #F.add_clause([(True,edgevarA(0,"s0",0))])
    #F.add_clause([(True,edgevarA(1,"s0",1))])
    #F.add_clause([(True,edgevarB(0,"s1",2))])
    #F.add_clause([(True,edgevarB(1,"s1",3))])
                            
    return F

def Translate():
    from sys import stdin

    assignment = []

    import re
    litregex = re.compile("(-?)x(\d+)")
    def parselit(s):
        m = litregex.match(s)
        return int(m.group(1)+m.group(2))
    
    while(True):
        line = stdin.readline()
        if line=="" : break
        if line[0] != 'v' : continue
        assignment.extend(map(parselit if opb else int,line.split()[1:]))

        print(assignment)

    for lit in assignment[:-1]:
        polarity = (lit>0)
        variable = allvars[abs(lit)-1]
        if variable[0]=='o':
            print(polarity,variable)

if __name__ == "__main__":
    if write:
        F = GadgetHCIP(int(argv[1]))
        if opb:
            print(F.to_opb())
        else:
            print(F.dimacs())
    else:
        Translate()

from cnfgen.cnf import CNF

from itertools import combinations, product

import sys

def BipartiteOddCycle(n,have_edges):
    description = "Bipartite vs Odd Cycle formula"
    F = CNF(description=description)

    def var_colour(v):
        return 'c_{{{0}}}'.format(v)

    def var_edge(u,v):
        if u > v:
            (u,v)=(v,u)
        return 'e_{{{0},{1}}}'.format(u,v)

    def var_index(v,i):
        return 'p_{{{0},{1}}}'.format(v,i)

    m = ((n-1)//2)*2+1 # Largest odd number not greater than n

    V = range(n)
    E = list(combinations(V,2))
    I = range(m)

    for v in V:
        F.add_variable(var_colour(v))

    if have_edges:
        for u,v in E:
            F.add_variable(var_edge(u,v))

    for v,i in product(V,I):
        F.add_variable(var_index(v,i))

    if have_edges:
        for u,v in E:
            F.add_clause([(True, var_colour(u)), (True, var_colour(v)), (False, var_edge(u,v))])
            F.add_clause([(False, var_colour(u)), (False, var_colour(v)), (False, var_edge(u,v))])

        for u,v,i in product(V,V,I):
            if u==v:
                F.add_clause([(False, var_index(u,i)), (False, var_index(v,(i+1)%m))])
            else:
                F.add_clause([(False, var_index(u,i)), (False, var_index(v,(i+1)%m)), (True, var_edge(u,v))])
    else:
        for u,v,i in product(V,V,I):
            if u==v:
                F.add_clause([(False, var_index(u,i)), (False, var_index(v,(i+1)%m))])
            else:
                F.add_clause([(False, var_index(u,i)), (False, var_index(v,(i+1)%m)),
                              (True, var_colour(u)), (True, var_colour(v))])
                F.add_clause([(False, var_index(u,i)), (False, var_index(v,(i+1)%m)),
                              (False, var_colour(u)), (False, var_colour(v))])

    for i in I:
        F.add_clause([(True, var_index(v,i)) for v in V])

    return F

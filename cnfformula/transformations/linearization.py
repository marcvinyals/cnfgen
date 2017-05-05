#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

from ..cnf import CNF, weighted_eq, weighted_geq

from ..cmdline  import register_cnf_transformation_subcommand
from ..transformations import register_cnf_transformation

###
### Substitions
###

@register_cnf_transformation
class Linearization(CNF):
    """Apply a substitution to a formula
    """

    def __init__(self, cnf, arity, no_rat, equality):
        """Build a new CNF linearizing clauses

        Arguments:
        - `cnf`: the original cnf
        """
        self._orig_cnf = cnf
        super(Linearization,self).__init__([],header=cnf._header)

        self._header="Linearized formula with arity {}\n\n".format(arity) \
            +self._header
        
        varname = [None]+list(self._orig_cnf.variables())
        def newvarname(l,i):
            return "{{{}}}^{}".format(varname[l],i)
        def newvar(l,i):
            return (l-1)*arity+i+1

        for l in range(1,len(varname)):
            for j in range(arity):
                self.add_variable(newvarname(l,j))

        # build and add new clauses
        for orig_cnst in self._orig_cnf._constraints:
            for orig_cls in orig_cnst.clauses():
                positive_literals = [x for x in orig_cls if x>0]
                negative_literals = [-x for x in orig_cls if x<0]
                p=len(positive_literals)
                n=len(negative_literals)
                pweight=0
                nweight=0
                if (p==0):
                    if no_rat:
                        nweight = -1
                        threshold = (-n*arity//2)+1
                    else:
                        nweight = -2
                        threshold = -n*arity
                elif (n==0):
                    if no_rat:
                        pweight = 1
                        threshold = -(-p*arity//2)
                    else:
                        pweight = 2
                        threshold = p*arity
                else:
                    pweight = n
                    nweight = -p
                    threshold = 0
                q = []
                if pweight:
                    q.extend([(pweight,newvar(l,j)) for l in positive_literals for j in range(arity)])
                if nweight:
                    q.extend([(nweight,newvar(l,j)) for l in negative_literals for j in range(arity)])
                if equality:
                    self._constraints.append(weighted_eq(*q,value=threshold))
                else:
                    self._constraints.append(weighted_geq(*q,threshold=threshold))
                    
        self._length = None
#        assert self._check_coherence()

@register_cnf_transformation_subcommand
class LinearizationCmd:
    name='lin'
    description='linearize clauses with arity N'

    @staticmethod
    def setup_command_line(parser):
        parser.add_argument('N',type=int,nargs='?',default=3,action='store',help="arity (default: 3)")
        parser.add_argument('--no-rat',action='store_true')
        parser.add_argument('--equality',action='store_true')

    @staticmethod
    def transform_cnf(F,args):
        return Linearization(F,args.N,args.no_rat,args.equality)

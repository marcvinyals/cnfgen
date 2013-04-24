#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function

__docstring__ =\
"""Utilities to build CNF formulas interesting for proof complexity.

The module `dimacs` contains facilities to generate manipulates dimacs
CNFs, in particular from command line.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

import sys
import random
import subprocess
from cnfformula import CNF
from cnfformula.utils import dimacs2cnf


def reshuffle(cnf,
              variable_permutation=None,
              clause_permutation=None,
              polarity_flip=None
              ):

    # empty cnf
    out=CNF(header='')

    out.header="Reshuffling of:\n\n"+cnf.header


    vars=list(cnf.variables())
    N=len(vars)
    M=len(cnf)

    # variable permutation
    if variable_permutation==None:
        variable_permutation=vars
        random.shuffle(variable_permutation)
    else:
        assert len(variable_permutation)==N

    # polarity flip
    if polarity_flip==None:
        polarity_flip=[1-2*random.randint(0,1)
                              for i in xrange(N)]
    else:
        assert len(polarity_flip)==N

    #
    # substitution of variables
    #
    for v in variable_permutation:
        out.add_variable(v)

    substitution=[None]*(2*N+1)
    reverse_idx=dict([(v,i) for (i,v) in enumerate(out.variables(),1)])
    polarity_flip = [None]+polarity_flip

    for i,v in enumerate(cnf.variables(),1):
        substitution[i]=  polarity_flip[i]*reverse_idx[v]
        substitution[-i]= -substitution[i]

    #
    # permutation of clauses
    #
    if clause_permutation==None:
        clause_permutation=range(M)
        random.shuffle(clause_permutation)

    # load clauses
    out._clauses = [None]*M
    for (old,new) in enumerate(clause_permutation):
        out._clauses[new]=tuple( substitution[l] for l in cnf._clauses[old])

    # load comments
    assert len(out._comments)==0
    clause_permutation.append((M,M)) # comments after last clause do not move
    for (pos,text) in cnf._comments:
        out._comments.append((clause_permutation[pos],text))
    clause_permutation.pop()
    def key(t): return t[0]
    out._comments.sort(key=key)


    # return the formula
    assert out._check_coherence(force=True)
    return out

def dimacsshuffle(inputfile=sys.stdin,outputfile=sys.stdout):
    """ Reshuffle variables and polarity
    """
    n = -1  # negative signal that spec line has not been read
    subst= None

    line_counter = 0

    header_buffer=[]

    # Prepare to use command line shuffle
    proc = subprocess.Popen("shuf", stdin=subprocess.PIPE, stdout=outputfile)

    for l in inputfile.readlines():

        line_counter+=1

        # add the comment to the header (discard if it is in the middle)
        if l[0]=='c':
            if not subst: header_buffer.append(l)
            continue

        # parse spec line
        if l[0]=='p':
            if subst:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(line_counter))
            _,_,nstr,_ = l.split()
            n = int(nstr)
            subst = substitution(n)
            
            # Print header
            for h in header_buffer:
                print(h,end='',file=outputfile)
            
            print("c Permuted with mapping",file=outputfile)
            for i in xrange(1,n+1):
                print("c   {} --> {}".format(i,subst[i]),file=outputfile)
            print("c",file=outputfile)
                        
            print(l,end='',file=outputfile)
            
            continue

        # parse literals
        clause = [int(lit) for lit in l.split()]

        # Checks at the end of clause
        if clause[-1] != 0:
            raise ValueError("Syntax error: last clause was incomplete")

        print(" ".join([str(subst[i]) for i in clause]),file=proc.stdin)


def substitution(n):

    vars=range(1,n+1)
    random.shuffle(vars)
    vars=[0]+vars
    flip=[0]+[1-2*random.randint(0,1) for i in xrange(n)]

    subst=[None]*(2*n+1)
    subst[0]=0
    for i in xrange(1,n+1):
        subst[i] = vars[i]*flip[i]
        subst[-i]= -subst[i]

    return subst


def command_line_reshuffle(argv):

    # Python 2.6 does not have argparse library
    try:
        import argparse
    except ImportError:
        print("Sorry: %s requires `argparse` library, which is missing.\n"%argv[0],file=sys.stderr)
        print("Either use Python 2.7 or install it from one of the following URLs:",file=sys.stderr)
        print(" * http://pypi.python.org/pypi/argparse",file=sys.stderr)
        print(" * http://code.google.com/p/argparse",file=sys.stderr)
        print("",file=sys.stderr)
        exit(-1)

    # Parse the command line arguments
    parser=argparse.ArgumentParser(prog='shuffle',epilog="""
    For more information type 'shuffle <formula type> [--help | -h ]'
    """)

    parser.add_argument('--output','-o',
                        type=argparse.FileType('wb',0),
                        metavar="<output>",
                        default='-',
                        help="""Output file. The formula is saved
                        on file instead of being sent to standard
                        output. Setting '<output>' to '-' is another
                        way to send the formula to standard output.
                        (default: -)
                        """)
    parser.add_argument('--seed','-S',
                        metavar="<seed>",
                        default=None,
                        type=str,
                        action='store',
                        help="""Seed for any random process in the
                        program. Any python hashable object will
                        be fine.  (default: current time)
                        """)
    parser.add_argument('--input','-i',
                        type=argparse.FileType('r',0),
                        metavar="<input>",
                        default='-',
                        help="""Input file. A formula in dimacs format. Setting '<input>' to '-' is
                        another way to read from standard input.
                        (default: -)
                        """)

    g=parser.add_mutually_exclusive_group()
    g.add_argument('--verbose', '-v',action='count',default=1,
                   help="""Include comments inside the formula. It may
                   not be supported by very old sat solvers.
                   """)
    g.add_argument('--quiet', '-q',action='store_const',const=0,dest='verbose',
                   help="""Output just the formula with not header
                   or comment.""")


    # Process the options
    args=parser.parse_args(argv[1:])

    # If necessary, init the random generator
    if hasattr(args,'seed') and args.seed:
        random.seed(args.seed)

    dimacsshuffle(args.input,args.output)

    if args.output!=sys.stdout:
        args.output.close()


### Launcher
if __name__ == '__main__':
    command_line_reshuffle(sys.argv)

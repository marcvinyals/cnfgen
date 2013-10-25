#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import print_function
import re
from .cnf import CNF

__docstring__ =\
"""Various utilities for the manipulation of the CNFs.

Copyright (C) 2012, 2013  Massimo Lauria <lauria@kth.se>
https://github.com/MassimoLauria/cnfgen.git

"""

__all__ = ["dimacs2cnf","dimacs2compressed_clauses"]


def dimacs2compressed_clauses(file_handle):
    """
    Parse a dimacs cnf file into a list of
    compressed clauses.

    return: (h,n,c) where

    h is a string of text (the header)
    n is the number of variables
    c is the list of compressed clauses.
    
    """
    n = None  # negative signal that spec line has not been read
    m = None

    my_header=""
    my_clauses=[]

    for line_counter,l in enumerate(file_handle.readlines()):

        # Add all the comments to the header. If a comment is found
        # inside the formula, add it to the header as well. Comments
        # interleaving clauses are not allowed in dimacs format.
        match = re.match(r'^c ?(.*)$',l)
        if match:
            my_header += match.group(1)+'\n'
            continue
        
        # Spec line
        match = re.match(r'^p cnf (\d+) (\d+)$',l)
        if match:
            if not n is None:
                raise ValueError("Syntax error: "+
                                 "line {} contains a second spec line.".format(line_counter+1))
            n = int(match.group(1))
            m = int(match.group(2))
            continue
        
        # Literals
        if re.match(r'^(-?\d+ )*0$',l):
            my_clauses.append(tuple([int(lit) for lit in l.split()][:-1]))
            continue

        # Uh?
        if not re.match(r'^\s*$',l):
            raise ValueError("Could not parse line {}.\n{}".format(line_counter+1,l))

    my_header=my_header.rstrip()+'\n'

    # Checks at the end of parsing
    if m is None:
        raise ValueError("Warning: empty input formula ")

    if m!=len(my_clauses):
        raise ValueError("Warning: input formula "+
                         "contains {} instead of expected {}.".format(len(my_clauses),m))

    # return the formula
    return (my_header,n,my_clauses)




def dimacs2cnf(file_handle):
    """Load dimacs file into a CNF object
    """

    header,nvariables,clauses = dimacs2compressed_clauses(file_handle)

    cnf=CNF(header=header)

    for i in xrange(1,nvariables+1):
        cnf.add_variable(i)

    cnf._add_compressed_clauses(clauses)
    

    # return the formula
    cnf._check_coherence(force=True)
    return cnf


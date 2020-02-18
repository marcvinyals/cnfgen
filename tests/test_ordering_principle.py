from cnfformula import CNF
from cnfformula import OrderingPrinciple, GraphOrderingPrinciple

from . import TestCNFBase
from .test_commandline_helper import TestCommandline

import unittest
import networkx as nx
import sys

class TestOrderingPrinciple(TestCNFBase):
    def test_empty(self):
        dimacs = """\
        p cnf 0 0
        """
        F = OrderingPrinciple(0)
        self.assertCnfEqualsDimacs(F,dimacs)

    def test_one_element(self):
        dimacs = """\
        p cnf 0 1
        0
        """
        F = OrderingPrinciple(1)
        self.assertCnfEqualsDimacs(F,dimacs)

        
class TestGraphOrderingPrinciple(TestCNFBase):
    def test_empty(self):
        G = CNF()
        graph=nx.Graph()
        F = GraphOrderingPrinciple(graph)
        self.assertCnfEqual(F,G)

    def test_complete(self):
        for total in (True, False):
            for smart in (True, False):
                for plant in (True, False):
                    for knuth in (0, 2, 3):
                        graph = nx.complete_graph(4)
                        F = GraphOrderingPrinciple(graph, total, smart, plant, knuth)
                        G = OrderingPrinciple(4, total, smart, plant, knuth)
                        self.assertCnfEquivalentModuloVariables(F, G)

class TestOrderingPrincipleCommandline(TestCommandline):
    def test_parameters(self):
        for total in (True,False):
            for smart in (True,False):
                for plant in (True,False):
                    for knuth in (False,2,3):
                        parameters = ["cnfgen","-q","op", 5]
                        if total : parameters.append("--total")
                        if smart : parameters.append("--smart")
                        if plant : parameters.append("--plant")
                        if knuth : parameters.append("--knuth{}".format(knuth))
                        switches = len([_f for _f in (total,smart,knuth) if _f])
                        if (switches>1) :
                            self.checkCrash(sys.stdin,parameters)
                        else :
                            F = OrderingPrinciple(5,total,smart,plant,knuth)
                            self.checkFormula(sys.stdin,F, parameters)

class TestGraphOrderingPrincipleCommandline(TestCommandline):
    def test_complete(self):
        for total in (True,False):
            for smart in (True,False):
                for plant in (True,False):
                    for knuth in (False,2,3):
                        parameters = ["cnfgen","-q","gop", "--complete", 5]
                        if total : parameters.append("--total")
                        if smart : parameters.append("--smart")
                        if plant : parameters.append("--plant")
                        if knuth : parameters.append("--knuth{}".format(knuth))
                        switches = len([_f for _f in (total,smart,knuth) if _f])
                        if (switches>1) :
                            self.checkCrash(sys.stdin,parameters)
                        else :
                            graph = nx.complete_graph(5)
                            F = GraphOrderingPrinciple(graph,total,smart,plant,knuth)
                            self.checkFormula(sys.stdin,F, parameters)

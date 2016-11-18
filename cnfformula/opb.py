from __future__ import print_function

class OPB(object):
    def __init__(self):
        self._index2name = []
        self._name2index = {}
        self._constraints = []
        self.header = ""
        self.dimacs = self.to_opb

    def to_opb(self, export_header=False, extra_text=None):
        from cStringIO import StringIO
        output = StringIO()
        output.write("* #variable= {} #constraint= {}\n".format(
            len(self._index2name),len(self._constraints)))
        for c in self._constraints:
            freeterm = c[-1]
            for term in c[:-1]:
                coefficient = term[0]
                literal = "x" + str(self._name2index[term[2]]+1)
                if not term[1] :
                    coefficient *= -1
                    freeterm += coefficient
                    # literal = "~" + literal
                output.write("{} {} ".format(coefficient,literal))
            output.write(">= {} ;\n".format(freeterm))

        return output.getvalue()
        
    def add_variable(self, var):
        self._index2name.append(var)
        self._name2index[var] = len(self._index2name)-1

    def add_constraint(self, constraint):
        self._constraints.append(constraint)
        
    def add_clause(self, clause, strict=False):
        self.add_constraint([(1,)+lit for lit in clause] + [1])

    def add_geq_constraint(self, variables, lower_bound):
        self.add_constraint([(1,True,var) for var in variables] + [lower_bound])
        
    def add_leq_constraint(self, variables, upper_bound):
        self.add_constraint([(-1,True,var) for var in variables] + [-upper_bound])

    def add_eq_constraint(self, variables, value):
        self.add_geq_constraint(variables, value)
        self.add_leq_constraint(variables, value)

from __future__ import print_function

from opb import OPB

class GLPK(OPB):
    def dimacs(self, export_header=False, extra_text=None):
        from cStringIO import StringIO
        output = StringIO()
        # Change binary to real to allow rational solutions
        output.write("p = MixedIntegerLinearProgram()\nx = p.new_variable(binary=True)\n")
        for c in self._constraints:
            output.write("p.add_constraint(")
            freeterm = c[-1]
            for term in c[:-1]:
                coefficient = term[0]
                literal = "x[{}]".format(self._name2index[term[2]]+1)
                if not term[1] :
                    coefficient *= -1
                    freeterm += coefficient
                output.write("+{}*{} ".format(coefficient,literal))
            output.write(">={})\n".format(freeterm))
        output.write("p.solve()\np.get_values(x)\n")

        return output.getvalue()

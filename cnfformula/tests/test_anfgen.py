#!/usr/bin/env python

import unittest

class TestCnfgen(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(SystemExit) as cm:
            import cnfformula.cnfgen as cnfgen
            cnfgen.command_line_utility(["cnfgen"])
        self.assertNotEqual(cm.exception.code, 0)

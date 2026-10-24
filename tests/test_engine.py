# -*- coding: utf-8 -*-
"""phyxexp 核心引擎单测（unittest，无需 pytest）。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from phyxexp.engine.uncertainty import type_a, type_b, combine
from phyxexp.engine.fit import linear_fit
from phyxexp.engine.models import youngs_modulus, spring_constant, diameter_uncertainty


class TestUncertainty(unittest.TestCase):
    def test_type_a(self):
        mean, s, u = type_a([1, 2, 3, 4, 5])
        self.assertAlmostEqual(mean, 3.0)
        self.assertAlmostEqual(s, 1.5811, places=3)
        self.assertAlmostEqual(u, 0.7071, places=3)

    def test_type_b(self):
        self.assertAlmostEqual(type_b(0.3), 0.3 / 3 ** 0.5, places=12)

    def test_combine(self):
        self.assertAlmostEqual(combine(3.0, 4.0), 5.0)


class TestFit(unittest.TestCase):
    def test_perfect_line(self):
        f = linear_fit([1, 2, 3, 4], [2, 4, 6, 8])
        self.assertAlmostEqual(f["k"], 2.0, places=9)
        self.assertAlmostEqual(f["b"], 0.0, places=9)
        self.assertAlmostEqual(f["r2"], 1.0, places=9)

    def test_insufficient(self):
        with self.assertRaises(ValueError):
            linear_fit([1, 2], [1, 2])


class TestModels(unittest.TestCase):
    def test_youngs_modulus_steel(self):
        r = youngs_modulus(0.5, 9.794, 0.95, 1.5, 0.075, 0.5015e-3, 4.705e-3,
                           0, 0, 0, 0, 0, 0, 0)
        self.assertGreater(r["E"], 1e11)
        self.assertLess(r["E"], 3e11)

    def test_spring_constant(self):
        # T^2 = 4*m  =>  slope=4  =>  k=4*pi^2/4=pi^2
        m = [0.1, 0.2, 0.3, 0.4]
        T = [2.0 * x ** 0.5 for x in m]
        r = spring_constant(m, T)
        self.assertAlmostEqual(r["k"], 3.1415926535 ** 2, places=6)

    def test_diameter_uncertainty(self):
        r = diameter_uncertainty([0.501, 0.502, 0.500, 0.502], 0.004)
        self.assertAlmostEqual(r["d_mean"], 0.50125e-3, places=12)
        self.assertGreater(r["u_d"], 0)


if __name__ == "__main__":
    unittest.main()

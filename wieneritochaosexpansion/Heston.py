# -*- coding,  utf-8 -*-
from BaseWienerItoChaosExpansion import USE_SYMENGINE
from BaseWienerItoChaosExpansion import BaseWienerItoChaosExpansion
from StopWatch import StopWatch

if USE_SYMENGINE:
    from symengine import Symbol
    from symengine import sqrt
else:
    from sympy import Symbol
    from sympy import sqrt

class Heston(BaseWienerItoChaosExpansion):
    def __init__(self):
        super().__init__()
        self.model_name = 'Heston'
        self.r0 = Symbol('r0', positive=True)
        self.ka = Symbol('kappa', positive=True)
        self.th = Symbol('theta', positive=True)
        self.nu = Symbol('nu', positive=True)
        self.v0 = Symbol('v0', positive=True)

    def r(self, t=Symbol('t', positive=True)):
        # return self.r0
        return 0

    def sigma(self, s=Symbol('s', positive=True),
              v=Symbol('v', positive=True)):
        return sqrt(v)

    def theta(self, t=Symbol('t', positive=True)):
        return self.th * self.ka

    def kappa(self, t=Symbol('t', positive=True)):
        return self.ka

    def gamma(self, v=Symbol('v', positive=True)):
        return self.nu * sqrt(v)

if __name__  ==  '__main__':
    sw = StopWatch()
    proc = Heston()
    proc.show_model_spec()
    # print(proc.print_in_r(proc.f_Xt(simplify=False)))
    sw.show_elapsed_time()
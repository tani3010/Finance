# -*- coding,  utf-8 -*-
from BaseWienerItoChaosExpansion import USE_SYMENGINE
from BaseWienerItoChaosExpansion import BaseWienerItoChaosExpansion
from StopWatch import StopWatch

if USE_SYMENGINE:
    from symengine import Symbol
else:
    from sympy import Symbol

class CEV(BaseWienerItoChaosExpansion):
    def __init__(self):
        super().__init__()
        self.model_name = 'CEV'
        self.r0 = Symbol('r0', positive=True)
        self.gam = Symbol('gamma', positive=True)

    def r(self, t=Symbol('t', positive=True)):
        # return self.r0
        return 0

    def sigma(self, s=Symbol('s', positive=True),
              v=Symbol('v', positive=True)):
        return v * s ** (self.gam - 1)

    def theta(self, t=Symbol('t', positive=True)):
        return 0

    def kappa(self, t=Symbol('t', positive=True)):
        return 0

    def gamma(self, v=Symbol('v', positive=True)):
        return 0

if __name__  ==  '__main__':
    sw = StopWatch()
    proc = CEV()
    proc.show_model_spec()
    print(proc.print_in_r(proc.f_St(simplify=False)))
    sw.show_elapsed_time()
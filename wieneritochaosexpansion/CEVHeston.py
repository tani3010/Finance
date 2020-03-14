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

'''
CEV-Heston
dS_t = mu * v_t * (S_t + c) ** gamma dW^1_t
dv_t = alpha * (1 - v_t) * dt + delta * \sqrt{v_t} dW^2_t
'''

class CEVHeston(BaseWienerItoChaosExpansion):
    def __init__(self):
        super().__init__()
        self.model_name = 'CEVHeston'
        self.mu = Symbol('mu', positive=True)
        self.c = Symbol('c', positive=True)
        # self.gam = Symbol('gam', positive=True)
        self.alpha = Symbol('alpha', positive=True)
        self.delta = Symbol('delta', positive=True)
        self.v0 = Symbol('v0', positive=True)

    def r(self, t=Symbol('t', positive=True)):
        return 0

    def sigma(self, s=Symbol('s', positive=True),
              v=Symbol('v', positive=True)):
        return self.mu * v * (1 + self.c/s) # ** self.gam

    def theta(self, t=Symbol('t', positive=True)):
        return self.alpha

    def kappa(self, t=Symbol('t', positive=True)):
        return self.alpha

    def gamma(self, v=Symbol('v', positive=True)):
        return self.delta * sqrt(v)

if __name__  ==  '__main__':
    sw = StopWatch()
    proc = CEVHeston()
    proc.show_model_spec()
    print(proc.print_in_r(proc.f_Xt(simplify=False)))
    sw.show_elapsed_time()
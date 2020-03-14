# -*- coding,  utf-8 -*-
from BaseWienerItoChaosExpansion import USE_SYMENGINE
from BaseWienerItoChaosExpansion import BaseWienerItoChaosExpansion
from StopWatch import StopWatch

if USE_SYMENGINE:
    from symengine import Symbol
else:
    from sympy import Symbol

# original process of the CKLS
# dX_t = (\alpha + \beta * X_t) * dt + \sigma * X_t^\gamma * dW_t
# transformed process of the CKLS
# dX_t = \beta * X_t * dt + \sigma / X_t * (X_l - \alpha / \beta)^\gamma

class CKLS(BaseWienerItoChaosExpansion):
    def __init__(self):
        super().__init__()
        self.model_name = 'CKLS'
        self.alpha = Symbol('alpha')
        self.beta = Symbol('beta', positive=True)
        self.gam = Symbol('gamma', positive=True)

    def r(self, t=Symbol('t', positive=True)):
        # return self.beta
        return 0

    def sigma(self, s=Symbol('s', positive=True),
              v=Symbol('v', positive=True)):
        return v / s * (s - self.alpha / self.beta) ** self.gam

    def theta(self, t=Symbol('t', positive=True)):
        return 0

    def kappa(self, t=Symbol('t', positive=True)):
        return 0

    def gamma(self, v=Symbol('v', positive=True)):
        return 0

if __name__  ==  '__main__':
    sw = StopWatch()
    proc = CKLS()
    proc.show_model_spec()
    print(proc.print_in_r(proc.f_St(simplify=False)))
    sw.show_elapsed_time()
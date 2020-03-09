# -*- coding: utf-8 -*-
from BasePricer import BasePricer
import QuantLib as ql

class BlackScholesPricer(BasePricer):
    def __init__(self):
        super().__init__()

    def set_process(self):
        self.process = ql.BlackScholesMertonProcess(
            self.handles['initS'], self.dividend_ts, self.risk_free_ts,
            self.volatility_ts)
    
if __name__  ==  '__main__':    
    pricer = BlackScholesPricer()
    pricer.set_params(
        initS = 100, volatility = 0.05,
        risk_free_rate = 0.05, dividend_rate = 0)
    strike = 100
    maturity_period = ql.Period("1Y")
    print('NPV(analytic)    = ',
          pricer.get_vanilla_option_price_analytic(strike, maturity_period))
    print('NPV(binomialtre) = ',
          pricer.get_vanilla_option_price_binomialtree(strike, maturity_period, 1000))
    print('NPV(FD)          = ',
          pricer.get_vanilla_option_price_fd(strike, maturity_period, 100, 100))
    print('NPV(pseudo-MC)   = ',
          pricer.get_vanilla_option_price_mc_pseudo(strike, maturity_period, 250, 50000))
    print('NPV(quasi-MC)    = ',
          pricer.get_vanilla_option_price_mc_quasi(strike, maturity_period, 250, 50000))




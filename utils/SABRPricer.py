# -*- coding: utf-8 -*-
from BasePricer import BasePricer
from math import exp, sqrt
import QuantLib as ql

class SABRPricer(BasePricer):
    def __init__(self):
        super().__init__()

    def get_vanilla_option_price_sabr(self, strike, maturity_period,
                                      use_noarbsabr=False,
                                      option_type=ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        maturity = ql.Actual365Fixed().yearFraction(
            self.base_date,
            self.calendar.advance(self.base_date, maturity_period)
        )

        if use_noarbsabr:
            sabr_vol = ql.sabrFlochKennedyVolatility(
                strike, self.handles['initS'].value(), maturity,
                self.handles['alpha'].value(), self.handles['beta'].value(),
                self.handles['nu'].value(), self.handles['rho'].value()
            )
        else:
            sabr_vol = ql.sabrVolatility(
                strike, self.handles['initS'].value(), maturity,
                self.handles['alpha'].value(), self.handles['beta'].value(),
                self.handles['nu'].value(), self.handles['rho'].value()
            )

        npv = ql.blackFormula(
            option_type, strike, self.handles['initS'].value(),
            sabr_vol * sqrt(maturity),
            exp(-self.handles['risk_free_rate'].value()*maturity)
        )
        return npv

    def get_vanilla_option_price_noarbSabr(
        self, strike, maturity_period, option_type=ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.engine = ql.FdSabrVanillaEngine(
            self.handles['initS'].value(), self.handles['alpha'].value(),
            self.handles['beta'].value(), self.handles['nu'].value(),
            self.handles['rho'].value(), self.risk_free_ts
        )
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()


if __name__  ==  '__main__':
    pricer = SABRPricer()
    pricer.set_params(
        initS=0.0488, alpha=0.026, beta=0.5, nu=0.4, rho=-0.1,
        risk_free_rate=0.05, dividend_rate=0)
    strike = 0.0488
    maturity_period = ql.Period("1Y")
    print('NPV(SABR)           = ',
          pricer.get_vanilla_option_price_sabr(strike, maturity_period, False))
    print('NPV(No-Arb SABR)    = ',
          pricer.get_vanilla_option_price_sabr(strike, maturity_period, True))
    print('NPV(FD)             = ',
          pricer.get_vanilla_option_price_noarbSabr(strike, maturity_period))


    pricer.get_implied_density(
        pricer.get_vanilla_option_price_sabr, strike=strike,
        maturity_period=maturity_period, use_noarbsabr=True)

    pricer.get_implied_density(
        pricer.get_vanilla_option_price_noarbSabr, strike=strike,
        maturity_period=maturity_period)

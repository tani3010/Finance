# -*- coding: utf-8 -*-
import QuantLib as ql

class BasePricer:
    def __init__(self):
        self.calendar = ql.JointCalendar(ql.Japan(), ql.UnitedKingdom())
        self.today = ql.Date.todaysDate()
        self.base_date = self.calendar.adjust(self.today)
        ql.Settings.instance().evaluationDate = self.base_date
        self.day_counter = ql.Actual365Fixed()
        self.process = None
        self.model = None
        self.engine = None
        self.pricer= None
        self.option = None

    def set_params(self, **params):
        self.params = params
        self.handles = {
            key: ql.QuoteHandle(ql.SimpleQuote(item))
                for (key, item) in zip(params.keys(), params.values())
        }
        self.set_termstructure()

    def set_termstructure(self):
        if self.params.get('risk_free_rate') is not None:
            self.risk_free_ts = ql.YieldTermStructureHandle(
                ql.FlatForward(self.base_date, self.handles['risk_free_rate'],
                               self.day_counter))

        if self.params.get('dividend_rate') is not None:
            self.dividend_ts = ql.YieldTermStructureHandle(
                ql.FlatForward(self.base_date, self.handles['dividend_rate'],
                               self.day_counter))

        if self.params.get('volatility') is not None:
            self.volatility_ts = ql.BlackVolTermStructureHandle(
                ql.BlackConstantVol(self.base_date, self.calendar,
                                    self.handles['volatility'], self.day_counter))

    def set_process(self):
        pass

    def vanilla_option_helper(self, strike, maturity_period, option_type):
        self.set_process()
        payoff = ql.PlainVanillaPayoff(option_type, strike)
        self.exercise_date = ql.EuropeanExercise(self.calendar.advance(
            self.base_date, maturity_period, ql.ModifiedFollowing, False))
        option = ql.VanillaOption(payoff, self.exercise_date)
        return option

    def get_vanilla_option_price_analytic(self, strike, maturity_period,
                                          option_type=ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.engine = ql.AnalyticEuropeanEngine(self.process)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()

    def get_vanilla_option_price_binomialtree(
        self, strike, maturity_period, steps, option_type=ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.engine = ql.BinomialVanillaEngine(self.process, 'crr', steps)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()

    def get_vanilla_option_price_fd(
        self, strike, maturity_period, timeSteps,
        gridPoints, option_type = ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.engine = ql.FDEuropeanEngine(
            self.process, timeSteps=timeSteps, gridPoints=gridPoints)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()

    def get_vanilla_option_price_mc_pseudo(
        self, strike, maturity_period, timeSteps, requiredSamples,
        option_type = ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.engine = ql.MCEuropeanEngine(
            self.process, 'PseudoRandom',
            timeSteps=timeSteps, requiredSamples=requiredSamples)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()

    def get_vanilla_option_price_mc_quasi(
        self, strike, maturity_period, timeSteps, requiredSamples,
        option_type = ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.engine = ql.MCEuropeanEngine(
            self.process, 'LowDiscrepancy',
            timeSteps=timeSteps, requiredSamples=requiredSamples)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()

    def get_digital_option_price(
        self, npv_function, strike, option_type=ql.Option.Call,
        discount=1.0, gap=1.0e-05, **params):
        kl = strike - 0.5*gap
        kr = kl + gap
        return (
            npv_function(strike=kl, option_type=option_type, **params) /
                - npv_function(strike=kr, option_type=option_type, **params)
            ) * discount / gap

    def get_implied_density(
        self, npv_function, strike, discount=1.0, gap=1.0e-05, **params):
        kl = strike - 0.5*gap
        kr = kl + gap
        npv_left = self.get_digital_option_price(
            npv_function=npv_function, strike=kl,
            option_type=ql.Option.Call, **params)
        npv_right = self.get_digital_option_price(
            npv_function=npv_function, strike=kr,
            option_type=ql.Option.Call, **params)
        return (npv_left - npv_right) * discount / gap

    def get_implied_volatility(
        self, npv, strike, maturity_period, discount=1.0):
        exercise = ql.EuropeanExercise(
            self.calendar.advance(self.base_date, maturity_period))
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, strike)
        option = ql.EuropeanOption(payoff, exercise)
        return option.impliedVolatility(npv)


# -*- coding, utf-8 -*-

from math import exp, log, sqrt
import QuantLib as ql

class QuantLibSettings():
    def __init__(self):
        self.calendar = ql.JointCalendar(ql.Japan(), ql.UnitedKingdom())
        self.date_today = ql.Date.todaysDate()
        self.date_base = self.calendar.adjust(self.date_today)
        self.dc_master = ql.Actual365Fixed()
        ql.Settings.instance().setEvaluationDate(self.date_base)

    def __del__(self):
        pass

def func_payoffVanillaCall(strike):
    return ql.PlainVanillaPayoff(ql.Option.Call, strike)

def func_payoffVanillaPut(strike):
    return ql.PlainVanillaPayoff(ql.Option.Put, strike)

def func_getCallPriceByBlackFormula(
    K, forward, risk_free_rate, volatility, maturity, shift=0):
    stddev = volatility * sqrt(maturity)
    payoff = func_payoffVanillaCall(K)
    discount = exp(-risk_free_rate * maturity)
    calculator = ql.BlackCalculator(payoff, forward, stddev, discount)
    return calculator.value()

def func_getPutPriceByBlackFormula(
    K, forward, risk_free_rate, volatility, maturity, shift=0):
    stddev = volatility * sqrt(maturity)
    payoff = func_payoffVanillaPut(K)
    discount = exp(-risk_free_rate * maturity)
    calculator = ql.BlackCalculator(payoff, forward, stddev, discount)
    return calculator.value()


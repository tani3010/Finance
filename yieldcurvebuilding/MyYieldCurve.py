# -*- coding: utf-8 -*-
import QuantLib as ql
import pandas as pd

class MyYieldCurve:
    def __init__(self, ibor=ql.JPYLibor(ql.Period(6, ql.Months)), settlementDays=2,
                 fixedLegConv=ql.ModifiedFollowing, fixedLegFreq=ql.Semiannual,
                 fixedLegDc=ql.Actual365Fixed()):
        self.ibor = ibor
        self.cal = self.ibor.fixingCalendar()
        self.settlementDays = settlementDays
        self.fixedLegConv = fixedLegConv
        self.fixedLegFreq = fixedLegFreq
        self.fixedLegDc = fixedLegDc
        self.initializeDateSettings()
        self.ratesDepo = None
        self.ratesFra = None
        self.ratesFuture = None
        self.ratesSwap = None

    @staticmethod
    def qldate2serial(dates):
        return [i.serialNumber() for i in dates]

    def initialize_interpolated_discountcurve(self):
        tmp_date = self.dates[0]
        self.dates_dense = []
        while tmp_date <= self.dates[-1]:
            self.dates_dense.append(tmp_date)
            tmp_date += 1
        self.times_dense = self.qldate2serial(self.dates_dense)
        self.interpolator = self.subinterpolator(self.qldate2serial(self.dates), self.DFs)
        self.DFs_dense = [self.interpolator(i) for i in self.times_dense]
        self.forecastTermStructure = ql.DiscountCurve(self.dates_dense, self.DFs_dense, ql.Actual365Fixed())
        self.forecastTermStructure.enableExtrapolation()

    def load_interpolated_discountcurve(self, dates, DFs, subinterpolator):
        self.base_date = dates[0]
        self.dates = dates
        self.DFs = DFs
        self.subinterpolator = subinterpolator
        self.initialize_interpolated_discountcurve()

    def initializeDateSettings(self, baseDate=ql.Date.todaysDate()):
        self.baseDate = self.cal.adjust(baseDate)
        ql.Settings.instance().evaluationDate = self.baseDate

    def importRatesDepo(self, rates, periodStrs):
        if len(rates) != len(periodStrs):
            return
        self.ratesDepo = [
                ql.DepositRateHelper(
                    ql.QuoteHandle(rate), ql.PeriodParser().parse(periodStr), self.settlementDays, self.cal,
                    self.ibor.businessDayConvention(), False, self.ibor.dayCounter()
                ) for rate, periodStr in zip(rates, periodStrs)
        ]

    def importRatesFra(self, rates, monthsToStarts):
        if len(rates) != len(monthsToStarts):
            return
        self.ratesFra = [
            ql.FraRateHelper(
                ql.QuoteHandle(rate), int(monthsToStart[:len(monthsToStart)-1]), self.ibor
                ) for rate, monthsToStart in zip(rates, monthsToStarts)
        ]

    def importRatesFuture(self, prices, iborStartDates):
        if len(prices) != len(iborStartDates):
            return
        self.ratesFuture = [
            ql.FuturesRateHelper(
                ql.QuoteHandle(price), iborStartDate,
                self.ibor, ql.QuoteHandle(ql.SimpleQuote(0)), ql.Futures.IMM
                ) for price, iborStartDate in zip(prices, iborStartDates)
        ]

    def importRatesSwap(self, rates, periodStrs, spreadDict=None, discountTermStructureHandle=ql.YieldTermStructureHandle()):
        if len(rates) != len(periodStrs):
            return
        self.ratesSwap = [
            ql.SwapRateHelper(
                ql.QuoteHandle(rate), ql.PeriodParser().parse(periodStr), self.cal,
                self.fixedLegFreq, self.fixedLegConv, self.fixedLegDc, self.ibor,
                ql.QuoteHandle(
                    spreadDict[periodStr] if spreadDict is not None and spreadDict.get(periodStr, None) is not None else ql.SimpleQuote(0)
                ), ql.Period(0, ql.Days), discountTermStructureHandle
            ) for rate, periodStr in zip(rates, periodStrs)
        ]

    def rateHelperUtil(self, ratesSome):
        if ratesSome is not None:
            for rate in ratesSome:
                self.rateHelpers.append(rate)

    def build(self):
        self.rateHelpers = ql.RateHelperVector()
        self.rateHelperUtil(self.ratesFuture)
        self.rateHelperUtil(self.ratesDepo)
        self.rateHelperUtil(self.ratesFra)
        self.rateHelperUtil(self.ratesSwap)
        self.forecastTermStructure = ql.PiecewiseLogCubicDiscount(
            self.settlementDays, self.cal, self.rateHelpers, self.fixedLegDc)

    def getForecastTermStructureHandle(self):
        return ql.YieldTermStructureHandle(self.forecastTermStructure)

    def discount(self, t, enableExtrapolation=True):
        return self.forecastTermStructure.discount(t, enableExtrapolation)

    def getNodes(self):
        nodes = self.forecastTermStructure.nodes()
        dates = []
        df = []
        for iter in nodes:
            dates.append(pd.to_datetime(iter[0].ISO()))
            df.append(iter[1])
        return pd.Series(df, index=dates)

    def getZeroRate(self):
        nodes = self.forecastTermStructure.nodes()
        dates = []
        zeroRate = []
        for iter in nodes:
            dates.append(pd.to_datetime(iter[0].ISO()))
            zeroRate.append(self.forecastTermStructure.zeroRate(iter[0], ql.Actual365Fixed(), ql.Continuous).rate())
        return pd.Series(zeroRate, index=dates)
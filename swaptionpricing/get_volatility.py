# -*- coding: utf-8 -*-
import QuantLib as ql
import util_qldf

class MySwaption:
    def __init__(self, baseDate=ql.Date.todaysDate()):
        self.cal = ql.JointCalendar(ql.UnitedKingdom(), ql.UnitedStates())
        self.baseDate = self.cal.adjust(baseDate)
        self.settlementDays = ql.Period(2, ql.Days)
        ql.Settings.instance().evaluationDate = self.baseDate

    def setForecastCurve(self, forecastTermStructureHnadle):
        self.forecastTermStructure = forecastTermStructureHnadle
        self.iborIndex = ql.USDLibor(ql.Period('3M'), self.forecastTermStructure)

    def setDiscountCurve(self, discountTermStructureHandle):
        self.discountTermStructure = discountTermStructureHandle

    def makeSwap(self, optionTenor, swapTenor, swapRate=None, spread=0.0, notional=1.0,
                 fixedLegTenor=ql.Period('6M'), fixedLegDayCounter=ql.Actual360(), endOfMonth=False):
        self.optionTenor = optionTenor
        self.swapTenor = swapTenor
        self.notional = notional
        self.strike = swapRate
        self.fixedLegTenor
        self.fixedLegDayCounter
        self.endOfMonth = endOfMonth
        self.exerciseDate = self.cal.advance(self.baseDate, optionTenor)
        self.effectiveDate = self.cal.advance(self.exerciseDate, self.settlementDays)
        self.maturity = self.cal.advance(self.effectiveDate, swapTenor)

        # schedule generation
        self.fixedSchedule = ql.Schedule(self.effectiveDate, self.maturity, self.fixedLegTenor, self.cal,
                                      ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, endOfMonth)
        self.floatSchedule = ql.Schedule(self.effectiveDate, self.maturity, self.iborIndex.tenor(), self.cal,
                                      ql.ModifiedFollowing, ql.ModifiedFollowing, ql.DateGeneration.Forward, endOfMonth)

        # make vanilla swap
        self.payerSwap = ql.VanillaSwap(ql.VanillaSwap.Payer, notional, self.fixedSchedule, swapRate, self.fixedLegDayCounter,
                                        self.floatSchedule, self.iborIndex, spread, self.iborIndex.dayCounter())
        self.receiverSwap = ql.VanillaSwap(ql.VanillaSwap.Receiver, notional, self.fixedSchedule, swapRate, self.fixedLegDayCounter,
                                           self.floatSchedule, self.iborIndex, spread, self.iborIndex.dayCounter())
        swapEngine = ql.DiscountingSwapEngine(self.discountTermStructure)
        self.payerSwap.setPricingEngine(swapEngine)
        self.receiverSwap.setPricingEngine(swapEngine)
        self.fairRate = self.payerSwap.fairRate()

    def makeSwaption(self, vol, settlementType=ql.Settlement.Physical,
                     volType=ql.ShiftedLognormal, shift=0.02, swapRebuild=True):
        if swapRebuild:
            self.makeSwap(self.optionTenor, self.swapTenor, self.fairRate)
        self.settlementType = 'Cash-Settle' if settlementType == ql.Settlement.Cash else 'Physical-Settle'
        self.volHandle = ql.QuoteHandle(ql.SimpleQuote(vol))
        self.payerSwaption = ql.Swaption(self.payerSwap, ql.EuropeanExercise(self.exerciseDate), settlementType)
        self.receiverSwaption = ql.Swaption(self.receiverSwap, ql.EuropeanExercise(self.exerciseDate), settlementType)
        if volType == ql.ShiftedLognormal:
            swaptionEngine = ql.BlackSwaptionEngine(
                self.discountTermStructure, ql.QuoteHandle(ql.SimpleQuote(vol)), ql.Actual365Fixed(), shift)
        elif volType == ql.Normal:
            swaptionEngine = ql.BachelierSwaptionEngine(
                self.discountTermStructure, ql.QuoteHandle(ql.SimpleQuote(vol)), ql.Actual365Fixed())
        self.payerSwaption.setPricingEngine(swaptionEngine)
        self.receiverSwaption.setPricingEngine(swaptionEngine)

    def createSwaptionHelper(self, volType=ql.ShiftedLognormal, shift=0.02):
        self.swaptionHelper = ql.SwaptionHelper(
            self.optionTenor,
            self.swapTenor,
            self.volHandle,
            self.iborIndex,
            self.fixedLegTenor,
            self.fixedLegDayCounter,
            self.iborIndex.dayCounter(),
            self.discountTermStructure,
            ql.BlackCalibrationHelper.RelativePriceError,
            self.fairRate,
            self.notional,
            volType,
            shift
        )

    def getVolatility(self, volType=ql.ShiftedLognormal, shift=0.02):
        self.createSwaptionHelper(volType, shift)
        tolerance = 1e-08
        iterNum = 1000
        lower = 1e-08
        upper = 5.0
        return self.swaptionHelper.impliedVolatility(
                    self.payerSwaption.NPV(),
                    tolerance, iterNum, lower, upper)

if __name__ == '__main__':
    inst_df = util_qldf.util_qldf()
    inst_df.set_path('./', 'test_df.csv')
    inst_df.load_df('DATE')
    rateFair = 0.05063076037741058
    # rateFair = 0.1
    rate = 0.04020076107910886
    vol = 0.05
    parity = MySwaption(ql.Date(17, 9, 2018))
    parity.setForecastCurve(inst_df.get_yieldtermstructure_handle())
    parity.setDiscountCurve(inst_df.get_yieldtermstructure_handle())
    parity.makeSwap(ql.Period('1M'), ql.Period('10Y'), rateFair, 0, 1e10)
    parity.makeSwaption(vol, ql.Settlement.Physical)
    print(parity.getVolatility(ql.ShiftedLognormal, 0.02))
    print(parity.getVolatility(ql.ShiftedLognormal, 0.01))
    print(parity.getVolatility(ql.Normal))
    parity.makeSwaption(0.003010051593568979, ql.Settlement.Physical, ql.Normal)
    print(parity.getVolatility(ql.ShiftedLognormal, 0.02))

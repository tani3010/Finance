# -*- coding: utf-8 -*-
import QuantLib as ql
import util_qldf
import pandas as pd

class SwaptionBase:
    def __init__(self, baseDate=ql.Date.todaysDate(), cal=ql.JointCalendar(ql.UnitedKingdom(), ql.UnitedStates()),
                 settlementDays=ql.Period(2, ql.Days), iborIndex=ql.USDLibor(ql.Period('3M'))):
        self.cal = cal
        self.baseDate = self.cal.adjust(baseDate)
        self.settlementDays = settlementDays
        self.iborIndex = iborIndex
        ql.Settings.instance().evaluationDate = self.baseDate

    def setForecastCurve(self, forecastTermStructureHnadle):
        self.forecastTermStructure = forecastTermStructureHnadle
        self.iborIndex = self.iborIndex.__class__(self.iborIndex.tenor(), forecastTermStructureHnadle)

    def setDiscountCurve(self, discountTermStructureHandle):
        self.discountTermStructure = discountTermStructureHandle

    def makeSwap(self, optionTenor, swapTenor, swapRate=None, spread=0.0, notional=1.0,
                 fixedLegTenor=ql.Period('6M'), fixedLegDayCounter=ql.Actual360(), endOfMonth=False):
        self.optionTenor = optionTenor
        self.swapTenor = swapTenor
        self.notional = notional
        self.strike = swapRate
        self.fixedLegTenor = fixedLegTenor
        self.fixedLegDayCounter = fixedLegDayCounter
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

    def makeSwaption(self, vol, volType=ql.ShiftedLognormal,
                     delivery=ql.Settlement.Physical, settlementMethod=ql.Settlement.PhysicalOTC,
                     shift=0.02, swapRebuild=True):
        if swapRebuild:
            self.makeSwap(self.optionTenor, self.swapTenor, self.fairRate)
        self.volHandle = ql.QuoteHandle(ql.SimpleQuote(vol))
        self.payerSwaption = ql.Swaption(self.payerSwap, ql.EuropeanExercise(self.exerciseDate), delivery, settlementMethod)
        self.receiverSwaption = ql.Swaption(self.receiverSwap, ql.EuropeanExercise(self.exerciseDate), delivery, settlementMethod)
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

class USDLiborSwaption(SwaptionBase):
    def __init__(self, baseDate=ql.Date.todaysDate()):
        super().__init__(baseDate, ql.JointCalendar(ql.UnitedKingdom(), ql.UnitedStates()),
                         ql.Period(2, ql.Days), ql.USDLibor(ql.Period('3M')))

class USDSOFRswaption(SwaptionBase):
    def __init__(self, baseDate=ql.Date.todaysDate()):
        super().__init__(baseDate, ql.JointCalendar(ql.UnitedKingdom(), ql.UnitedStates()),
                         ql.Period(2, ql.Days), ql.OvernightIndex('SOFR', 0, ql.USDCurrency(), ql.UnitedStates(), ql.Actual360()))

    def setForecastCurve(self, forecastTermStructureHnadle):
        self.forecastTermStructure = forecastTermStructureHnadle
        self.iborIndex = self.iborIndex.__class__(
                'SOFR', 0, ql.USDCurrency(), ql.UnitedStates(), ql.Actual360(), forecastTermStructureHnadle)

def getVolTypeName(volType):
    if volType == ql.ShiftedLognormal:
        return 'ShiftedLogNormal'
    elif volType == ql.Normal:
        return 'Normal'
    else:
        return 'Undefined Vol Name'

def getDeliveryName(delivery):
    if delivery == ql.Settlement.Physical:
        return 'Physical'
    elif delivery == ql.Settlement.Cash:
        return 'Cash'
    else:
        return 'Undefined Delivery Name'

def getSettlementMethodName(settlementMethod):
    if settlementMethod == ql.Settlement.PhysicalOTC:
        return 'PhysicalOTC'
    elif settlementMethod == ql.Settlement.PhysicalCleared:
        return 'PhysicalCleared'
    elif settlementMethod == ql.Settlement.CollateralizedCashPrice:
        return 'CollateralizedCashPrice'
    elif settlementMethod == ql.Settlement.ParYieldCurve:
        return 'ParYieldCurve'
    else:
        return 'Undefind Settlement Method Name'

if __name__ == '__main__':
    inst_df = util_qldf.util_qldf()
    inst_df.set_path('./', 'test_df.csv')
    inst_df.load_df('DATE')

    rate = 0.05
    vol = 0.05

    # swaption = USDSOFRswaption(ql.Date(17, 9, 2018))
    swaption = USDLiborSwaption(ql.Date(17, 9, 2018))

    swaption.setForecastCurve(inst_df.get_discount_yieldtermstructure_handle())
    swaption.setDiscountCurve(inst_df.get_forecast_yieldtermstructure_handle())
    swaption.setDiscountCurve(inst_df.get_discount_yieldtermstructure_handle())
    swaption.makeSwap(ql.Period('5Y'), ql.Period('5Y'), rate, 0.0, 1e10)

    volTypes = [ql.ShiftedLognormal, ql.Normal]
    deliveries = [ql.Settlement.Physical, ql.Settlement.Cash]
    settlementMethods = [
        ql.Settlement.PhysicalOTC,
        ql.Settlement.PhysicalCleared,
        ql.Settlement.CollateralizedCashPrice,
        ql.Settlement.ParYieldCurve
    ]

    result_df = None
    for volType in volTypes:
        for delivery in deliveries:
            for settle in settlementMethods:
                swaption.makeSwaption(vol, volType, delivery, settle)
                try:
                    npv = swaption.payerSwaption.NPV()
                except:
                    npv = None
                finally:
                    record = {
                        'volType': getVolTypeName(volType),
                        'derivery': getDeliveryName(delivery),
                        'settlementMethod': getSettlementMethodName(settle),
                        'NPV': npv
                    }
                    if result_df is None:
                        result_df = pd.DataFrame([record])
                    else:
                        result_df = result_df.append([record], ignore_index=True)

    result_df.dropna(inplace=True)
    result_df.reset_index(drop=True, inplace=True)
    print(result_df)
    print(swaption.getVolatility(ql.ShiftedLognormal, 0.02))
    print(swaption.getVolatility(ql.ShiftedLognormal, 0.01))
    print(swaption.getVolatility(ql.Normal))
    swaption.makeSwaption(0.003010051593568979, ql.Normal, ql.Settlement.Physical)
    print(swaption.getVolatility(ql.ShiftedLognormal, 0.02))

# -*- coding: utf-8 -*-
import QuantLib as ql
import matplotlib.pyplot as plt
import MarketDataSample as mds
import MyYieldCurve as cv

if __name__ == '__main__':
  ## load market data
  dat = mds.MarketDataSample()

  ## build JPYOIS curve
  jpyOIS = cv.MyYieldCurve(ql.OvernightIndex("JPYOIS", 2, ql.JPYCurrency(), ql.Japan(), ql.Actual365Fixed()),
                 2, ql.ModifiedFollowing, ql.Annual, ql.Actual365Fixed())
  jpyOIS.importRatesDepo(dat.dataDepoJPYOIS.values(), dat.dataDepoJPYOIS.keys())
  jpyOIS.importRatesSwap(dat.dataSwapJPYOIS.values(), dat.dataSwapJPYOIS.keys(), None, ql.YieldTermStructureHandle())
  jpyOIS.build()

  ## build JPYL6 curve
  jpyL6 = cv.MyYieldCurve(ql.JPYLibor(ql.Period(6, ql.Months)),
                2, ql.ModifiedFollowing, ql.Semiannual, ql.Actual365Fixed())
  jpyL6.importRatesDepo(dat.dataDepoJPYL6.values(), dat.dataDepoJPYL6.keys())
  jpyL6.importRatesFra(dat.dataFraJPYL6.values(), dat.dataDepoJPYL6.keys())
  jpyL6.importRatesSwap(dat.dataSwapJPYL6.values(), dat.dataSwapJPYL6.keys(), None, jpyOIS.getForecastTermStructureHandle())
  jpyL6.build()

  ## build JPYL3 curve
  jpyL3 = cv.MyYieldCurve(ql.JPYLibor(ql.Period(3, ql.Months)),
                2, ql.ModifiedFollowing, ql.Semiannual, ql.Actual365Fixed())
  jpyL3.importRatesDepo(dat.dataDepoJPYL3.values(), dat.dataDepoJPYL3.keys())
  jpyL3.importRatesFra(dat.dataFraJPYL3.values(), dat.dataDepoJPYL3.keys())
  jpyL3.importRatesSwap(dat.dataSwapJPYL6.values(), dat.dataSwapJPYL6.keys(), dat.dataSpreadJPYL3,
                        jpyOIS.getForecastTermStructureHandle())
  jpyL3.build()

  ## build USDOIS curve
  usdOIS = cv.MyYieldCurve(ql.OvernightIndex("USDOIS", 2, ql.USDCurrency(), ql.UnitedStates(), ql.Actual360()),
                 2, ql.ModifiedFollowing, ql.Annual, ql.Actual360())
  usdOIS.importRatesDepo(dat.dataDepoUSDOIS.values(), dat.dataDepoUSDOIS.keys())
  usdOIS.importRatesSwap(dat.dataSwapUSDOIS.values(), dat.dataSwapUSDOIS.keys(), None, ql.YieldTermStructureHandle())
  usdOIS.build()

  ## build USDL3 curve
  usdL3 = cv.MyYieldCurve(ql.USDLibor(ql.Period(3, ql.Months)),
                2, ql.ModifiedFollowing, ql.Semiannual, ql.Thirty360())
  # usdL3.importRatesFuture(dat.dataFutureUSDL3.keys(), dat.dataFutureUSDL3.values())
  usdL3.importRatesDepo(dat.dataDepoUSDL3.values(), dat.dataDepoUSDL3.keys())
  usdL3.importRatesFra(dat.dataFraUSDL3.values(), dat.dataDepoUSDL3.keys())
  usdL3.importRatesSwap(dat.dataSwapUSDL3.values(), dat.dataSwapUSDL3.keys(), None, usdOIS.getForecastTermStructureHandle())
  usdL3.build()

  ## curve test
  df_jpyOIS = jpyOIS.getNodes()
  df_jpyL6 = jpyL6.getNodes()
  df_jpyL3 = jpyL3.getNodes()
  df_usdOIS = usdOIS.getNodes()
  df_usdL3 = usdL3.getNodes()

  zeroRate_jpyOIS = jpyOIS.getZeroRate()
  zeroRate_jpyL6 = jpyL6.getZeroRate()
  zeroRate_jpyL3 = jpyL3.getZeroRate()
  zeroRate_usdOIS = usdOIS.getZeroRate()
  zeroRate_usdL3 = usdL3.getZeroRate()

  plt.figure()
  plt.title("Discount Factor ( as of :" + jpyOIS.baseDate.ISO() + " )")
  fig_JPYOIS = df_jpyOIS.plot(marker="o", label="JPYOIS")
  fig_JPYL3 = df_jpyL3.plot(marker="v", label="JPYL3")
  fig_JPYL6 = df_jpyL6.plot(marker="^", label="JPYL6")
  fig_USDOIS = df_usdOIS.plot(marker="s", label="USDOIS")
  fig_USDL3 = df_usdL3.plot(marker="p", label="USDL3")
  plt.rcParams['xtick.direction'] = 'in'
  plt.rcParams['ytick.direction'] = 'in'
  plt.grid(linestyle='--', alpha=0.4)
  plt.legend()
  plt.savefig("test_df.pdf")

  plt.figure()
  plt.title("Instantaneous Forward Rate ( as of :" + jpyOIS.baseDate.ISO() + " )")
  fig_JPYOIS = zeroRate_jpyOIS.plot(marker="o", label="JPYOIS")
  fig_JPYL3 = zeroRate_jpyL3.plot(marker="v", label="JPYL3")
  fig_JPYL6 = zeroRate_jpyL6.plot(marker="^", label="JPYL6")
  fig_USDOIS = zeroRate_usdOIS.plot(marker="s", label="USDOIS")
  fig_USDL3 = zeroRate_usdL3.plot(marker="p", label="USDL3")
  plt.rcParams['xtick.direction'] = 'in'
  plt.rcParams['ytick.direction'] = 'in'
  plt.grid(linestyle='--', alpha=0.4)
  plt.legend()
  plt.savefig("test_zeroRate.pdf")

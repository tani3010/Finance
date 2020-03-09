# -*- coding: utf-8 -*-
from BasePricer import BasePricer
import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt


def my_plot(title, xlabel, ylabel, xdata, ydata, labels,
            xlim=None, ylim=None, savefile=None):
    plt.figure()
    plt.title(title)
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    if xlim is not None:
        plt.xlim(xlim)

    if ylim is not None:
        plt.ylim(ylim)

    for x, y, l in zip(xdata, ydata, labels):
        plt.plot(x, y, label=l)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.grid(linestyle='--', alpha=0.4)
    plt.legend()

    if savefile is not None:
        plt.savefig(savefile)
    plt.show()

class HestonPricer(BasePricer):
    def __init__(self):
        super().__init__()

    def set_process(self):
        self.process = ql.HestonProcess(
            self.risk_free_ts, self.dividend_ts,
            self.handles['initS'], self.handles['initV'].value(),
            self.handles['kappa'].value(), self.handles['theta'].value(),
            self.handles['sigma'].value(), self.handles['rho'].value())

    def get_vanilla_option_price_analytic(self, strike, maturity_period,
                                          option_type = ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.model = ql.HestonModel(self.process)
        self.engine = ql.AnalyticHestonEngine(self.model)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()

    def get_vanilla_option_price_fd(self, strike, maturity_period,
                                    option_type = ql.Option.Call):
        self.option = self.vanilla_option_helper(
                strike, maturity_period, option_type)
        self.model = ql.HestonModel(self.process)
        self.engine = ql.FdHestonVanillaEngine(self.model)
        self.option.setPricingEngine(self.engine)
        return self.option.NPV()


if __name__  ==  '__main__':
    initS = 100
    pricer = HestonPricer()
    pricer.set_params(
        initS = initS, initV = 0.16 ** 1,
        risk_free_rate = 0.05 * 0, dividend_rate = 0,
        kappa = 10, theta = 0.15 ** 1, sigma = 0.1, rho = -0.8)
    strike = initS
    strikes = np.linspace(-300, 300, num=200) * 5e-01 + initS
    maturity_period = ql.Period("1Y")
    print('NPV(analytic)    = ',
          pricer.get_vanilla_option_price_analytic(strike, maturity_period))

    dens = [
        pricer.get_implied_density(
            pricer.get_vanilla_option_price_analytic,
            k, gap=1e-01,
            maturity_period=maturity_period) for k in strikes
    ]
    my_plot('Heston Density', 'strike', 'prob', [strikes], [dens], ['dens'])


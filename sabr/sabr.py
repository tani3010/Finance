# -*- coding: utf-8 -*-

from fdsabr import ArbitrageFreeSABR
from fdsabr import FreeBoundarySABR
import QuantLib as ql
import numpy as np
import matplotlib.pyplot as plt

class BaseSmileSection:
    def __init__(self):
        self.base_date = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = self.base_date
        self.cal = ql.JointCalendar(ql.Japan(), ql.UnitedKingdom())
        self.dc = ql.Actual365Fixed()
        self.inst = None

    def set_params(self, option_tenor, forward, alpha, beta, nu, rho, shift=0.0):
        self.tau = self.cal.advance(self.base_date, option_tenor)
        self.tau_term = self.dc.yearFraction(self.base_date, self.tau)
        self.forward = forward
        self.alpha = alpha
        self.beta = beta
        self.nu = nu
        self.rho = rho
        self.shift = shift
        self.sabr_params = [alpha, beta, nu, rho]
        self.create_instance()

    def create_instance(self):
        pass

    def density(self, strikes, discount=1.0, gap=0.0001):
        return [self.inst.density(k, discount, gap) for k in strikes]

    def volatility(self, strikes, volatility_type=ql.ShiftedLognormal):
        return [self.inst.volatility(k, volatility_type, self.shift) for k in strikes]

class MySabrSmileSection(BaseSmileSection):
    def __init__(self):
        super().__init__()

    def create_instance(self):
        self.inst = ql.SabrSmileSection(
            self.tau, self.forward, self.sabr_params, self.dc, self.shift)

class MyNoArbSabrSmileSection(BaseSmileSection):
    def __init__(self):
        super().__init__()

    def create_instance(self):
        self.inst = ql.NoArbSabrSmileSection(
            self.tau, self.forward, self.sabr_params, self.dc, self.shift)

class MyZabrLVSmileSection(BaseSmileSection):
    def __init__(self):
        super().__init__()

    def create_instance(self):
        self.sabr_params.append(1.0)  # append gamma parameter
        self.inst = ql.ZabrLocalVolatilitySmileSection(
            self.tau, self.forward, self.sabr_params, self.dc)

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

if __name__ == '__main__':
    option_tenor_str = '1Y'
    option_tenor = ql.Period(option_tenor_str)
    forward = 0.0488
    alpha = 0.026
    beta = 0.5
    nu = 0.4
    rho = -0.1
    shift = 0.02
    sss = MySabrSmileSection()
    sss_shift = MySabrSmileSection()
    nss = MyNoArbSabrSmileSection()
    zss_lv = MyZabrLVSmileSection()
    sss.set_params(option_tenor, forward, alpha, beta, nu, rho)
    sss_shift.set_params(option_tenor, forward, alpha, beta, nu, rho, shift)
    nss.set_params(option_tenor, forward, alpha, beta, nu, rho)
    zss_lv.set_params(option_tenor, forward, alpha, beta, nu, rho)
    strikes = np.linspace(0.0001, 0.1, 700)

    nd = 6
    N = 200
    T = sss.tau_term
    timesteps = 100*int(T)
    af = ArbitrageFreeSABR()
    fb = FreeBoundarySABR()
    af.makeTransformedSABRDensityLawsonSwayne(alpha, beta, nu, rho, forward, T, N, timesteps, nd, shift)
    fb.makeTransformedSABRDensityLawsonSwayne(alpha, beta, nu, rho, forward, T, N, timesteps, nd, shift)

    my_plot('SABR shifted Black Volatility', 'strike', 'volatility',
            [strikes, strikes, strikes, strikes, strikes, strikes],
            [sss.volatility(strikes), sss_shift.volatility(strikes),
             nss.volatility(strikes), zss_lv.volatility(strikes),
             af.volatility(strikes), fb.volatility(strikes)],
            ['SABR', 'shifted SABR', 'No-Arbitrage SABR', 'ZABR (Local Volatility)',
             'Arbitrage-Free shifted SABR', 'Free-Boundary shifted SABR'],
            None, None,
            './sabrblackvolatility.pdf')

    my_plot('SABR Normal Volatility', 'strike', 'volatility',
            [strikes, strikes, strikes, strikes],
            [sss.volatility(strikes, ql.Normal), sss_shift.volatility(strikes, ql.Normal),
             nss.volatility(strikes, ql.Normal), zss_lv.volatility(strikes, ql.Normal)],
            ['SABR', 'shifted SABR', 'NoArb-SABR', 'ZABR (Local Volatility)'],
            None, None,
            './sabrnormalvolatility.pdf')

    my_plot('SABR implied density', 'strike', 'density',
            [strikes, strikes, strikes, strikes, strikes, strikes],
            [sss.density(strikes), sss_shift.density(strikes),
             nss.density(strikes), zss_lv.density(strikes),
             af.density(strikes), fb.density(strikes)],
            ['SABR', 'shifted SABR', 'No-Arbitrage SABR', 'ZABR (Local Volatility)',
             'Arbitrage-Free shifted SABR', 'Free-Boundary shifted SABR'],
            None, [-10, 40],
            './sabrimplieddensity.pdf')
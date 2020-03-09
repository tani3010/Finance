# -*- coding,  utf-8 -*-

## implementation of following Free-Boundary SABR in python
## Floc'h, L., & Kennedy, G. J. (2014). Finite difference techniques for arbitrage free SABR. Available at SSRN 2402001.

import numpy as np
from scipy.interpolate import interp1d
from QuantLib import ShiftedLognormal, Normal
import QuantLib as ql
import matplotlib.pyplot as plt

def func_getImpliedShiftedBlackVolatility(
    premium, strike, forward, risk_free_rate, maturity, shift):
    tmp = ql.blackFormulaImpliedStdDev(
        ql.Option.Call, strike, forward, premium, 1.0, shift)/np.sqrt(maturity)
    return tmp if tmp != 0 else None

class BaseFDSABR:
    def __init__(self):
        self.cached = False

    def density(self, strikes, discount=1.0, gap=1e-04):
        f = interp1d(self.Fm_shifted, self.probability_density, kind='slinear')
        return f(strikes)

    def volatility(self, k, volatility_type=ShiftedLognormal):
        if volatility_type == Normal:
            return
        elif volatility_type == ShiftedLognormal:
            premiums = [
                self.priceCallTransformedSABRDensity(strike) for strike in k
            ]
            # print(premiums)
            return [
                func_getImpliedShiftedBlackVolatility(
                    premium, strike, self.forward, 0, self.T, self.shift)
                for premium, strike in zip(premiums, k)
            ]
        else:
            print('Unknown volatility type was selected.')

    @staticmethod
    def Y(alpha, nu, rho, zm):
        return alpha/nu*(np.sinh(nu*zm)+rho*(np.cosh(nu*zm)-1))

    @staticmethod
    def F(forward, beta, ym, shift=0):
        print('Not implemented.')

    @staticmethod
    def C(alpha, beta, rho, nu, ym, Fm):
        print('Not implemented.')

    @staticmethod
    def G(forward, beta, Fm, j0, shift=0):
        print('Not implemented.')

    @staticmethod
    def computeBoundaries(alpha, beta, nu, rho, forward, T, nd, shift=0):
        print('Not implemented.')

    def makeForward(self, alpha, beta, nu, rho, forward, z, shift=0):
        return self.F(forward, beta, self.Y(alpha, nu, rho, z), shift)

    @staticmethod
    def yOfStrike(strike, forward, beta, shift=0):
        print('Not implemented.')

    @staticmethod
    def solveStep(Fm, Cm, Em, dt, h, P, PL, PR):
        frac = dt/(2*h)
        M = len(P)
        A = np.zeros(M-1)
        B = np.zeros(M)
        C = np.zeros(M-1)
        B[1:(M-1)] = 1+frac*(Cm[1:(M-1)]*Em[1:(M-1)]*(1/(Fm[2:M]-Fm[1:(M-1)])+1/(Fm[1:(M-1)]-Fm[0:(M-2)])))
        C[1:(M-1)] = -frac*Cm[2:M]*Em[2:M]/(Fm[2:M]-Fm[1:(M-1)])
        A[0:(M-2)] = -frac*Cm[0:(M-2)]*Em[0:(M-2)]/(Fm[1:(M-1)]-Fm[0:(M-2)])
        B[0] = Cm[0]/(Fm[1]-Fm[0])*Em[0]
        C[0] = Cm[1]/(Fm[1]-Fm[0])*Em[1]
        B[M-1] = Cm[M-1]/(Fm[M-1]-Fm[M-2])*Em[M-1]
        A[M-2] = Cm[M-2]/(Fm[M-1]-Fm[M-2])*Em[M-2]
        tri = np.diag(B)+np.diag(A, -1)+np.diag(C, 1)
        P[0] = 0
        P[M-1] = 0
        P = np.linalg.solve(tri, P)
        PL = PL+dt*Cm[1]/(Fm[1]-Fm[0])*Em[1]*P[1]
        PR = PR+dt*Cm[M-2]/(Fm[M-1]-Fm[M-2])*Em[M-2]*P[M-2]
        return {
            'P': P,
            'PL': PL,
            'PR': PR
        }

    def priceCallTransformedSABRDensity(self, strike):
        if not self.cached:
            print('probability density was not cached.')
            return

        ystrike = self.yOfStrike(strike, self.forward, self.beta, self.shift)
        zstrike = -1/self.nu*np.log((np.sqrt(1-self.rho**2+(self.rho+self.nu*ystrike/self.alpha)**2)-self.rho-self.nu*ystrike/self.alpha)/(1-self.rho))
        if zstrike <= self.zmin:
            p = self.forward-strike
        else:
            if zstrike >= self.zmax:
                p = 0
            else:
                Fmax = self.makeForward(self.alpha, self.beta, self.nu, self.rho, self.forward, self.zmax, self.shift)
                p = (Fmax-(strike+self.shift))*self.PR
                k0 = int(np.ceil((zstrike-self.zmin)/self.h))
                ztilde = self.zmin+k0*self.h
                ftilde = self.makeForward(self.alpha, self.beta, self.nu, self.rho, self.forward, ztilde, self.shift)
                term = ftilde-(strike+self.shift)
                if term > 1e-5:
                    zm = self.zmin+(k0-0.5)*self.h
                    Fm = self.makeForward(self.alpha, self.beta, self.nu, self.rho, self.forward, zm, self.shift)
                    dFdz = (ftilde-Fm)/(ztilde-zm)
                    p += 0.5*term**2*self.P[k0]/dFdz
                if (k0+1) == (len(self.P)-1):
                    k = np.array([k0+1])
                else:
                    k = np.array(range(k0+1, len(self.P)-1))
                zm = self.zmin+(k-0.5)*self.h
                Fm = self.makeForward(self.alpha, self.beta, self.nu, self.rho, self.forward, zm, self.shift)
                p += np.sum((Fm-(strike+self.shift))*self.h*self.P[k])
        return p

    def makeTransformedSABRDensityLawsonSwayne(self, alpha, beta, nu, rho, forward, T, N, timesteps, nd, shift=0):
        tmp = self.computeBoundaries(alpha, beta, nu, rho, forward, T, nd, shift)
        zmin = tmp['zmin']
        zmax = tmp['zmax']
        J = N-2
        h0 = (zmax-zmin)/J
        j0 = int((0-zmin)/h0)
        h = (0-zmin)/(j0-0.5)
        z = np.array(range(0, J+2))*h+zmin
        zmax = z[J]
        zm = z-0.5*h
        ym = self.Y(alpha, nu, rho, zm)
        ymax = self.Y(alpha, nu, rho, zmax)
        ymin = self.Y(alpha, nu, rho, zmin)
        Fm = self.F(forward, beta, ym, shift)
        Fmax = self.F(forward, beta, ymax, shift)
        Fmin = self.F(forward, beta, ymin, shift)
        Fm[0] = 2*Fmin-Fm[1]
        Fm[J+1] = 2*Fmax-Fm[J]
        Cm = self.C(alpha, beta, rho, nu, ym, Fm)
        Cm[0] = Cm[1]
        Cm[J+1] = Cm[J]
        Gammam = self.G(forward, beta, Fm, j0, shift)
        dt = T/timesteps
        b = 1-0.5*np.sqrt(2)
        dt1 = dt*b
        dt2 = dt*(1-2*b)
        Em = np.ones(J+2)
        Emdt1 = np.exp(rho*nu*alpha*Gammam*dt1)
        Emdt1[0] = Emdt1[1]
        Emdt1[J+1] = Emdt1[J]
        Emdt2 = np.exp(rho*nu*alpha*Gammam*dt2)
        Emdt2[0] = Emdt2[1]
        Emdt2[J+1] = Emdt2[J]
        PL = 0
        PR = 0
        P = np.zeros(J+2)
        P[j0] = 1/h
        for t in range(timesteps):
            Em = Em*Emdt1
            tmp = self.solveStep(Fm, Cm, Em, dt1, h, P, PL, PR)
            P1 = tmp['P']
            PL1 = tmp['PL']
            PR1 = tmp['PR']
            Em = Em*Emdt1
            tmp = self.solveStep(Fm, Cm, Em, dt1, h, P1, PL1, PR1)
            P2 = tmp['P']
            PL2 = tmp['PL']
            PR2 = tmp['PR']
            P = (np.sqrt(2)+1)*P2-np.sqrt(2)*P1
            PL = (np.sqrt(2)+1)*PL2-np.sqrt(2)*PL1
            PR = (np.sqrt(2)+1)*PR2-np.sqrt(2)*PR1
            Em = Em*Emdt2

        P[P < 0] = 0
        self.forward = forward
        self.alpha = alpha
        self.beta = beta
        self.nu = nu
        self.rho = rho
        self.shift = shift
        self.T = T
        self.P = P
        self.PL = PL
        self.PR = PR
        self.zm = zm
        self.zmin = zmin
        self.zmax = zmax
        self.Cm = Cm
        self.Fm = Fm
        self.Fm_shifted = Fm - shift
        self.h = h
        self.probability_density = P/Cm
        self.cached = True

class ArbitrageFreeSABR(BaseFDSABR):
    def __init__(self):
        super().__init__()

    @staticmethod
    def F(forward, beta, ym, shift=0):
        return ((forward+shift)**(1-beta)+(1-beta)*ym)**(1/(1-beta))

    @staticmethod
    def C(alpha, beta, rho, nu, ym, Fm):
        return np.sqrt(alpha**2+2*rho*alpha*nu*ym+nu**2*ym**2)*Fm**beta

    @staticmethod
    def G(forward, beta, Fm, j0, shift=0):
        G = ((Fm+shift)**beta-(forward+shift)**beta)/(Fm-forward)
        G[j0] = beta/(forward+shift)**(1-beta)
        return G

    @staticmethod
    def computeBoundaries(alpha, beta, nu, rho, forward, T, nd, shift=0):
        zmin = -nd*np.sqrt(T)
        zmax = -zmin
        if beta < 1:
            ybar = -(forward+shift)**(1-beta)/(1-beta)
            zbar = -1/nu*np.log((np.sqrt(1-rho**2+(rho+nu*ybar/alpha)**2)-rho-nu*ybar/alpha)/(1-rho))
            if zbar > zmin:
                zmin = zbar
        return {
            'zmin': zmin,
            'zmax': zmax
        }

    @staticmethod
    def yOfStrike(strike, forward, beta, shift=0):
        return ((strike+shift)**(1-beta)-(forward+shift)**(1-beta))/(1-beta)

class FreeBoundarySABR(BaseFDSABR):
    def __init__(self):
        super().__init__()

    @staticmethod
    def F(forward, beta, ym, shift=0):
        u = np.sign(forward+shift)*np.abs(forward+shift)**(1-beta)+(1-beta)*ym
        return np.sign(u)*np.abs(u)**(1/(1-beta))

    @staticmethod
    def C(alpha, beta, rho, nu, ym, Fm):
        return np.sqrt(alpha**2+2*rho*alpha*nu*ym+nu**2*ym**2)*np.abs(Fm)**beta

    @staticmethod
    def G(forward, beta, Fm, j0, shift=0):
        G = (np.abs(Fm+shift)**beta-np.abs(forward+shift)**beta)/(Fm-forward)
        G[j0] = np.sign(forward+shift)*beta/np.abs(forward+shift)**(1-beta)
        return G

    @staticmethod
    def computeBoundaries(alpha, beta, nu, rho, forward, T, nd, shift=0):
        return {
            'zmin': -nd*np.sqrt(T),
            'zmax': nd*np.sqrt(T)
        }

    @staticmethod
    def yOfStrike(strike, forward, beta, shift=0):
        return (np.sign(strike+shift)*np.abs(strike+shift)**(1-beta)-np.sign(forward+shift)*np.abs(forward+shift)**(1-beta))/(1-beta)

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


if __name__  ==  '__main__':
    af = ArbitrageFreeSABR()
    fb = FreeBoundarySABR()

    forward = 50/100/100
    beta = 0.25
    alpha = 0.6*forward**(1-beta)
    nu = 0.3
    rho = -0.3

    forward = 0.0488
    # forward = -0.004
    alpha = 0.026
    beta = 0.5
    nu = 0.4
    rho = -0.1
    shift = 0.02
    T = 1
    nd = 6
    N = 100
    timesteps = 100*T
    strikes = np.linspace(1e-07, 0.1, 80) - shift

    af.makeTransformedSABRDensityLawsonSwayne(alpha, beta, nu, rho, forward, T, N, timesteps, nd, shift)
    fb.makeTransformedSABRDensityLawsonSwayne(alpha, beta, nu, rho, forward, T, N, timesteps, nd, shift)

    my_plot('PDF of advanced SABR model', 'strike', 'density',
           [af.Fm_shifted, fb.Fm_shifted],
           [af.probability_density, fb.probability_density],
           ['Arbitrage-Free SABR', 'Free-Boundary SABR'],
           None, None, None)

    prems_af = [af.priceCallTransformedSABRDensity(k) for k in strikes]
    prems_fb = [fb.priceCallTransformedSABRDensity(k) for k in strikes]
    vol_af = af.volatility(strikes)
    vol_fb = fb.volatility(strikes)

    my_plot('Premium of advanced SABR model', 'strike', 'premium',
            [strikes, strikes],
            [prems_af, prems_fb],
            ['Arbitrage-Free SABR', 'Free-Boundary SABR'],
            None, None, None)

    my_plot('Black Volatility of advanced SABR model', 'strike', 'Black Volatility',
            [strikes, strikes],
            [vol_af, vol_fb],
            ['Arbitrage-Free SABR', 'Free-Boundary SABR'],
            None, None, None)



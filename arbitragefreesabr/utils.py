# -*- coding,  utf-8 -*-
import sys
import QuantLib as ql
from numpy import exp, log, sqrt
from numpy import inf
from scipy.stats import norm, lognorm
from scipy.special import jv
from scipy.integrate import quad
from scipy.optimize import newton

## number of constant
CONST_TOLERANCE_MASTER = sys.float_info.epsilon ** 0.5
CONST_TOLERANCE_INTEGRATION = CONST_TOLERANCE_MASTER
CONST_TOLERANCE_OPTIMIZATION_ERROR = CONST_TOLERANCE_MASTER

## get plain vanilla payoff of call
## x: terminal value of underlying asset
## K: execution price
## gearing: gearing of underlying asset
def func_payoff_vanillaCall(x, K, gearing=1):
    return max(x * gearing - K, 0)

## get plain vanilla payoff of put
## x: terminal value of underlying asset
## K: execution price
## gearing: gearing of underlying asset
def func_payoff_vanillaPut(x, K, gearing=1):
    return max(K - x * gearing, 0)

## get call price by Black-Scholes formula
## K: execution price
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
def func_getCallPriceByBlackScholesFormula(K, initS, riskFreeRate, dividendRate, volatility, maturity):
    mu = riskFreeRate - dividendRate
    d1 = (log(initS / K) + (mu + 0.5 * volatility ** 2) * maturity) / (volatility * sqrt(maturity))
    d2 = (log(initS / K) + (mu - 0.5 * volatility ** 2) * maturity) / (volatility * sqrt(maturity))
    return initS * exp(-dividendRate * maturity) * norm.cdf(d1) - K * exp(-riskFreeRate * maturity) * norm.cdf(d2)

## get put price by Black-Scholes formula
## K: execution price
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
def func_getPutPriceByBlackScholesFormula(K, initS, riskFreeRate, dividendRate, volatility, maturity):
    mu = riskFreeRate - dividendRate
    d1 = (log(initS / K) + (mu + 0.5 * volatility ** 2) * maturity) / (volatility * sqrt(maturity))
    d2 = (log(initS / K) + (mu - 0.5 * volatility ** 2) * maturity) / (volatility * sqrt(maturity))
    return K * exp(-riskFreeRate * maturity) * norm.cdf(-d2) - initS * exp(-dividendRate * maturity) * norm.cdf(-d1)

## get call price by Black formula
## K: execution price
## forward: initial forward of underlying asset
## riskFreeRate: riskfree rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
## shift: width of volatility shift
def func_getCallPriceByBlackFormula(K, forward, riskFreeRate, volatility, maturity, shift=0):
    d1 = (log((forward + shift) / (K + shift)) + 0.5 * volatility ** 2 * maturity) / (volatility * sqrt(maturity))
    d2 = (log((forward + shift) / (K + shift)) - 0.5 * volatility ** 2 * maturity) / (volatility * sqrt(maturity))
    return exp(-riskFreeRate * maturity) * ((forward + shift) * norm.cdf(d1) - (K + shift) * norm.cdf(d2))

## get put price by Black formula
## K: execution price
## forward: initial forward of underlying asset
## riskFreeRate: riskfree rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
## shift: width of volatility shift
def func_getPutPriceByBlackFormula(K, forward, riskFreeRate, volatility, maturity, shift=0):
    d1 = (log((forward + shift) / (K + shift)) + 0.5 * volatility ** 2 * maturity) / (volatility * sqrt(maturity))
    d2 = (log((forward + shift) / (K + shift)) - 0.5 * volatility ** 2 * maturity) / (volatility * sqrt(maturity))
    return exp(-riskFreeRate * maturity) * ((K + shift) * norm.cdf(-d2) - (forward + shift) * norm.cdf(-d1))

## get terminal value of Geometric Brownian Motion by monte carlo simulation
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
## n: the number of path in simulation
def func_getTerminalValueByMC_gbm(initS, riskFreeRate, dividendRate, volatility, maturity, n):
    mu = riskFreeRate - dividendRate
    return initS * exp((mu - 0.5 * volatility ** 2) * maturity + volatility * sqrt(maturity) * norm.rvs(size=n))

## get probability density of Geometric Brownian Motion
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
def func_density_gbm(x, initS, riskFreeRate, dividendRate, volatility, maturity):
    mu = riskFreeRate - dividendRate
    return lognorm.pdf(x,
        s=volatility*sqrt(maturity),
        loc=0,
        scale=initS*exp((mu-0.5*volatility**2)*maturity))

## get probability density of CEV process
## "Computing the Constant Elasticity of Variance Option Pricing Formula"
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## beta: elasticity parameter of CEV process
## maturity: term to maturity in year basis
def func_density_cev(x, initS, riskFreeRate, dividendRate, volatility, beta, maturity):
    mu = riskFreeRate - dividendRate
    k = 2 * mu / (volatility**2 * (2 - beta) * (exp(mu * (2 - beta) * maturity) - 1))
    m = k * initS ** (2 - beta) * exp(mu * (2 - beta) * maturity)
    w = k * x**(2 - beta)
    return \
        (2-beta)*k**(1/(2-beta))*(m*w**(1-2*beta))**(1/(4-2*beta))*exp(-m-w)*jv(1/(2-beta), 2*sqrt(m*w))

## get call price by integration
## func_density: density function of underlying
## K: execution price
## lower: lower bound of integration
## upper: upper bound of integration
## discount: discount factor in some numeraire
## gearing: gearing
## kargs: additional arguments of func.density
def func_getCallPriceByIntegration(func_density, K, lower=-inf, upper=inf, discount=1, gearing=1, **kargs):
    def func_integrand(x):
      return func_payoff_vanillaCall(x, K, gearing) * func_density(x=x, **kargs)

    return discount * quad(func_integrand, a=lower, b=upper, epsrel=CONST_TOLERANCE_INTEGRATION)[0]

## get put price by integration
## func_density: density function of underlying
## K: execution price
## lower: lower bound of integration
## upper: upper bound of integration
## discount: discount factor in some numeraire
## gearing: gearing
## kargs: additional arguments of func.density
def func_getPutPriceByIntegration(func_density, K, lower=-inf, upper=inf, discount=1, gearing=1, **kargs):
    def func_integrand(x):
      return func_payoff_vanillaPut(x, K, gearing) * func_density(x=x, **kargs)

    return discount * quad(func_integrand, a=lower, b=upper, epsrel=CONST_TOLERANCE_INTEGRATION)[0]

## get implied shifted Black volatility
## K: execution price
## forward: initial forward of underlying asset
## riskFreeRate: riskfree rate
## maturity: term to maturity in year basis
## shift: width of volatility shift
def func_getImpliedShiftedBlackVolatility(premium, K, forward, riskFreeRate, maturity, shift=0):
    def f(x):
        if forward <= K:
            calculated_premium = func_getCallPriceByBlackFormula(K, forward, riskFreeRate, x, maturity, shift)
        else:
            calculated_premium = func_getPutPriceByBlackFormula(K, forward, riskFreeRate, x, maturity, shift)
        return premium - calculated_premium

    return newton(f, 0.5, tol=CONST_TOLERANCE_OPTIMIZATION_ERROR)


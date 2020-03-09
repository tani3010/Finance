## utility functions in finance

## number of constant
CONST_TOLERANCE_MASTER <- .Machine$double.eps^0.5
CONST_TOLERANCE_INTEGRATION <- CONST_TOLERANCE_MASTER
CONST_TOLERANCE_OPTIMIZATION_ERROR <- CONST_TOLERANCE_MASTER

## get plain vanilla payoff of call
## x: terminal value of underlying asset
## K: execution price
## gearing: gearing of underlying asset
func.payoff.vanillaCall <- function(x, K, gearing = 1) {
  return(pmax(x * gearing - K, 0))
}

## get plain vanilla payoff of put
## x: terminal value of underlying asset
## K: execution price
## gearing: gearing of underlying asset
func.payoff.vanillaPut <- function(x, K, gearing = 1) {
  return(pmax(K - x * gearing, 0))
}

## get call price by Black-Scholes formula
## K: execution price
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
func.getCallPriceByBlackScholesFormula <- function(K, initS, riskFreeRate, dividendRate, volatility, maturity) {
  mu <- riskFreeRate - dividendRate
  d1 <- (log(initS / K) + (mu + 0.5 * volatility^2) * maturity) / (volatility * sqrt(maturity))
  d2 <- (log(initS / K) + (mu - 0.5 * volatility^2) * maturity) / (volatility * sqrt(maturity))
  return(
    initS * exp(-dividendRate * maturity) * pnorm(d1) - K * exp(-riskFreeRate * maturity) * pnorm(d2)
  )
}

## get put price by Black-Scholes formula
## K: execution price
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
func.getPutPriceByBlackScholesFormula <- function(K, initS, riskFreeRate, dividendRate, volatility, maturity) {
  mu <- riskFreeRate - dividendRate
  d1 <- (log(initS / K) + (mu + 0.5 * volatility^2) * maturity) / (volatility * sqrt(maturity))
  d2 <- (log(initS / K) + (mu - 0.5 * volatility^2) * maturity) / (volatility * sqrt(maturity))
  return(
    K * exp(-riskFreeRate * maturity) * pnorm(-d2) - initS * exp(-dividendRate * maturity) * pnorm(-d1)
  )
}

## get call price by Black formula
## K: execution price
## forward: initial forward of underlying asset
## riskFreeRate: riskfree rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
## shift: width of volatility shift
func.getCallPriceByBlackFormula <- function(K, forward, riskFreeRate, volatility, maturity, shift = 0) {
  d1 <- (log((forward + shift) / (K + shift)) + 0.5 * volatility^2 * maturity) / (volatility * sqrt(maturity))
  d2 <- (log((forward + shift) / (K + shift)) - 0.5 * volatility^2 * maturity) / (volatility * sqrt(maturity))
  return(
    exp(-riskFreeRate * maturity) * ((forward + shift) * pnorm(d1) - (K + shift) * pnorm(d2))
  )
}

## get put price by Black formula
## K: execution price
## forward: initial forward of underlying asset
## riskFreeRate: riskfree rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
## shift: width of volatility shift
func.getPutPriceByBlackFormula <- function(K, forward, riskFreeRate, volatility, maturity, shift = 0) {
  d1 <- (log((forward + shift) / (K + shift)) + 0.5 * volatility^2 * maturity) / (volatility * sqrt(maturity))
  d2 <- (log((forward + shift) / (K + shift)) - 0.5 * volatility^2 * maturity) / (volatility * sqrt(maturity))
  return(
    exp(-riskFreeRate * maturity) * ((K + shift) * pnorm(-d2) - (forward + shift) * pnorm(-d1))
  )
}

## get terminal value of Geometric Brownian Motion by monte carlo simulation
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
## n: the number of path in simulation
func.getTerminalValueByMC.gbm <- function(initS, riskFreeRate, dividendRate, volatility, maturity, n) {
  mu <- riskFreeRate - dividendRate
  return(
    initS * exp((mu - 0.5 * volatility^2) * T + volatility * sqrt(maturity) * rnorm(n))
  )
}

## get probability density of Geometric Brownian Motion
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## maturity: term to maturity in year basis
func.density.gbm <- function(x, initS, riskFreeRate, dividendRate, volatility, maturity) {
  mu <- riskFreeRate - dividendRate
  return(
    dlnorm(x,
           meanlog=log(initS)+(mu-0.5*volatility^2)*maturity,
           sdlog=volatility*sqrt(maturity))
  )
}


## get probability density of CEV process
## "Computing the Constant Elasticity of Variance Option Pricing Formula"
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## beta: elasticity parameter of CEV process
## maturity: term to maturity in year basis
##
## Schroder, M. (1989). Computing the constant elasticity of variance option pricing formula. the Journal of Finance, 44(1), 211-219.
##
func.density.cev <- function(x, initS, riskFreeRate, dividendRate, volatility, beta, maturity) {
  mu <- riskFreeRate - dividendRate
  tmpbeta <- 2*beta
  k <- 2 * mu / (volatility^2 * (2 - tmpbeta) * (exp(mu * (2 - tmpbeta) * maturity) - 1))
  m <- k * initS^(2 - tmpbeta) * exp(mu * (2 - tmpbeta) * maturity)
  w <- k * x^(2 - tmpbeta)
  return(
    (2-tmpbeta)*k^(1/(2-tmpbeta))*(m*w^(1-2*tmpbeta))^(1/(4-2*tmpbeta))*exp(-m-w)*besselI(2*sqrt(m*w), nu=1/(2-tmpbeta))
  )
}

## get call price by integration
## func.density: density function of underlying
## K: execution price
## lower: lower bound of integration
## upper: upper bound of integration
## discount: discount factor in some numeraire
## gearing: gearing
## ...: additional arguments of func.density
func.getCallPriceByIntegration <- function(func.density, K, lower = -Inf, upper = Inf, discount = 1, gearing = 1, ...) {
  func.integrand <- function(x) {
    return(func.payoff.vanillaCall(x, K, gearing) * func.density(x = x, ...))
  }
  return(discount * integrate(func.integrand, lower=lower, upper=upper, rel.tol = CONST_TOLERANCE_INTEGRATION)$value)
}

## get put price by integration
## func.density: density function of underlying
## K: execution price
## lower: lower bound of integration
## upper: upper bound of integration
## discount: discount factor in some numeraire
## gearing: gearing
## ...: additional arguments of func.density
func.getPutPriceByIntegration <- function(func.density, K, lower = -Inf, upper = Inf, discount = 1, gearing = 1, ...) {
  func.integrand <- function(x) {
    return(func.payoff.vanillaPut(x, K, gearing) * func.density(x = x, ...))
  }
  return(discount * integrate(func.integrand, lower = lower, upper = upper, rel.tol = CONST_TOLERANCE_INTEGRATION)$value)
}

## get CEV call price by integration
## K: execution price
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## beta: constant elasticity parameter of CEV process
## maturity: term to maturity in year basis
## upper: upper bound of integration
## discount: discount factor in some numeraire
## gearing: gearing
func.getCEVCallPriceByIntegration <- function(
  K, initS, riskFreeRate, dividendRate, volatility, beta, maturity, upper = 1000, discount = 1, gearing = 1) {

  func.integrand <- function(x) {
    return(
      func.payoff.vanillaCall(x, K, gearing) * func.density.cev(x = x, initS, riskFreeRate, dividendRate, volatility, beta, maturity))
  }
  return(discount * integrate(func.integrand, lower = 0, upper = upper, rel.tol = CONST_TOLERANCE_INTEGRATION)$value)
}

## get CEV put price by integration
## K: execution price
## initS: initial value of underlying asset
## riskFreeRate: riskfree rate
## dividendRate: dividend rate
## volatility: volatility of underlying asset
## beta: constant elasticity parameter of CEV process
## maturity: term to maturity in year basis
## upper: upper bound of integration
## discount: discount factor in some numeraire
## gearing: gearing
func.getCEVPutPriceByIntegration <- function(
  K, initS, riskFreeRate, dividendRate, volatility, beta, maturity, upper = 1000, discount = 1, gearing = 1) {

  func.integrand <- function(x) {
    return(
      func.payoff.vanillaPut(x, K, gearing) * func.density.cev(x = x, initS, riskFreeRate, dividendRate, volatility, beta, maturity))
  }
  return(discount * integrate(func.integrand, lower = 0, upper = upper, rel.tol = CONST_TOLERANCE_INTEGRATION)$value)
}

## get implied shifted Black volatility
## K: execution price
## forward: initial forward of underlying asset
## riskFreeRate: riskfree rate
## maturity: term to maturity in year basis
## shift: width of volatility shift
func.getImpliedShiftedBlackVolatility <- function(premium, K, forward, riskFreeRate, maturity, shift = 0) {
  f <- function(x) {
    return(
      premium - ifelse(forward <= K,
        func.getCallPriceByBlackFormula(K, forward, riskFreeRate, x, maturity, shift),
        func.getPutPriceByBlackFormula(K, forward, riskFreeRate, x, maturity, shift))
    )
  }
  return(
    uniroot(f, c(0, 5), tol = CONST_TOLERANCE_OPTIMIZATION_ERROR)$root
  )
}





### exapmples

func.getImpliedShiftedBlackVolatility(
  func.getCallPriceByBlackFormula(0.05, 0.04, 0.02, 0.4, 1),
  0.05, 0.04, 0.02, 1
)

func.density.cev(
  80, initS = 80, riskFreeRate = 0.03, dividendRate = 0, volatility = 1.33, beta = 0.5, maturity = 5
)

func.getCallPriceByIntegration(
  func.density.cev, K = 80, discount = exp(-5 * 0.03), lower = 0,
  initS = 80, riskFreeRate = 0.0, dividendRate = 0.03, volatility = 1.33, beta = 0.5, maturity = 5
)


# density(initS*exp((riskFreeRate-0.5*volatility^2)*T+volatility*sqrt(maturity)*rnorm(n.mc)), from=0, to=max(x))

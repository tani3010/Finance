# source("./utils.R")

K <- 80
initS <- 80
riskFreeRate <- 0.03
dividendRate <- 0
volatility <- 0.3
beta <- 0.5
maturity <- 1
discount <- exp(-riskFreeRate * maturity)
n <- 1e06

func.getCallPriceByBlackScholesFormula(K, initS, riskFreeRate, dividendRate, volatility, maturity)
func.getCallPriceByIntegration(
  func.density.gbm, K = K, discount = discount, initS = initS, riskFreeRate = riskFreeRate,
  dividendRate = dividendRate, volatility = volatility, maturity = maturity
)

mean(
  func.payoff.vanillaCall(
    func.getTerminalValueByMC.gbm(initS, riskFreeRate, dividendRate, volatility, maturity, n), K)
) * discount


func.getCallPriceByIntegration(
  func.density.cev, K = K, discount = discount, lower = 0,
  initS = initS, riskFreeRate = riskFreeRate, dividendRate = dividendRate, volatility = volatility,
  beta = beta, maturity = maturity
)


# install.packages(c("PerformanceAnalytics", "PortfolioAnalytics", "DEoptim"))

library(Cairo)
library(dplyr)
library(PerformanceAnalytics)
library(PortfolioAnalytics)

data(managers)
dat <- managers
charts.PerformanceSummary(dat, colorset = rainbow(ncol(dat)),
                          main = "Performance Summary", methods = c("StdDev", "HistoricalVaR"))

spec <- portfolio.spec(assets = names(dat)) %>%
  add.constraint(type = "weight_sum", min_sum = -2, max_sum = 2) %>%
  add.constraint(type = "box", min = -0.2, max = 0.2) %>%
  add.constraint(type = "position_limit", max_pos = ncol(dat)) %>%
  add.objective(type = "return", name = "mean") %>%
  add.objective(type = "risk", name = "StdDev")
rp <- random_portfolios(spec, 5000, "sample")
port.opt <- optimize.portfolio(dat, spec, optimize_method = "random", rp = rp, trace = TRUE)

CairoPDF("./portfoliooptimization.pdf", width = 7, height = 8)
plot(port.opt, main = "Optimal Portfolio", risk.col = "StdDev", neighbors = 10,
     panel.first = grid(), tcl = 0.25)
dev.off()

bt <- suppressMessages(optimize.portfolio.rebalancing(
  dat, spec, optimize_method = "DEoptim", rebalance_on = "quarters", training_period = 70, traceDE = 0))

CairoPDF("./rebalancing.pdf", width = 7, height = 7)
chart.Weights(bt, main = "weights plot", col = rainbow(ncol(dat)), las = 1, tcl = 0.25)
dev.off()
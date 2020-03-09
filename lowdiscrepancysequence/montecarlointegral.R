library(Cairo)
library(cubature)
library(randtoolbox)

func <- function(x) exp(-x[1]^2-x[2]^2-x[3]^2)
adaptIntegrate(func, c(0, 0, 0), c(1, 1, 1))
value.analytical <- adaptIntegrate(func, c(0, 0, 0), c(1, 1, 1))$integral

n <- 200
divisor <- 1:n

rand.pseudo <- cbind(runif(n), runif(n), runif(n))
rand.halton <- halton(n, 3)
rand.sobol <- sobol(n, 3)
mc <- cumsum(exp(-rowSums(rand.pseudo^2))) / divisor
qmc.halton <- cumsum(exp(-rowSums(rand.halton^2))) / divisor
qmc.sobol <- cumsum(exp(-rowSums(rand.sobol^2))) / divisor

CairoPDF("./motecarlointegral.pdf", width = 7, height = 7)
plot(mc, type = "l", col = 2, ylim = c(0.3, 0.6),
     las = 1, panel.first = grid(), tcl = 0.25, cex = 2,
     xlab = "simulation num", ylab = "integral value",
     main = "montecarlo integral")
lines(qmc.halton, col = 3)
lines(qmc.sobol, col = 4)
abline(h = value.analytical)
legend("topright", c("MC", "QMC: halton", "QMC: sobol", "analytical value"),
       lty = rep(1, 4), col = c(2, 3, 4, 1))
dev.off()

library(Cairo)
library(MASS)
library(mvtnorm)
library(Rcpp)

sourceCpp("./hamiltonianmontecarlo.cpp")  # compile Rcpp code

CairoPDF("./hamiltonianmontecarlo.pdf", width = 14, height = 7)
par(mfrow = 1:2)

num.samples <- 50000
num.steps <- 100

## 1D gauss distribution
raw.sample <- sampleHMC(num.samples, num.steps, 1)
z <- sapply(raw.sample, function(x) x$z)
truehist(z[sapply(raw.sample, function(x) x$updFlag)], xlim = c(-5, 5), ylim = c(0, 0.5),
         panel.first = grid(), tcl = 0.25, las = 1, xlab = "x", col = "#b0c4de",
         main = "1D Gauss Distribution", bty = "o")
curve(dnorm, col = 2, lwd = 2, add = TRUE)

## 2D gauss distribution
raw.sample <- sampleHMC(num.samples, num.steps, 2)
z <- sapply(raw.sample, function(x) x$z)
updFlag <- sapply(raw.sample, function(x) x$updFlag)[1, ]
plot(x = z[1, updFlag], y = z[2, updFlag], col = densCols(cbind(z[1, updFlag], z[2, updFlag])), xlab = "x1", ylab = "x2",
     main = "2D Gauss Distribution", panel.first = grid(), tcl = 0.25, las = 1)
p.func <- function(z, mean = rep(0, 2)) dmvnorm(z, mean = mean, sigma = diag(2))
x <- y <- seq(-3, 3, length.out = 500)
contour(x = x, y = y, z = outer(x, y, function(x, y) p.func(cbind(x, y))), lwd = 3, col = rainbow(7), add = TRUE)

dev.off()
library(Cairo)
library(randtoolbox)

plot.func <- function(dat.random, main, xlim = c(0, 1), ylim = c(0, 1)) {
  plot(dat.random, main = main, las = 1, panel.first = grid(), tcl = 0.25, cex = 2,
       xlab = "x1", ylab = "x2", col = densCols(dat.random),
       xlim = xlim, ylim = ylim)
}

## uniform random number
n <- 200
rand.pseudo <- matrix(cbind(runif(n), runif(n)), ncol = 2)
rand.halton <- halton(n, dim = 2, init = TRUE, normal = FALSE, usetime = TRUE)
rand.sobol <- sobol(n, dim = 2, init = TRUE, scrambling = 0, seed = 4711, normal = FALSE)
rand.torus <- torus(n, dim = 2, c(5, 7), init = TRUE, mixed = FALSE, usetime = FALSE, normal = FALSE)

CairoPDF("./uniformrandom.pdf", width = 10, height = 10)
par(mfrow = c(2, 2))
plot.func(rand.pseudo, "pseudo random")
plot.func(rand.halton, "halton")
plot.func(rand.sobol, "sobol")
plot.func(rand.torus, "torus")
dev.off()

## normal random number
n <- 1000
rand.pseudo.normal <- matrix(cbind(rnorm(n), rnorm(n)), ncol = 2)
rand.halton.normal <- halton(n, dim = 2, init = TRUE, normal = TRUE, usetime = TRUE)
rand.sobol.normal <- sobol(n, dim = 2, init = TRUE, scrambling = 0, seed = 4711, normal = TRUE)
rand.torus.normal <- torus(n, dim = 2, c(5,7), init = TRUE, mixed = FALSE, usetime = FALSE, normal = TRUE)

xlim <- ylim <- c(-4, 4)
CairoPDF("./normalrandom.pdf", width = 10, height = 10)
par(mfrow = c(2, 2))
plot.func(rand.pseudo.normal, "pseudo random normal", xlim, ylim)
plot.func(rand.halton.normal, "halton normal", xlim, ylim)
plot.func(rand.sobol.normal, "sobol normal", xlim, ylim)
plot.func(rand.torus.normal, "torus normal", xlim, ylim)
dev.off()
library(Cairo)
library(mvtnorm)

sim.size <- 10000
getRand <- function(n = 1, mean = c(0, 0)) rmvnorm(n, mean = mean, sigma = diag(1, 2) * 0.2)
p.func <- function(z, mean = rep(1.5, 2)) dmvnorm(z, mean = mean, sigma = matrix(c(1, 0.8, 0.8, 1) * 0.2, 2))
z.init <- getRand()
state <- vector("list", sim.size)
rand.unif <- runif(sim.size)
state[[1]] <- list(z = z.init, p = p.func(z.init), updFlag = F)
for (i in 2:sim.size) {
  z.new <- getRand(mean = state[[i - 1]]$z)
  updFlag <- min(1, p.func(z.new) / state[[i - 1]]$p) >= rand.unif[i]
  state[[i]] <- list(z = z.new * updFlag + state[[i - 1]]$z * !updFlag, 
                     p = ifelse(updFlag, p.func(z.new), state[[i - 1]]$p), updFlag = updFlag)
}

x <- y <- seq(-3, 3, length.out = 500)
z <- sapply(state[sapply(state, function(x) x$updFlag)], function(par) par$z)  # extract only accepted z

CairoPDF("./metropolishastings.pdf")
plot(x = z[1, ], y = z[2, ], lwd = 2, xlim = c(0, 3), ylim = c(0, 3), xlab = "", ylab = "",
     main = sprintf("%d accept ( in %d sample )", sum(sapply(state, function(par) par$updFlag)), sim.size),
     las = 1, panel.first = grid(), tcl = 0.25, cex = 2)
contour(x = x, y = y, z = outer(x, y, function(x, y) p.func(cbind(x, y))), lwd = 2, col = rainbow(10), add = T)
dev.off()
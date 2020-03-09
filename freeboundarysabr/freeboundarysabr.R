library(Cairo)
library(Rcpp)

sourceCpp("./freeboundarysabr.cpp")  # compile Rcpp code

forward <- 50/100/100
beta <- 0.25
alpha <- 0.6*forward^(1-beta)
nu <- 0.3
rho <- -0.3
T <- 3
nd <- 3
N <- 100
timesteps <- 365*T
strikes <- seq(-0.1, 0.1, length.out = 80)

output <- makeTransformedSABRDensityLawsonSwayne(alpha, beta, nu, rho, forward, T, N, timesteps, nd)
premium <- sapply(strikes,
                  function(x)
                    priceCallTransformedSABRDensity(x, alpha, beta, nu, rho, forward, T, P = output$P, PL = output$PL, PR = output$PR,
                                                    zmin = output$zmin, zmax = output$zmax, h = output$h))
Fm <- makeForwardR(alpha, beta, nu, rho, forward, output$zm)
Fmin <- makeForwardR(alpha, beta, nu, rho, forward, output$zmin)
Fmax <- makeForwardR(alpha, beta, nu, rho, forward, output$zmax)

CairoPDF("./freeboundarysabr.pdf", width = 14, height = 7)
par(mfrow = 1:2)
plot(x = Fm, y = output$density, type = "o", xlim = c(Fmin, Fmax), xlab = "strike", ylab = "",
     panel.first = grid(), tcl = 0.25, las = 1, main = "FB-SABR density")
abline(v = forward, col = 2)
legend("topright", "ATM", col = 2, lty = 1)

plot(x = strikes, y = premium, type = "o", panel.first = grid(), tcl = 0.25, las = 1,
     xlab = "strike", ylab = "", main = "FB-SABR Call Premium")
abline(v = forward, col = 2)
legend("topright", "ATM", col = 2, lty = 1)
dev.off()
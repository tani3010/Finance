library(Cairo)

Y <- function(alpha, nu, rho, zm) alpha/nu*(sinh(nu*zm)+rho*(cosh(nu*zm)-1))
F <- function(forward, beta, ym) (forward^(1-beta)+(1-beta)*ym)^(1/(1-beta))
C <- function(alpha, beta, rho, nu, ym, Fm) sqrt(alpha^2+2*rho*alpha*nu*ym+nu^2*ym^2)*Fm^beta
G <- function(forward, beta, Fm, j0) {
  G <- (Fm^beta-forward^beta)/(Fm-forward)
  G[j0+1] <- beta/forward^(1-beta)
  return(G)
}

computeBoundaries <- function(alpha, beta, nu, rho, forward, T, nd) {
  zmin <- -nd*sqrt(T)
  zmax <- -zmin
  if (beta < 1) {
    ybar <- -forward^(1-beta)/(1-beta)
    zbar <- -1/nu*log((sqrt(1-rho^2+(rho+nu*ybar/alpha)^2)-rho-nu*ybar/alpha)/(1-rho))
    if (zbar > zmin) zmin <- zbar
  }
  list(zmin = zmin, zmax = zmax)
}

makeForward <- function(alpha, beta, nu, rho, forward, z) F(forward, beta, Y(alpha, nu, rho, z))
yOfStrike <- function(strike, forward, beta) (strike^(1-beta)-forward^(1-beta))/(1-beta)

solveStep <- function(Fm, Cm, Em, dt, h, P, PL, PR) {
  frac <- dt/(2*h)
  M <- length(P)
  A <- numeric(M-1)
  B <- numeric(M)
  C <- numeric(M-1)
  B[2:(M-1)] <- 1+frac*(Cm[2:(M-1)]*Em[2:(M-1)]*(1/(Fm[3:M]-Fm[2:(M-1)])+1/(Fm[2:(M-1)]-Fm[1:(M-2)])))
  C[2:(M-1)] <- -frac*Cm[3:M]*Em[3:M]/(Fm[3:M]-Fm[2:(M-1)])
  A[1:(M-2)] <- -frac*Cm[1:(M-2)]*Em[1:(M-2)]/(Fm[2:(M-1)]-Fm[1:(M-2)])
  B[1] <- Cm[1]/(Fm[2]-Fm[1])*Em[1]
  C[1] <- Cm[2]/(Fm[2]-Fm[1])*Em[2]
  B[M] <- Cm[M]/(Fm[M]-Fm[M-1])*Em[M]
  A[M-1] <- Cm[M-1]/(Fm[M]-Fm[M-1])*Em[M-1]
  tri <- diag(B)+rbind(rep(0, M), diag(A, M-1, M))+cbind(rep(0, M), diag(C, M, M-1))
  P[1] <- P[M] <- 0
  P <- solve(tri, P)
  PL <- PL+dt*Cm[2]/(Fm[2]-Fm[1])*Em[2]*P[2]
  PR <- PR+dt*Cm[M-1]/(Fm[M]-Fm[M-1])*Em[M-1]*P[M-1]
  list(P = P, PL = PL, PR = PR)
}

priceCallTransformedSABRDensity <- function(strike, alpha, beta, nu, rho, forward, T, P, PL, PR, zmin, zmax, h) {
  ystrike <- yOfStrike(strike, forward, beta)
  zstrike <- -1/nu*log((sqrt(1-rho^2+(rho+nu*ystrike/alpha)^2)-rho-nu*ystrike/alpha)/(1-rho))
  if (zstrike <= zmin)
    p <- forward-strike
  else {
    if (zstrike >= zmax)
      p <- 0
    else {
      Fmax <- makeForward(alpha, beta, nu, rho, forward, zmax)
      p <- (Fmax-strike)*PR
      k0 <- ceiling((zstrike-zmin)/h)
      ztilde <- zmin+k0*h
      ftilde <- makeForward(alpha, beta, nu, rho, forward, ztilde)
      term <- ftilde-strike
      if(term > 1e-5) {
        zm <- zmin+(k0-0.5)*h
        Fm <- makeForward(alpha, beta, nu, rho, forward, zm)
        dFdz <- (ftilde-Fm)/(ztilde-zm)
        p <- p+0.5*term*term*P[k0+1]/dFdz
      }
      k <- (k0+1):(length(P)-2)
      zm <- zmin+(k-0.5)*h
      Fm <- makeForward(alpha, beta, nu, rho, forward, zm)
      p <- p+sum((Fm-strike)*h*P[k+1])
    }
  }
  return(p)
}

makeTransformedSABRDensityLawsonSwayne <- function(alpha, beta, nu, rho, forward, T, N, timesteps, nd) {
  tmp <- computeBoundaries(alpha, beta, nu, rho, forward, T, nd)
  zmin <- tmp$zmin
  zmax <- tmp$zmax
  J <- N-2
  h0 <- (zmax-zmin)/J
  j0 <- as.integer((0-zmin)/h0)
  h <- (0-zmin)/(j0-0.5)
  z <- (0:(J+1))*h+zmin
  zmax <- z[J+1]
  zm <- z-0.5*h
  ym <- Y(alpha, nu, rho, zm)
  ymax <- Y(alpha, nu, rho, zmax)
  ymin <- Y(alpha, nu, rho, zmin)
  Fm <- F(forward, beta, ym)
  Fmax <- F(forward, beta, ymax)
  Fmin <- F(forward, beta, ymin)
  Fm[1] <- 2*Fmin-Fm[2]
  Fm[J+2] <- 2*Fmax-Fm[J+1]
  Cm <- C(alpha, beta, rho, nu, ym, Fm)
  Cm[1] <- Cm[2]
  Cm[J+2] <- Cm[J+1]
  Gammam <- G(forward, beta, Fm, j0)
  dt <- T/timesteps
  b <- 1-0.5*sqrt(2)
  dt1 <- dt*b
  dt2 <- dt*(1-2*b)
  Em <- rep(1, J+2)
  Emdt1 <- exp(rho*nu*alpha*Gammam*dt1)
  Emdt1[1] <- Emdt1[2]
  Emdt1[J+2] <- Emdt1[J+1]
  Emdt2 <- exp(rho*nu*alpha*Gammam*dt2)
  Emdt2[1] <- Emdt2[2]
  Emdt2[J+2] <- Emdt2[J+1]
  PL <- PR <- 0
  P <- rep(0, J+2)
  P[j0+1] <- 1/h
  for (t in 1:timesteps) {
    Em <- Em*Emdt1
    tmp <- solveStep(Fm, Cm, Em, dt1, h, P, PL, PR)
    P1 <- tmp$P
    PL1 <- tmp$PL
    PR1 <- tmp$PR
    Em <- Em*Emdt1
    tmp <- solveStep(Fm, Cm, Em, dt1, h, P1, PL1, PR1)
    P2 <- tmp$P
    PL2 <- tmp$PL
    PR2 <- tmp$PR
    P <- (sqrt(2)+1)*P2-sqrt(2)*P1
    PL <- (sqrt(2)+1)*PL2-sqrt(2)*PL1
    PR <- (sqrt(2)+1)*PR2-sqrt(2)*PR1
    Em <- Em*Emdt2
  }
  list(P = P, PL = PL, PR = PR, zm = zm, zmin = zmin, zmax = zmax, Cm = Cm, h = h, density = P/Cm)
}




alpha <- 0.026; beta <- 0.5; nu <- 0.4; rho <- -0.1; forward <- 0.0488
T <- 1
nd <- 4
N <- 100
timesteps <- 100*T
strikes <- seq(1e-7, 0.1, length.out = 40)
output <- makeTransformedSABRDensityLawsonSwayne(alpha, beta, nu, rho, forward, T, N, timesteps, nd)
premium <- sapply(strikes,
  function(x)
    priceCallTransformedSABRDensity(x, alpha, beta, nu, rho, forward, T, P = output$P, PL = output$PL, PR = output$PR,
                                    zmin = output$zmin, zmax = output$zmax, h = output$h))
Fm <- makeForward(alpha, beta, nu, rho, forward, output$zm)
Fmin <- makeForward(alpha, beta, nu, rho, forward, output$zmin)
Fmax <- makeForward(alpha, beta, nu, rho, forward, output$zmax)
output$P[Fm < forward][output$P[Fm < forward] < output$PL] <- output$PL
output$P[Fm > forward][output$P[Fm > forward] < output$PR] <- output$PR

CairoPDF("./arbitragefreesabr.pdf", width = 14, height = 7)
par(mfrow = 1:2)
plot(x = Fm, y = output$density, type = "o", xlim = c(Fmin, Fmax), xlab = "strike", ylab = "",
     panel.first = grid(), tcl = 0.25, las = 1, main = "Arb-Free SABR density")
abline(v = forward, col = 2)
legend("topright", "ATM", col = 2, lty = 1)

plot(x = strikes, y = premium, type = "o", xlab = "strike", ylab = "",
     panel.first = grid(), tcl = 0.25, las = 1, main = "Arb-Free SABR Call Premium")
abline(v = forward, col = 2)
legend("topright", "ATM", col = 2, lty = 1)
dev.off()
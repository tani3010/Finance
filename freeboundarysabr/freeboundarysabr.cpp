#include <RcppArmadillo.h>
// [[Rcpp::depends(RcppArmadillo)]]
using namespace Rcpp;

double sign(const double x) {
  return x >= 0.0 ? 1.0 : -1.0;
}

NumericVector sign(const NumericVector& x) {
  return ifelse(x >= 0.0, rep(1.0, x.size()), rep(-1.0, x.size()));
}

double abs(double x) {
  return fabs(x);
}

NumericVector abs(const NumericVector& x) {
  return Rcpp::abs(x);
}

template <typename T>
T Y(const double alpha, const double nu, const double rho, const T& zm) {
  return alpha/nu*(sinh(nu*zm)+rho*(cosh(nu*zm)-1));
}

template <typename T>
T F(const double forward, const double beta, const T& ym) {
  const T u = sign(forward)*pow(abs(forward), 1-beta)+(1-beta)*ym;
  return sign(u)*pow(abs(u), 1/(1-beta));
}

NumericVector C(const double alpha, const double beta, const double rho, const double nu,
                const NumericVector& ym, const NumericVector& Fm) {
  return sqrt(alpha*alpha+2*rho*alpha*nu*ym+nu*nu*ym*ym)*pow(abs(Fm), beta);
}

NumericVector G(const double forward, const double beta, const NumericVector Fm, const int j0) {
  NumericVector G = (pow(abs(Fm), beta)-pow(abs(forward), beta))/(Fm-forward);
  G[j0] = sign(forward)*beta/pow(abs(forward), 1-beta);
  return G;
}

template <typename T>
T makeForward(const double alpha, const double beta , const double nu,
              const double rho, const double forward, const T& z) {
  return F(forward, beta, Y<T>(alpha, nu, rho, z));
}

// [[Rcpp::export]]
NumericVector makeForwardR(const double alpha, const double beta , const double nu,
                           const double rho, const double forward, const NumericVector& z) {
  return F(forward, beta, Y<NumericVector>(alpha, nu, rho, z));
}

List computeBoundaries(const double alpha, const double beta, const double nu, const double rho,
                       const double forward, const double T, const double nd) {
  return List::create(Named("zmin")=-nd*sqrt(T), Named("zmax")=nd*sqrt(T));
}

double yOfStrike(const double strike, const double forward, const double beta) {
  return (sign(strike)*pow(abs(strike), 1-beta)-sign(forward)*pow(abs(forward), 1-beta))/(1-beta);
}

List solveStep(NumericVector& Fm, NumericVector& Cm, NumericVector& Em, const double dt,
               const double h, const NumericVector& P, double PL, double PR) {
  const double frac = 0.5*dt/h;
  const int M = P.size();
  NumericVector A(M-1);
  NumericVector B(M);
  NumericVector C(M-1);
  double PL_, PR_;
  B[Range(1, M-2)] = 1+frac*(Cm[Range(1, M-2)]*Em[Range(1, M-2)]*(1/(Fm[Range(2, M-1)]-Fm[Range(1, M-2)])+1/(Fm[Range(1, M-2)]-Fm[Range(0, M-3)])));
  C[Range(1, M-2)] = -frac*Cm[Range(2, M-1)]*Em[Range(2, M-1)]/(Fm[Range(2, M-1)]-Fm[Range(1, M-2)]);
  A[Range(0, M-3)] = -frac*Cm[Range(0, M-3)]*Em[Range(0, M-3)]/(Fm[Range(1, M-2)]-Fm[Range(0, M-3)]);
  B[0] = Cm[0]/(Fm[1]-Fm[0])*Em[0];
  C[0] = Cm[1]/(Fm[1]-Fm[0])*Em[1];
  B[M-1] = Cm[M-1]/(Fm[M-1]-Fm[M-2])*Em[M-1];
  A[M-2] = Cm[M-2]/(Fm[M-1]-Fm[M-2])*Em[M-2];
  arma::vec P_ = as<arma::vec>(P);
  arma::mat tri(M, M, arma::fill::zeros);
  for (int i = 0; i < M; ++i) {
    tri(i, i) = B[i];
    if (i > 0) tri(i, i-1) = A[i-1]; 
    if (i+1 < M) tri(i, i+1) = C[i];
  }
  P_[0] = P_[M-1] = 0;
  P_ = arma::solve(tri, P_);
  PL_ = PL+dt*Cm[1]/(Fm[1]-Fm[0])*Em[1]*P_[1];
  PR_ = PR+dt*Cm[M-2]/(Fm[M-1]-Fm[M-2])*Em[M-2]*P_[M-2];
  return List::create(Named("P")=NumericVector(P_.begin(), P_.end()), Named("PL")=PL_, Named("PR")=PR_);
}

// [[Rcpp::export]]
List makeTransformedSABRDensityLawsonSwayne(const double alpha, const double beta, const double nu, const double rho,
                                            const double forward, const double T, const size_t N, const size_t timesteps, const size_t nd=4) {
  List tmp = computeBoundaries(alpha, beta, nu, rho, forward, T, nd);
  double zmin = tmp["zmin"];
  double zmax = tmp["zmax"];
  const double J = N-2;
  const double h0 = (zmax-zmin)/J;
  const int j0 = (0-zmin)/h0;
  const double h = (0-zmin)/(j0-0.5);
  NumericVector z(J+2);
  for (int i = 0; i < z.size(); ++i) z[i] = i*h+zmin;
  zmax = z[J];
  NumericVector zm = z-0.5*h;
  NumericVector ym = Y<NumericVector>(alpha, nu, rho, zm);
  double ymax =  Y<double>(alpha, nu, rho, zmax);
  double ymin = Y<double>(alpha, nu, rho, zmin);
  NumericVector Fm = F<NumericVector>(forward, beta, ym);
  double Fmax = F<double>(forward, beta, ymax);
  double Fmin = F<double>(forward, beta, ymin);
  Fm[0] = 2*Fmin-Fm[1];
  Fm[J+1] = 2*Fmax-Fm[J];
  NumericVector Cm = C(alpha, beta, rho, nu, ym, Fm);
  Cm[0] = Cm[1];
  Cm[J+1] = Cm[J];
  NumericVector Gammam = G(forward, beta, Fm, j0);
  double dt = T/timesteps;
  double b = 1-0.5*sqrt(2);
  double dt1 = dt*b;
  double dt2 = dt*(1-2*b);
  NumericVector Em = rep(1.0, J+2);
  NumericVector Emdt1 = exp(rho*nu*alpha*Gammam*dt1);
  Emdt1[0] = Emdt1[1];
  Emdt1[J+1] = Emdt1[J];
  NumericVector Emdt2 = exp(rho*nu*alpha*Gammam*dt2);
  Emdt2[0] = Emdt2[1];
  Emdt2[J+1] = Emdt2[J];
  double PL = 0;
  double PR = 0;
  NumericVector P = rep(0.0, J+2);
  P[j0] = 1/h;
  for (size_t t = 0; t < timesteps; ++t) {
    Em = Em*Emdt1;
    tmp = solveStep(Fm, Cm, Em, dt1, h, P, PL, PR);
    NumericVector P1 = tmp["P"];
    double PL1 = tmp["PL"];
    double PR1 = tmp["PR"];
    Em = Em*Emdt1;
    tmp = solveStep(Fm, Cm, Em, dt1, h, P1, PL1, PR1);
    NumericVector P2 = tmp["P"];
    double PL2 = tmp["PL"];
    double PR2 = tmp["PR"];
    P = (sqrt(2)+1)*P2-sqrt(2)*P1;
    PL = (sqrt(2)+1)*PL2-sqrt(2)*PL1;
    PR = (sqrt(2)+1)*PR2-sqrt(2)*PR1;
    Em = Em*Emdt2;
  }
  return List::create(Named("P")=P, Named("PL")=PL, Named("PR")=PR, Named("zm")=zm,
                      Named("zmin")=zmin, Named("zmax")=zmax, Named("Cm")=Cm, Named("h")=h,
                      Named("density")=P/Cm);
}

// [[Rcpp::export]]
double priceCallTransformedSABRDensity(const double strike, const double alpha, const double beta,
                                       const double nu, const double rho, const double forward,
                                       const double T, NumericVector& P,
                                       const double PL, const double PR, const double zmin,
                                       const double zmax, const double h) {
  const double ystrike = yOfStrike(strike, forward, beta);
  const double zstrike = -1/nu*log((sqrt(1-rho*rho+pow(rho+nu*ystrike/alpha, 2))-rho-nu*ystrike/alpha)/(1-rho));
  double p, Fmax, ztilde, ftilde, term, zm, Fm, dFdz;
  int k0;
  if (zstrike <= zmin)
    p = forward-strike;
  else {
    if (zstrike >= zmax)
      p = 0;
    else {
      Fmax = makeForward<double>(alpha, beta, nu, rho, forward, zmax);
      p = (Fmax-strike)*PR;
      k0 = ceil((zstrike-zmin)/h);
      ztilde = zmin+k0*h;
      ftilde = makeForward<double>(alpha, beta, nu, rho, forward, ztilde);
      term = ftilde-strike;
      if (term > 1e-5) {
        zm = zmin+(k0-0.5)*h;
        Fm = makeForward<double>(alpha, beta, nu, rho, forward, zm);
        dFdz = (ftilde-Fm)/(ztilde-zm);
        p = p+0.5*term*term*P[k0]/dFdz;
      }
      NumericVector k(P.size()-2 > k0+1 ?  P.size()-k0-2 : k0-P.size()+4);
      for(int i=0; i < k.size(); ++i) k[i] = sign(P.size()-2-(k0+1))*i+k0+1;
      NumericVector FmV = makeForward<NumericVector>(alpha, beta, nu, rho, forward, zmin+(k-0.5)*h);
      int lower = P.size()-2 > k0+1 ? k0+1 : P.size()-2;
      int upper = P.size()-2 > k0+1 ? P.size()-2 : k0+1;
      p = p+h*sum((FmV-strike)*P[Range(lower, upper)]);
    }
  }
  return p;
}
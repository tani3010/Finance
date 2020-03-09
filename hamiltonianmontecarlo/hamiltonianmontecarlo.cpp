#include <Rcpp.h>
using namespace Rcpp;

double E(NumericVector x) {
  return 0.5 * sum(pow(x, 2));
}

NumericVector derivE(NumericVector x) {
  return x;
}

// [[Rcpp::export]]
List sampleHMC(const unsigned long simSize,
               const unsigned long leapfrogSize,
               const unsigned int stateDim) {
  RNGScope scope;
  LogicalVector updFlag = rep(false, stateDim);
  NumericVector u = runif(simSize, 0, 1);
  NumericVector z = runif(stateDim, 1, 1);
  NumericVector r = rnorm(stateDim, 0, 1);
  NumericVector r_init = clone(r);
  double H;
  List stepInfoList(simSize);
  stepInfoList[0] = List::create(Named("z") = clone(z),
                                 Named("updFlag") = clone(updFlag));
  NumericVector leapfrogSimSize = round(runif(simSize, leapfrogSize, leapfrogSize * 3.0), 0);
  NumericVector epsilon = ifelse(runif(simSize, 0, 1) > 0.5, 1.0, -1.0) * rnorm(simSize, 0.9, 1.1) * 0.01;
  for (unsigned long i = 1; i < simSize; ++i) {
    z = clone(as<NumericVector>(as<List>(stepInfoList[i - 1])["z"]));
    r_init = ifelse(as<LogicalVector>(as<List>(stepInfoList[i - 1])["updFlag"]), rnorm(stateDim, 0, 1), r_init);
    H = E(z) + 0.5 * sum(pow(r_init, 2));
    r = r_init - 0.5 * epsilon[i - 1] * derivE(z);
    for (unsigned long j = 0; j < leapfrogSimSize[i - 1]; ++j) {
      z = z + epsilon[i - 1] * r;
      r = r - epsilon[i - 1] * derivE(z);
    }
    z = z + 0.5 * epsilon[i - 1] * r;
    updFlag = rep(std::min<double>(1.0, exp(H - (E(z) + 0.5 * sum(pow(r, 2))))) > u[i - 1], stateDim);
    stepInfoList[i] = List::create(Named("z") = ifelse(updFlag, z, as<NumericVector>(as<List>(stepInfoList[i - 1])["z"])),
                                   Named("updFlag") = clone(updFlag));    
  }
  return stepInfoList;
}
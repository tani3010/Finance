#include <Rcpp.h>
#include <RQuantLib.h>

using namespace Rcpp;
using namespace QuantLib;
// [[Rcpp::depends(RQuantLib)]]
// [[Rcpp::plugins(openmp)]]

// [[Rcpp::export]]
NumericVector getSabrCallPrice(
  const NumericVector& strike, const double expiryTime, const double forward,
  const double alpha, const double beta, const double nu, const double rho,
  const double shift = 0.0, const double discount = 1.0) {
  boost::shared_ptr<SabrInterpolatedSmileSection> siss(new SabrInterpolatedSmileSection(
    QuantLib::Date::todaysDate() + expiryTime * 365, forward, as<std::vector<Rate> >(strike), false,
    forward, as<std::vector<Volatility> >(strike), alpha, beta, nu, rho, true, true, true, true, shift));
  NumericVector result(strike.size());
  for (int i = 0; i < strike.size(); ++i) {
    result[i] = siss->optionPrice(strike[i], Option::Call, discount);
  }
  return result;
}

// [[Rcpp::export]]
NumericVector getSabrImpliedShiftedBlackVolatility(
  const NumericVector& strike, const double expiryTime, const double forward,
  const double alpha, const double beta, const double nu, const double rho,
  const double shift = 0.0) {
  boost::shared_ptr<SabrInterpolatedSmileSection> siss(new SabrInterpolatedSmileSection(
    QuantLib::Date::todaysDate() + expiryTime * 365, forward, as<std::vector<Rate> >(strike), false,
    forward, as<std::vector<Volatility> >(strike), alpha, beta, nu, rho, true, true, true, true, shift));
  NumericVector result(strike.size());
  for (int i = 0; i < strike.size(); ++i) {
    result[i] = siss->volatilityImpl(strike[i]);
  }
  return result;
}

// [[Rcpp::export]]
NumericVector getSabrImpliedDensity(
  const NumericVector& strike, const double expiryTime, const double forward,
  const double alpha, const double beta, const double nu, const double rho,
  const double shift = 0.0) {
  boost::shared_ptr<SabrInterpolatedSmileSection> siss(new SabrInterpolatedSmileSection(
    QuantLib::Date::todaysDate() + expiryTime * 365, forward, as<std::vector<Rate> >(strike), false,
    forward, as<std::vector<Volatility> >(strike), alpha, beta, nu, rho, true, true, true, true, shift));
  NumericVector result(strike.size());
  for (int i = 0; i < strike.size(); ++i) {
    result[i] = siss->density(strike[i]);
  }
  return result;
}

// [[Rcpp::export]]
NumericVector getNoArbSabrImpliedDensity(
  const NumericVector& strike, const double expiryTime, const double forward,
  const double alpha, const double beta, const double nu, const double rho) {
  boost::shared_ptr<NoArbSabrModel> nasm(new NoArbSabrModel(expiryTime, forward, alpha, beta, nu, rho));
  NumericVector result(strike.size());
  for (int i = 0; i < strike.size(); ++i) result[i] = nasm->density(strike[i]);
  return result;
}

// [[Rcpp::export]]
NumericVector getNoArbSabrImpliedBlackVolatility(
  const NumericVector& strike, const double expiryTime, const double forward,
  const double alpha, const double beta, const double nu, const double rho) {
  boost::shared_ptr<NoArbSabrInterpolatedSmileSection> nasiss(new NoArbSabrInterpolatedSmileSection(
    QuantLib::Date::todaysDate() + expiryTime * 365, forward, as<std::vector<Rate> >(strike), false,
    forward, as<std::vector<Volatility> >(strike), alpha, beta, nu, rho, true, true, true, true));
  NumericVector result(strike.size());
  for (int i = 0; i < strike.size(); ++i) result[i] = nasiss->volatilityImpl(strike[i]);
  return result;
}

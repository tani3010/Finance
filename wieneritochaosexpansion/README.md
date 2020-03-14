* Implementing Wiener-Ito Chaos Expansion using python
There are mainly two types of asymptotic expansion methods for SDE solutions in finance.
One is small diffusion theory, and the ohter is Wiener-Ito Chaos(WIC) expansion.
Asymptotic expansion using small diffusion theory is implemented in yuima package in R.
But there is no asymptotic implementation using WIC, so here is what I implemented using python.

This implementation is applicable to the following two-dimensional SDE, but can be calculated using more general settings.

\frac{\mathrm{d}S_t}{S_t} = r(t)\mathrm{d}t + \sigma(S_t, v_t)\mathrm{d}W_t^S \\
\mathrm{d}v_t = (\theta(t) - \kappa(t)v_t)\mathrm{d}t + \gamma(t)\mathrm{d}W_t^v \\
\mathrm{d}<S, v>_t = \rho\mathrm{d}t \\


* Bibliography
[1]Funahashi, H. (2014). A chaos expansion approach under hybrid volatility models. Quantitative Finance, 14(11), 1923-1936.

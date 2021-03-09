import warnings

import numpy as np
from scipy import stats

DISTRIBUTIONS = [stats.alpha, stats.anglit, stats.arcsine, stats.argus, stats.beta, stats.betaprime, stats.bradford, stats.burr, stats.burr12, stats.cauchy, stats.chi, stats.chi2, stats.cosine, stats.crystalball, stats.dgamma, stats.dweibull, stats.erlang, stats.expon, stats.exponnorm, stats.exponweib, stats.exponpow, stats.f, stats.fatiguelife, stats.fisk, stats.foldcauchy, stats.foldnorm, stats.frechet_r, stats.frechet_l, stats.genlogistic, stats.gennorm, stats.genpareto, stats.genexpon, stats.genextreme, stats.gausshyper, stats.gamma, stats.gengamma, stats.genhalflogistic, stats.gilbrat, stats.gompertz, stats.gumbel_r, stats.gumbel_l, stats.halfcauchy, stats.halflogistic, stats.halfnorm, stats.halfgennorm, stats.hypsecant, stats.invgamma, stats.invgauss,
                 stats.invweibull, stats.johnsonsb, stats.johnsonsu, stats.kappa4, stats.kappa3, stats.ksone, stats.kstwobign, stats.laplace, stats.levy, stats.levy_l, stats.levy_stable, stats.logistic, stats.loggamma, stats.loglaplace, stats.lognorm, stats.lomax, stats.maxwell, stats.mielke, stats.moyal, stats.nakagami, stats.ncx2, stats.ncf, stats.nct, stats.norm, stats.norminvgauss, stats.pareto, stats.pearson3, stats.powerlaw, stats.powerlognorm, stats.powernorm, stats.rdist, stats.reciprocal, stats.rayleigh, stats.rice, stats.recipinvgauss, stats.semicircular, stats.skewnorm, stats.t, stats.trapz, stats.triang, stats.truncexpon, stats.truncnorm, stats.tukeylambda, stats.uniform, stats.vonmises, stats.vonmises_line, stats.wald, stats.weibull_min, stats.weibull_max, stats.wrapcauchy]


def fit_and_test_all(data, pbfun=None):
    fits = []
    for dist in DISTRIBUTIONS:
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore')
                # fit dist to data
                params = dist.fit(data)
                # perform Kolmogorov-Smirnov test
                d, _ = stats.kstest(data, dist.cdf, args=params)
                fits.append((dist, params, d))
        except RuntimeError:
            pass
        if pbfun is not None:
            pbfun(1)
    fits.sort(key=lambda x: x[2])
    return fits

annual_max = data.groupby(lambda i: data.iloc[i].time.split('-')[0]).max()
hmax = np.sort(annual_max.swh)
"""fitting and plotting of those fits"""

import numpy as np
from dataclasses import dataclass
from delta_method import delta_method

import scipy

from .plot import plt, mplhep

    
def fit(f, x, y, w2, use_empty_bins = True, condense = False, **fit_kwargs):
    if condense:
        # merge bins together that have the same value
        _, indices, counts = np.unique(
            np.r_[[0], ~np.isclose(y[:-1], y[1:])].cumsum(),
            return_index = True,
            return_counts = True
        )
        w2 = np.array([sl.sum() for sl in np.split(w2, indices[1:])])
        y = np.array([sl.sum() for sl in np.split(y, indices[1:])])
        x = np.array([sl.mean() for sl in np.split(x, indices[1:])])
    # use the poisson interval calculation to estimate error bars
    low, up = mplhep.error_estimation.poisson_interval(y, w2)
    # assume symmetric error bars and just have the error be the difference
    # between the upper edge of the error and the value if the lower edge is nan
    yerr = (up-low)/2
    yerr[np.isnan(low)] = (up[np.isnan(low)]-y[np.isnan(low)])
    if not use_empty_bins:
        keep = (y > 0.0)
        x = x[keep]
        y = y[keep]
        yerr = yerr[keep]
    return scipy.optimize.curve_fit(
        f, x, y,
        sigma = yerr,
        absolute_sigma=True,
        **fit_kwargs
    )


def deduce_label(f, opt, cov, **plt_kwargs):
    params = ' '.join([f'{n} = {p:.3g}$\\pm${e:.3g}' for n,p,e in zip('ABCD',opt,np.sqrt(np.diag(cov)))])
    label = ''
    if 'label' in plt_kwargs:
        label = plt_kwargs['label'] + ' '
    if getattr(f, '__label__', None) is not None:
        label += f'{f.__label__}\n{params}'
    elif getattr(f, '__name__', None) is not None:
        label += f'{f.__name__}\n{params}'
    else:
        label = params
    return label


@dataclass
class expo:
    max_e: float = 1.
    
    def __call__(self, e, amplitude, rate):
        return amplitude*np.exp(rate*(1-e/self.max_e))


    @property
    def __label__(self):
        if self.max_e != 1.:
            return r"$Ae^{B(1-E_\text{ECal}/"+str(self.max_e)+")}$"
        return r"$Ae^{B(1-E_\text{ECal})}$"

    def delta_method(self, plt_range, alpha = 0.05):
        return delta_method(self.cov, self.opt, plt_range, self, self.x, self.y, alpha)

    
    def fit(self, x, y, w2, **kwargs):
        opt, cov = fit(self, x, y, w2, **kwargs)
        self.opt = opt
        self.cov = cov
        self.x = x
        self.y = y
        self.w2 = w2
        return self

    
    def fit_and_plt(self, x, y, w2, fit_kwargs = {}, plt_range = None, **plt_kwargs):
        self.fit(x, y, w2, **fit_kwargs)
        if plt_range is None:
            plt_range = np.linspace(np.min(x),np.max(x),100)
        plt_kwargs['label'] = deduce_label(self, self.opt, self.cov, **plt_kwargs)
        art, = plt.plot(plt_range, self(plt_range, *self.opt), **plt_kwargs)
        d = self.delta_method(plt_range)
        plt.gca().fill_between(
            x=plt_range, y1 = d['lwr_conf'], y2 = d['upr_conf'],
            color = art.get_color(),
            alpha = 0.2
        )
        return self

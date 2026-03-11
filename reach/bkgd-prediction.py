from harvester.plot import plt, mplhep, show
from harvester.io import load_hists, load_max_signal_allowed
from harvester.fit import expo, deduce_label
import hist
import numpy as np
import json

h = load_hists()

bkgd_yield = {}
sig_eff = {}

for beam, cut, max_efrac in [
    (4, 1.1/4, 1.5/4),
    (8, 2.76/8, 3.16/8)
]:
    bkgd_yield[beam] = {}
    eef_h = h[beam]['histograms']['EcalEnergyFrac']
    bkg_h = sum(
        eef_h[bkg,'ecal_rms',:]*h[beam][bkg]['scale_1e13']
        for bkg in ['dimuon','enriched-nuclear']
    )[:hist.loc(max_efrac)]
    
    efrac = bkg_h.axes[0].centers
    defrac = bkg_h.axes[0].widths
    
    cumulative_bkg = bkg_h.view().cumsum()
    mplhep.histplot(
        cumulative_bkg['value'],
        bins = bkg_h.axes[0].edges,
        w2 = cumulative_bkg['variance'],
        w2method = mplhep.error_estimation.poisson_interval,
        label = 'Cumulative Background MC',
        color = 'dimgrey'
    )

    the_fit = expo().fit_and_plt(
        efrac,
        cumulative_bkg['value'],
        cumulative_bkg['variance'],
        fit_kwargs = dict(use_empty_bins = False)
    )
    
    plt.ylabel(r"$N_\text{bkgd}$ below $E_\text{frac}$")
    plt.xlabel(r"$E_\text{frac} = E_\text{ECal} / E_\text{Beam}$")
    plt.yscale('log')
    # plt.ylim(ymin=1e-2) #, ymax=1e3)
    plt.xlim(0,max_efrac)
    plt.legend(loc='upper left')
    show(
        beam,
        filename=f'plots/rms-on-both/{beam}gev-cumulative-bkgd-fit.pdf',
        stage='Simulation Internal',
        display=False
    )
    
    ana_bins = np.array([0.0, 0.1, 0.2, cut])
    
    i_bin = np.digitize(ana_bins, bins=bkg_h.axes[0].edges, right=True)-1
    i_bin[0] = 0
    integrated_bkg = cumulative_bkg[i_bin][1:]-cumulative_bkg[i_bin][:-1]
    
    mplhep.histplot(
        integrated_bkg['value'],
        bins=ana_bins,
        w2=integrated_bkg['variance'],
        w2method=mplhep.error_estimation.poisson_interval,
        label='Bkgd MC',
        color='dimgrey'
    )

    fit_at_edges = the_fit(ana_bins, *the_fit.opt)
    fit_val = fit_at_edges[1:]-fit_at_edges[:-1]
    dm = the_fit.delta_method(ana_bins)
    up = dm['upr_conf'][1:]-dm['upr_conf'][:-1]
    lo = dm['lwr_conf'][1:]-dm['lwr_conf'][:-1]
    bkgd_yield[beam]['sim'] = integrated_bkg.value.tolist()
    bkgd_yield[beam]['fit_val'] = fit_val.tolist()
    bkgd_yield[beam]['up'] = up.tolist()
    bkgd_yield[beam]['lo'] = lo.tolist()
    # print(up, fit_val, lo)
    mplhep.histplot(
        fit_val,
        bins=ana_bins,
        yerr = (up-lo)/2,
        histtype='errorbar',
        capsize=5,
        label = deduce_label(the_fit, the_fit.opt, the_fit.cov)
    )

    sig_eff[beam] = {}
    for proc in eef_h.axes[0]:
        if not proc.startswith('ap'):
            continue
        sig_frac = eef_h[proc,'ecal_rms',:].view().cumsum()
        _sig_eff = (sig_frac[i_bin][1:]-sig_frac[i_bin][:-1])/h[beam][proc]['weightsum']
        sig_eff[beam][proc] = _sig_eff.value.tolist()
    plt.legend(loc='upper left')
    plt.ylabel(r"$N_\text{bkgd}$ / bin")
    plt.xlabel(r"Analysis Bin $E_\text{frac} = E_\text{ECal} / E_\text{Beam}$")
    plt.yscale('log')
    # plt.ylim(ymin=1)
    plt.xlim(0,cut)
    show(beam, display=False, filename=f'plots/rms-on-both/{beam}gev-integrated-bkgd-fit.pdf')

with open('bkgd-prediction.json','w') as f:
    json.dump(bkgd_yield, f, indent=2)

with open('sig-eff.json', 'w') as f:
    json.dump(sig_eff, f, indent=2)
from harvester.plot import plt, mplhep, show
from harvester.fit import expo, deduce_label
import hist
import numpy as np
import json
import uproot

import argparse
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument('hist', type=Path)
args = parser.parse_args()

with uproot.open(args.hist) as f:
    bkg_h = f['ReducedEaT/ReducedEaT_funnel_final_total_ecal_rec_energy'].to_hist()

beam = 8
cut = 2760
max_e = 3160
output = args.hist.parent
bkgd_yield = {}

for option in ['entireback', 'funnel', 'prototype']:
    bkg_h = f[f'ReducedEaT/ReducedEaT_{option}_final_total_ecal_rec_energy'].to_hist()
    # need to scale histogram from weights to yield
    # this is the correct scale for the 8GeV, Enriched Nuclear sample from the EaT paper
    # the Di-Muon sample is assumed to be negligible
    bkg_h = bkg_h[:hist.loc(max_e):hist.rebin(5)]*200.0
    
    e = bkg_h.axes[0].centers
    de = bkg_h.axes[0].widths
    
    cumulative_bkg = bkg_h.view().cumsum()
    mplhep.histplot(
        cumulative_bkg['value'],
        bins = bkg_h.axes[0].edges,
        w2 = cumulative_bkg['variance'],
        w2method = mplhep.error_estimation.poisson_interval,
        label = 'Cumulative Background MC',
        color = 'dimgrey'
    )
    
    the_fit = expo(max_e = max_e).fit_and_plt(
        e,
        cumulative_bkg['value'],
        cumulative_bkg['variance'],
        fit_kwargs = dict(use_empty_bins = False)
    )
    
    plt.ylabel(r"$N_\text{bkgd}$ below $E_\text{ECal}$")
    plt.xlabel(r"$E_\text{ECal}$ / MeV")
    plt.yscale('log')
    # plt.ylim(ymin=1e-2) #, ymax=1e3)
    plt.xlim(0,max_e)
    plt.legend(loc='upper left')
    show(
        beam,
        filename=output / f'{beam}gev-{option}-cumulative-bkgd-fit.pdf',
        stage='Simulation Internal',
        display=False
    )
    
    ana_bins = np.array([0.0, 0.1*beam*1000, 0.2*beam*1000, cut])
    
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
    bkgd_yield[option] = {
        "sim": integrated_bkg.value.tolist(),
        "fit_val": fit_val.tolist(),
        "up": up.tolist(),
        "lo": lo.tolist()
    }
    mplhep.histplot(
        fit_val,
        bins=ana_bins,
        yerr = (up-lo)/2,
        histtype='errorbar',
        capsize=5,
        label = deduce_label(the_fit, the_fit.opt, the_fit.cov)
    )
    
    plt.legend(loc='upper left')
    plt.ylabel(r"$N_\text{bkgd}$ / bin")
    plt.xlabel(r"Analysis Bin $E_\text{ECal}$")
    plt.yscale('log')
    # plt.ylim(ymin=1)
    plt.xlim(0,cut)
    show(beam, display=False, filename=output / f'{beam}gev-{option}-integrated-bkgd-fit.pdf')


for option, by in bkgd_yield.items():
    mplhep.histplot(
        by['fit_val'],
        bins=ana_bins,
        yerr = [(up-lo)/2 for up, lo in zip(by['up'],by['lo'], strict=True)],
        histtype='errorbar',
        capsize=5,
        label=option
    )
plt.legend(loc='upper left')
plt.ylabel(r"$N_\text{bkgd}$ / bin")
plt.xlabel(r"Analysis Bin $E_\text{ECal}$")
plt.yscale('log')
# plt.ylim(ymin=1)
plt.xlim(0,cut)
show(beam, display=False, filename=output / f'{beam}gev-integrated-bkgd-fit-comp.pdf')


with open(output / 'bkgd-prediction.json','w') as f:
    json.dump(bkgd_yield, f, indent=2)


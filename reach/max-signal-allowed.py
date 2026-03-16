import pandas as pd
import numpy as np
import uproot
import argparse
from pathlib import Path
from harvester.plot import plt_msa, plt, show
from hcal_options import hcal_options

parser = argparse.ArgumentParser()
parser.add_argument('combine', help='results from combine', type=Path)
parser.add_argument('--options', nargs='+', help='hcal option short names', default=['entireback','funnel3','funnel2_withside6', 'prototype'], choices=list(hcal_options.keys()))
parser.add_argument('-o', '--output', help='directory to put output images', type=Path)
args = parser.parse_args()

if args.output is None:
    args.output = args.combine.parent

with uproot.open(args.combine) as f:
    msa = pd.DataFrame(
        f['limit'].arrays(library='np')
    ).set_index(['option', 'mh'])


all_options = list((option, hcal_options[option]) for option in args.options)+[('paper', 'Full LDMX')]

plt_msa(
    *(
        (msa.loc[option, :], label)
        for option, label in all_options
    ),
    show_kw = {
        "filename": args.output / 'max-signal-allowed-all.pdf',
        "stage": "Simulation Internal",
        "beam": 8,
        "display": False
    }
)

plt_msa(
    *((msa.loc[option,:], label) for option, label in all_options if option != "prototype"),
    show_kw = {
        "filename": args.output / 'max-signal-allowed-no-prototype.pdf',
        "stage": "Simulation Internal",
        "beam": 8,
        "display": False
    }
)

mass = msa.loc['paper',:].index.to_numpy()
ref = msa.loc['paper',:].limit.to_numpy()
ref_unc = msa.loc['paper',:].limitErr.to_numpy()
for option, label in all_options:
    if option == 'paper':
        continue

    opt_val = msa.loc[option,:].limit.to_numpy()
    opt_unc = msa.loc[option,:].limitErr.to_numpy()

    ratio = opt_val/ref
    ratio_err = np.where(
        ref != 0,
        np.sqrt(opt_unc**2/ref**2 + opt_val**2*ref_unc**2/ref**4),
        np.nan
    )
    plt.errorbar(mass, ratio, yerr=ratio_err, label=label, fmt='o')
plt.xscale('log')
plt.legend()
plt.xlabel(r"$m_{A'} /$ MeV")
plt.ylabel("Limit Ratio to Full LDMX")
show(
    display=False,
    filename = args.output / 'limit-ratio-to-full-ldmx.pdf',
    beam = 8
)

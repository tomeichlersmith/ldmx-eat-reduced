import pandas as pd
import numpy as np
import uproot
import argparse
from pathlib import Path
import matplotlib.pyplot as plt
from harvester import theory, exclusions, signal_events_to_y
from harvester.io import load_signal_yield
from harvester.plot import show
from hcal_options import hcal_options

parser = argparse.ArgumentParser()
parser.add_argument('combine', help='results from combine', type=Path)
parser.add_argument('-o', '--output', help='directory to put output images', type=Path)
parser.add_argument('--options', nargs='+', help='hcal option short names', default=['entireback','funnel3','funnel2_withside6', 'prototype'], choices=list(hcal_options.keys()))
parser.add_argument('--scale', default=1, type=float, help='scale factor background was multiplied by')
args = parser.parse_args()

if args.output is None:
    args.output = args.combine.parent

with uproot.open(args.combine) as f:
    msa = pd.DataFrame(
        f['limit'].arrays(library='np')
    ).set_index(['option', 'mh'])


all_options = list((option, hcal_options[option]) for option in args.options)+[('paper', 'Full LDMX')]
alpha_D = 0.5
mA_over_mChi = 3
masses = np.array([1,5,10,50,100,500,1000])
mchi = np.array(masses)/mA_over_mChi
signal_yield = load_signal_yield()


def limit(msa, label, band = None, plt_kwargs = {}):
    plt_kwargs.setdefault('lw',3)
    y_limit = signal_events_to_y(
        msa.limit.to_numpy(),
        signal_yield.prod_yield.to_numpy()*args.scale,
        alpha_D, mA_over_mChi
    )
    art = plt.plot(
        mchi,
        y_limit,
        label=rf'EaT; $'+('10^{13}' if args.scale == 1 else rf'{args.scale:.0f}\times 10^{13}')+'~\text{EoT}$; '+(method if label is None else label),
        **plt_kwargs
    )
    if band is not None:
        y_limit_up = signal_events_to_y(
            msa.limit.to_numpy(),
            (1-band*0.2)*pass_rate_per_eps2[b].prod_rate*1e13*args.scale,
            alpha_D, mA_over_mChi
        )
        y_limit_dn = signal_events_to_y(
            msa.limit.to_numpy(),
            (1+band*0.2)*pass_rate_per_eps2[b].prod_rate*1e13*args.scale,
            alpha_D, mA_over_mChi
        )
        plt.gca().fill_between(
            mchi, y_limit_dn, y2 = y_limit_up,
            color = art[0].get_color(),
            alpha = 0.5
        )


def reach_plt(
    *limit_args,
    old_limits = [],
    include_mm = 8,
    **show_kw
):
    plt.figure(figsize=(100/8,8))
    theory.draw(plt.gca(), color='black')
    exclusions.draw(plt.gca(), color='lightgray')
    for la in limit_args:
        limit(*la)
    if include_mm:
        if isinstance(include_mm, bool):
            # default to both as dashed lines
            plt.plot(
                *exclusions.LDMX_Std_Whitepaper(),
                label=r'Nominal MM; $4\times10^{14}~\text{EoT}$; 4 GeV',
                color='tab:blue',
                ls='--',
                lw=3
            )
            plt.plot(
                *exclusions.LDMX_MM_8GeV(),
                label=r'Nominal MM; $4\times10^{14}~\text{EoT}$; 8 GeV',
                color='tab:orange',
                ls='--',
                lw=3
            )
        elif isinstance(include_mm, (float,int)):
            if int(include_mm) == 4:
                plt.plot(
                    *exclusions.LDMX_Std_Whitepaper(),
                    label=r'Nominal MM; $4\times10^{14}~\text{EoT}$; 4 GeV',
                    color='gray',
                    ls='--',
                    lw=3
                )
            elif int(include_mm) == 8:
                plt.plot(
                    *exclusions.LDMX_MM_8GeV(),
                    label=r'Nominal MM; $4\times10^{14}~\text{EoT}$; 8 GeV',
                    color='gray',
                    ls='--',
                    lw=3
                )
            else:
               raise ValueError(f"Unrecognized beam energy {include_mm}")
        else:
           raise ValueError(f"Unrecognized beam energy {include_mm}")

    plt.yscale('log')
    plt.xscale('log')
    plt.ylim(ymax=1e-7)
    plt.xlim(1,1e3)
    plt.xlabel(r"$m_\chi$ [MeV]")
    plt.ylabel(r"$y = \alpha_D \epsilon^2 (m_\chi/m_{A'})^4$")
    plt.legend(
        loc='upper left',
        bbox_to_anchor= (1,1),
        title=r"$\alpha_D = "+str(alpha_D)+r"\quad m_{A'} = "+str(mA_over_mChi)+r"m_\chi$"
    )
    show_kw.setdefault('stage','Simulation Internal')
    show_kw.setdefault('display', False)
    show(**show_kw)


reach_plt(
    *((msa.loc[option,:], label) for option, label in all_options),
    beam = 8,
    lumi = None,
    filename = args.output / '8gev-reach-all.pdf'
)
